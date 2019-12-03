import torch
import torch.nn.functional as F
from torch.autograd import Variable
import scipy.io.wavfile as wav
import librosa

import pandas as pd
import numpy as np
import math
import os
import ml_engine.configure as c

from ml_engine.DB_wav_reader import read_feats_structure, read_audio
from ml_engine.SR_Dataset import read_MFB, ToTensorTestInput
from ml_engine.model.model import background_resnet
from ml_engine.python_speech_features.base import fbank

log_dir = 'ml_engine/model_saved' # Where the checkpoints are saved
embedding_dir = 'ml_engine/enroll_embeddings' # Where embeddings are saved
test_dir = 'ml_engine/feat_logfbank_nfilt40/test/' # Where test features are saved
    
# Settings
use_cuda = False # Use cuda or not
embedding_size = 128 # Dimension of speaker embeddings
cp_num = 24 # Which checkpoint to use?
n_classes = 240 # How many speakers in training data?
test_frames = 100 # Split the test utterance 

def wav_to_logfbank(filename):
    audio = read_audio(filename, c.SAMPLE_RATE)
    filter_banks, energies = fbank(audio, samplerate = c.SAMPLE_RATE, nfilt=c.FILTER_BANK, winlen=0.025)

    if c.USE_LOGSCALE:
        filter_banks = 20 * np.log10(np.maximum(filter_banks, 1e-5))

    filter_banks = normalize_frames(filter_banks, Scale=c.USE_SCALE)

    return filter_banks

def normalize_frames(m, Scale=True):
    if Scale:
        return (m - np.mean(m, axis=0)) / (np.std(m, axis=0) + 2e-12)
    else:
        return (m - np.mean(m, axis=0))

def load_model(use_cuda, log_dir, cp_num, embedding_size, n_classes):
    model = background_resnet(embedding_size=embedding_size, num_classes=n_classes)
    if use_cuda:
        model.cuda()
    print('[ML_ENGINE]=> loading checkpoint')
    # original saved file with DataParallel
    checkpoint = torch.load(log_dir + '/checkpoint_' + str(cp_num) + '_cpu.pth')
    # create new OrderedDict that does not contain `module.`
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    return model

def split_enroll_and_test(dataroot_dir):
    DB_all = read_feats_structure(dataroot_dir)
    enroll_DB = pd.DataFrame()
    test_DB = pd.DataFrame()
    
    enroll_DB = DB_all[DB_all['filename'].str.contains('enroll.p')]
    test_DB = DB_all[DB_all['filename'].str.contains('test.p')]
    
    # Reset the index
    enroll_DB = enroll_DB.reset_index(drop=True)
    test_DB = test_DB.reset_index(drop=True)
    return enroll_DB, test_DB

def get_embeddings(use_cuda, filename, model, test_frames):
    #input, label = read_MFB(filename) # input size:(n_frames, n_dims)
    input = wav_to_logfbank(filename)

    tot_segments = math.ceil(len(input)/test_frames) # total number of segments with 'test_frames' 
    activation = 0
    with torch.no_grad():
        for i in range(tot_segments):
            temp_input = input[i*test_frames:i*test_frames+test_frames]
            
            TT = ToTensorTestInput()
            temp_input = TT(temp_input) # size:(1, 1, n_dims, n_frames)
    
            if use_cuda:
                temp_input = temp_input.cuda()
            temp_activation,_ = model(temp_input)
            activation += torch.sum(temp_activation, dim=0, keepdim=True)
    
    activation = l2_norm(activation, 1)
                
    return activation

def l2_norm(input, alpha):
    input_size = input.size()  # size:(n_frames, dim)
    buffer = torch.pow(input, 2)  # 2 denotes a squared operation. size:(n_frames, dim)
    normp = torch.sum(buffer, 1).add_(1e-10)  # size:(n_frames)
    norm = torch.sqrt(normp)  # size:(n_frames)
    _output = torch.div(input, norm.view(-1, 1).expand_as(input))
    output = _output.view(input_size)
    # Multiply by alpha = 10 as suggested in https://arxiv.org/pdf/1703.09507.pdf
    output = output * alpha
    return output

