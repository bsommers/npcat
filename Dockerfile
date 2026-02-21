FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    tshark \
    tcpdump \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir click scapy matplotlib

RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY --chown=appuser:appuser . /app

RUN pip install --no-cache-dir -e .

USER appuser

ENTRYPOINT ["netcapanalysis"]
CMD ["--help"]
