FROM python:3.5
MAINTAINER ina-uzu "ina.uzu.song@gmail.com"
#RUN apt-get update -y
#RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]
