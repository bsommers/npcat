# Architecture

## Overview

NetCap Analysis is a Python-based network packet capture and analysis tool that provides visualization and reporting capabilities for pcap files.

## Components

```
netcapanalysis/
├── cli.py           # Command-line interface (Click)
├── capture.py       # Packet capture (scapy/tshark)
├── analyzer.py      # Single pcap analysis
├── multianalyze.py  # Multi-capture timeline analysis
├── charts.py        # Chart generation (matplotlib/mermaid)
├── report.py        # Markdown report generation
└── __init__.py      # Package initialization
```

## Data Flow

### Single File Analysis

```
pcap file → analyzer.py → stats dict → charts.py → PNG/mermaid
                              ↓
                         report.py → Markdown report
```

### Multi-Capture Timeline Analysis

```
pcap files → multianalyze.py → timeline list → charts.py → PNG/mermaid
                                            ↓
                                       Markdown report
```

## Key Modules

### cli.py
- Uses Click framework for CLI
- Commands: capture, analyze, chart, mermaid, timeline

### capture.py
- Primary: scapy (no root required with proper capabilities)
- Fallback: tshark (requires root)
- Auto-selects available interface

### analyzer.py
- Parses pcap files using scapy
- Extracts: protocols, ports, conversations, packet lengths
- Returns statistics dictionary

### multianalyze.py
- Analyzes multiple pcap files in sequence
- Tracks packet indices across captures for timeline ordering
- Calculates conversation metrics:
  - **Turns**: Direction changes (bidirectional = more turns)
  - **Chattiness**: Packets per packet interval
  - **Avg Packet Size**: Total bytes / packet count

### charts.py
- matplotlib for PNG bar charts
- mermaid generation for sequence/timeline diagrams
- mermaid_to_png() for PNG export via npx

### report.py
- Generates markdown with embedded mermaid
- Creates PNG charts alongside report

## Docker Architecture

```
python:3.12-slim
├── tshark, tcpdump (packet capture)
├── nodejs (mermaid-cli for PNG)
├── click, scapy, matplotlib (Python deps)
└── appuser (non-root user)
```

### Non-root Capture

Dockerfile configures:
- dumpcap with capabilities: CAP_NET_RAW, CAP_NET_ADMIN
- User added to wireshark group
- Allows packet capture without running container as root
