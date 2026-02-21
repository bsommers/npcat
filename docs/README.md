# NetCap Analysis Documentation

Welcome to the NetCap Analysis Tool documentation.

## Contents

- [Installation](installation.md) - How to install and set up
- [Architecture](architecture.md) - System design and components
- [CLI Reference](cli.md) - Command-line interface documentation
- [Examples](examples.md) - Real-world usage examples
- [Reports](reports.md) - Report format and output details

## Quick Start

```bash
# Analyze a capture file
netcapanalysis analyze -i capture.pcap -o report.md

# Multi-capture timeline analysis
netcapanalysis timeline -i capture1.pcap -i capture2.pcap -o timeline.md
```

## Features

- Packet capture using scapy or tshark
- Single and multi-capture analysis
- Packet length distribution charts
- Destination port analysis
- Conversation timeline with UML diagrams
- Metrics: turns, chattiness, average packet size
- Markdown reports with embedded mermaid diagrams
- PNG chart export
