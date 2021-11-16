FROM ubuntu:latest
WORKDIR /usr/fagtoy/Desktop/self/bgram
RUN apt-get update && apt-get install -y curl
ENTRYPOINT ["curl", "-s"]