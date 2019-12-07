<p align="center">
  <a href="http://cscp2.sogang.ac.kr/CSE4187/index.php/EVA(Easier_Voice_Assistant)">
    <img title="Logo" src="img/logo.png" width=500>
  </a>
</p>

<p align="center">
    <a href="https://www.python.org/downloads/release/python-350/">
        <img src="https://img.shields.io/badge/python-v3.5-blue.svg?logo=python&logoColor=white">
    </a>
    <a href="http://flask.palletsprojects.com/en/1.1.x/">
        <img src="https://img.shields.io/badge/flask-v1.1.1-blue.svg?logo=flask&logoColor=white">
    </a>
    <a href="https://pytorch.org/">
        <img src="https://img.shields.io/badge/pytorch-v1.3.1-blue.svg?logo=pytorch&logoColor=white">
    </a>
    <a href="https://www.docker.com/">
        <img src="https://img.shields.io/badge/Install with-docker-blue.svg?logo=docker&logoColor=white">
    </a>
    <a href="https://github.com/ina-uzu/EVA-Easier-Voice-Assistant/issues">
        <img src="https://img.shields.io/github/issues/ina-uzu/EVA-Easier-Voice-Assistant?logo=github">
    </a>
</p>


## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Showcase](#showcase)
- [Feedback](#feedback)
- [Contribution](#contribution)
- [Build with](#build-with)
- [Build Process](#build-process)
- [Authors](#authors)
- [License](#license)


## Introduction
<span style="font-size:1.2em;">EVA is a speaker recognition and voice shortcut system.</span>


## Features

- Users can register various functions with their own shortcut keys and enjoy them faster and easier.
- By distinguishing the speaker based on the voice, the same voice input performs different functions for each user.


## Showcase

<p align="center">
  <img src = "img/motivation.png" width=700>
</p>

<p align="center">
  <img src = "img/diagram.png" width=700>
</p>


## Feedback

Please feel free to give us any feedback or feature requests by [opening an issue](https://github.com/ina-uzu/eva/issues).


## Contribution

If you wish to contribute to our project, please please do not hesitate to [contact us](https://github.com/ina-uzu/eva/issues).


## Build with
- [Python3](https://www.python.org/) - Python is an interpreted, high-level, general-purpose programming language.
- [Flask](http://flask.palletsprojects.com/) - Flask provides you with tools, libraries and technologies that allow you to build a web application.
- [Pytorch](https://pytorch.org/) - An open source machine learning framework that accelerates the path from research prototyping to production deployment.


## Build Process
**Docker is required if you wish to develop by yourself.**  

http://54.180.120.132:5000/  

// docker container 목록 보기  
docker ps  ( -a : 실행 중인 것만 보기 옵션)  

// docker image & container 새로 생성 및 run  
docker stop $(docker ps -a -q)  
docker rm $(docker ps -a -q)  
docker rmi  
docker build -t eva .  
docker run -d -p 5000:5000 --name eva eva  


## Authors

* **Min Woo Kim** - *ML engineer* - [JoeyValentine](https://github.com/JoeyValentine)
* **Kyu Yeon Lee** - *ML engineer* - [Destructions](https://github.com/destructions)
* **Ina Song** *Server engineer* - [ina-uzu](https://github.com/ina-uzu)
* **Joohan Lee** *Server engineer* - [joohan1030](https://github.com/joohan1030)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

