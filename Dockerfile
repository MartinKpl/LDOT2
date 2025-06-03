FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Workaround for package archive issues (if you still get 404s, see below)
RUN apt-get update --allow-releaseinfo-change --fix-missing

RUN apt-get update && apt-get install -y --fix-missing \
    python3 python3-pip python3-dev \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    git \
    xvfb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN git clone https://github.com/MartinKpl/LDOT2.git

COPY . .

CMD ["/bin/bash"]