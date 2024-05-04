FROM python:3.11

RUN apt-get update || apt-get upgrade

RUN mkdir /wasdwork

WORKDIR /wasdwork

COPY ./core ./core
COPY ./bot.py ./bot.py
COPY ./requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
