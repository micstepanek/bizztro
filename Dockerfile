FROM python:3.10
WORKDIR /usr/bizztro/src
COPY main.py data_checker.py requirements.txt ./
RUN pip3.10 install -r requirements.txt
ENTRYPOINT ["python3.10h", "./main.py"]