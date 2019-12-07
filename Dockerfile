FROM python:3.5
COPY . /eva
WORKDIR /eva
RUN apt-get update
RUN apt-get install libsndfile1 -y
RUN pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]
