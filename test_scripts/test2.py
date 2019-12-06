# -*- coding:utf-8 -*-
import json
import array
import requests

url = "http://54.180.120.132:5000/"
#url = "http://127.0.0.1:5000/"


def test():

    byte_array = array.array('B')
    audio_file = open("../data/sample_sound.wav", 'rb')
    byte_array.frombytes(audio_file.read())
    body = byte_array.tobytes()
    stt = '카스'

    try:

        stt_data = stt.encode() + b'!'
        body = stt_data + body
        response = requests.post(url + "cmd", data=body, headers={'Content-Type': 'application/octet-stream'})

        print("url : ", url + "cmd")
        print("file len : ", len(body))
        print("status code :", response.status_code)
        return response.text

    except Exception as e:
        print("ERROR! ", str(e))


def main():
    resp = test()
    cmd = json.loads(resp)
    print(cmd)


if __name__ == "__main__":
    main()
