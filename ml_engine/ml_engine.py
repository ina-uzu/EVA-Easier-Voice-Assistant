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

def get_embeddings(use_cuda, filename, model, test_frames):
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

def load_enroll_embeddings(embedding_dir):
    embeddings = {}

    for f in os.listdir(embedding_dir):
        if f[0] == '.':
            continue
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
embeddings = load_enroll_embeddings(embedding_dir)
spk_list = [*embeddings]
thres = 0.95

'''
IN 
    - file_path : path of the audio data in .wav format
    - speaker_id: ID to be associated with the given audio file.

RETURNS 
    - NONE
'''
def enroll_speaker(file_path, speaker_id):
    # Get activation, which is used as embedding
    activation = get_embeddings(use_cuda, file_path, model, test_frames)

    if not os.path.exists(embedding_dir):
        os.makedirs(embedding_dir)

    print("[ML_ENGINE]Saving embeddings of speaker ", speaker_id)
    embedding_path = os.path.join(embedding_dir, speaker_id+'.pth')
    torch.save(speaker_id, embedding_path)

    embeddings[speaker_id] = activation

'''
IN 
    - file_path: path of the audio data in .wav format

RETURNS 
    - ID of predicted speaker
'''
def identify_speaker(file_path):
    # Perform the test 
    return perform_identification(use_cuda, model, embeddings, file_path, test_frames, spk_list)

'''
IN 
    - file_path : path of the audio data in .wav format
    - speaker_id: speaker id to be verified.

RETURNS 
    - verification result in True or False.
'''
def verify_speaker(file_path, speaker_id):
    # Set SPEAKER_ID for test (dummy)

    # Perform the test 
    return perform_verification(use_cuda, model, embeddings, speaker_id, file_path, test_frames, thres)

def main():
    print('[ML_ENGINE]Hello from ml_engine!')

if __name__ == '__main__':
    main()
