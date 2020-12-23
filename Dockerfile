FROM python:alpine

WORKDIR /app

RUN apk add --no-cache ffmpeg curl tzdata && \
    pip install requests && \
    curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl && \
    chmod a+rx /usr/local/bin/youtube-dl && \
    curl https://codeload.github.com/oliverjrose99/Recordurbate/zip/master --output master.zip && \
    unzip master.zip ; mv Recordurbate-master/recordurbate/* .; rm -r Recordurbate-master && \
    rm master.zip && \
    apk del curl

ADD server.py docker-init.sh ./
RUN mv configs configs_init

# to store videos
VOLUME /app/videos
# To store streamers list ; should be good this data
# to be seperated to the real config
VOLUME /app/configs

CMD ./docker-init.sh
