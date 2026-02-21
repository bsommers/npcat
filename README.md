# NetCap Analysis Tool

Network packet capture and analysis tool with visualization and reporting.

## Features

- **Packet Capture**: Live capture using scapy or tshark
- **Single File Analysis**: Protocol distribution, port analysis, conversation tracking
- **Multi-Capture Timeline**: Analyze multiple captures with timeline view
- **Metrics**: Turns (direction changes), chattiness, average packet size
- **Visualization**: PNG bar charts, mermaid sequence/timeline diagrams
- **Reports**: Markdown with embedded mermaid diagrams

## Quick Start

```bash
# Using Docker (recommended)
docker build -t netcapanalysis:latest .

# Or local installation
uv venv .venv && source .venv/bin/activate
pip install --break-system-packages -e .

# Capture packets
sudo netcapanalysis capture -c 100 -o capture.pcap

# Analyze
netcapanalysis analyze -i capture.pcap -o report.md

# Multi-capture timeline
netcapanalysis timeline -i capture1.pcap -i capture2.pcap -o timeline.md
```

## Commands

| Command | Description |
|---------|-------------|
| `capture` | Capture live packets to pcap |
| `analyze` | Analyze single pcap file |
| `chart` | Generate specific chart |
| `mermaid` | Export mermaid diagram |
| `timeline` | Multi-capture timeline analysis |

## Documentation

See the [docs/](docs/) folder for detailed documentation:

- [docs/README.md](docs/README.md) - Documentation index
- [docs/architecture.md](docs/architecture.md) - System architecture
- [docs/cli.md](docs/cli.md) - CLI reference
- [docs/examples.md](docs/examples.md) - Usage examples
- [docs/reports.md](docs/reports.md) - Report formats

## Docker

```bash
# Build
docker build -t netcapanalysis:latest .

# Run
docker run --rm -it --privileged -v $(pwd):/data netcapanalysis capture -c 100 -o /data/capture.pcap
docker run --rm -it -v $(pwd):/data netcapanalysis analyze -i /data/capture.pcap -o /data/report.md
```

## Requirements

- Python 3.8+
- scapy, matplotlib, click
- tshark (optional, for enhanced capture)
- nodejs + npx (optional, for mermaid PNG export)

## License

MIT
