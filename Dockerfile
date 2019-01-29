FROM nginx

RUN apt update && \
    apt install -y certbot wget && \
    wget https://github.com/bcicen/tinycron/releases/download/v0.4/tinycron-0.4-linux-amd64 && \
    chmod +x tinycron-0.4-linux-amd64 && \
    mv tinycron-0.4-linux-amd64 /usr/bin/tinycron

COPY start.py /
COPY certbotrenew.sh /

COPY conftemplates/ /conftemplates

RUN chmod +x start.py

ENV  PYTHONUNBUFFERED=1
CMD ["/start.py"]
