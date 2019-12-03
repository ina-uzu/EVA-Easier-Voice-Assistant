# -*- coding:utf-8 -*-
import json

import requests
import chardet

# url = "http://15.164.50.174:5000/"
url = "http://163.239.28.22:5000/"


def get_final_cmd(stt, voice):
    params = {"stt": stt, "voice": voice}

    try:
        response = requests.post(url + "cmd", params=params)

        print("url : ", url + "cmd")
        print("params : ", params)
        print("status code :", response.status_code)
        return response.text

    except Exception as e:
        print("ERROR! ", str(e))


def send_stt(stt):
    params = {"stt": stt}
    try:
        response = requests.post(url + "stt/", params=params)

        print("url : ", url + "stt")
        print("params : ", params)
        print("status code :", response.status_code)

    except Exception as e:
        print("ERROR! ", str(e))


def main():
    stt = input("stt: ")

    try:
        '''
        resp = get_final_cmd(stt, "TEST")
        cmd = json.loads(resp)

        if "command" in cmd:
            cmd = cmd["command"]
            print(cmd)
        '''
        send_stt(stt)
        
    except Exception as e:
        print("ERROR! ", str(e))


if __name__ == "__main__":
    main()
