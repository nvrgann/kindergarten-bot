FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget unzip gnupg2 curl     && apt-get install -y chromium-driver chromium

ENV CHROME_BIN=/usr/bin/chromium
ENV PATH=$PATH:/usr/lib/chromium/

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]