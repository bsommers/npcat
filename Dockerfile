FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    tshark \
    tcpdump \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 wireshark || true \
    && usermod -aG wireshark root || true \
    && chmod 750 /usr/bin/dumpcap \
    && setcap 'CAP_NET_RAW+eip CAP_NET_ADMIN+eip' /usr/bin/dumpcap \
    || chmod +s /usr/bin/dumpcap

RUN pip install --no-cache-dir click scapy matplotlib

RUN useradd -m -u 1000 appuser \
    && groupadd -g 1000 wireshark || true \
    && usermod -aG wireshark appuser

WORKDIR /app

COPY --chown=appuser:appuser . /app

RUN pip install --no-cache-dir -e .

USER appuser

ENTRYPOINT ["netcapanalysis"]
CMD ["--help"]
