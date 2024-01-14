FROM python:3.9

WORKDIR /usr/src/app

RUN pip install dropbox stegano psutil
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx


RUN mkdir bot utils

COPY ./bot ./bot
COPY ./utils ./utils

ENV BOT_ID=0
ENV DROPBOX_TOKEN='SAMPLE_TOKEN'
ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"

RUN chmod +x bot/hello.sh

CMD python bot/bot.py $BOT_ID $DROPBOX_TOKEN