def enroll_per_spk(use_cuda, test_frames, model, DB, embedding_dir):
    """
    Output the averaged d-vector for each speaker (enrollment)
    Return the dictionary (length of n_spk)
    """
    n_files = len(DB) # 10
    enroll_speaker_list = sorted(set(DB['speaker_id']))
    
    embeddings = {}
    
    # Aggregates all the activations
    print("[ML_ENGINE]Start to aggregate all the d-vectors per enroll speaker")
    
    for i in range(n_files):
        filename = DB['filename'][i]
        spk = DB['speaker_id'][i]
        
        activation = get_embeddings(use_cuda, filename, model, test_frames)
        if spk in embeddings:
            embeddings[spk] += activation
        else:
            embeddings[spk] = activation
            
        print("[ML_ENGINE]Aggregates the activation (spk : %s)" % (spk))
        
    if not os.path.exists(embedding_dir):
        os.makedirs(embedding_dir)
        
    # Save the embeddings
    for spk_index in enroll_speaker_list:
        embedding_path = os.path.join(embedding_dir, spk_index+'.pth')
        torch.save(embeddings[spk_index], embedding_path)
        print("[ML_ENGINE]Save the embeddings for %s" % (spk_index))
    return embeddings

def load_enroll_embeddings(embedding_dir):
    embeddings = {}
    for f in os.listdir(embedding_dir):
        spk = f.replace('.pth','')
        # Select the speakers who are in the 'enroll_spk_list'
        embedding_path = os.path.join(embedding_dir, f)
        tmp_embeddings = torch.load(embedding_path)
        embeddings[spk] = tmp_embeddings
        
    return embeddings

def perform_identification(use_cuda, model, embeddings, test_filename, test_frames, spk_list):
    test_embedding = get_embeddings(use_cuda, test_filename, model, test_frames)
    max_score = -10**8
    best_spk = None
    for spk in spk_list:
        score = F.cosine_similarity(test_embedding, embeddings[spk])
        score = score.data.cpu().numpy() 
        if score > max_score:
            max_score = score
            best_spk = spk
    #print("Speaker identification result : %s" %best_spk)
    true_spk = '230M4087'
    print("\n[ML_ENGINE]=== Speaker identification ===")
    print("[ML_ENGINE]Predicted speaker : %s\n" %(best_spk))
    return best_spk

def perform_verification(use_cuda, model, embeddings, enroll_speaker, test_filename, test_frames, thres):
    enroll_embedding = embeddings[enroll_speaker]
    test_embedding = get_embeddings(use_cuda, test_filename, model, test_frames)

    score = F.cosine_similarity(test_embedding, enroll_embedding)
    score = score.data.cpu().numpy()


    print("\n[ML_ENGINE]=== Speaker verification ===")
    print("[ML_ENGINE]Score : %0.4f\n[ML_ENGINE]Threshold : %0.2f\n" %(score, thres))

    if score > thres:
        print ('[ML_ENGINE]true')
        return True

    print('[ML_ENGINE]false')
    return False

#init engine
model = load_model(use_cuda, log_dir, cp_num, embedding_size, n_classes)
enroll_DB, test_DB = split_enroll_and_test(c.TEST_FEAT_DIR)
embeddings = load_enroll_embeddings(embedding_dir)
spk_list = ['103F3021', '207F2088', '213F5100', '217F3038', '225M4062', '229M2031', '230M4087', '233F4013', '236M3043', '240M3063']
thres = 0.95

'''
IN 
    - file_path : path of the audio data in .wav format
    - speaker_id: ID to be associated with the given audio file.

RETURNS 
    - NONE
'''
def enroll_speaker(file_path, id):
    # Where to save embeddings
    embedding_dir = 'ml_engine/enroll_embeddings'
    
    # Perform the enrollment and save the results
    enroll_per_spk(use_cuda, test_frames, model, enroll_DB, embedding_dir)


'''
IN 
    - file_path : path of the audio data in .wav format
    - speaker_id: speaker id to be verified.

RETURNS 
    - verification result in True or False.
'''
def verify_speaker(file_path, speaker_id):
    # Set SPEAKER_ID for test (dummy)
    speaker_id = '230M4087'

    # Perform the test 
    return perform_verification(use_cuda, model, embeddings, speaker_id, file_path, test_frames, thres)

'''
IN 
    - file_path: path of the audio data in .wav format

RETURNS 
    - ID of predicted speaker
'''
def identify_speaker(file_path):
    # Perform the test 
    return perform_identification(use_cuda, model, embeddings, file_path, test_frames, spk_list)

def main():
    print('[ML_ENGINE]Hello from ml_engine!')

if __name__ == '__main__':
    main()
