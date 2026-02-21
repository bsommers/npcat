# CLI Reference

## Commands

### capture

Capture live network packets to a pcap file.

```bash
netcapanalysis capture [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-i, --interface TEXT` | Network interface (auto-detected if not specified) |
| `-c, --count INTEGER` | Number of packets to capture (default: 100) |
| `-o, --output PATH` | Output pcap file (required) |
| `-f, --filter TEXT` | BPF filter expression (e.g., "tcp port 80") |
| `-d, --duration INTEGER` | Capture duration in seconds |

**Examples:**

```bash
# Capture 100 packets
netcapanalysis capture -c 100 -o capture.pcap

# Capture on specific interface
sudo netcapanalysis capture -i eth0 -c 500 -o capture.pcap

# Capture with filter
sudo netcapanalysis capture -i eth0 -f "tcp and port 443" -c 100 -o tls.pcap

# Capture for 30 seconds
sudo netcapanalysis capture -i eth0 -d 30 -o capture.pcap
```

---

### analyze

Analyze a pcap file and generate a markdown report.

```bash
netcapanalysis analyze [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-i, --input PATH` | Input pcap file (required) |
| `-o, --output PATH` | Output markdown file (default: report.md) |
| `--no-png` | Skip PNG chart generation |

**Examples:**

```bash
# Basic analysis
netcapanalysis analyze -i capture.pcap -o report.md

# Analysis without PNG
netcapanalysis analyze -i capture.pcap -o report.md --no-png
```

---

### chart

Generate a specific chart from a pcap file.

```bash
netcapanalysis chart [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-i, --input PATH` | Input pcap file (required) |
| `-o, --output PATH` | Output chart file (required) |
| `-t, --type [length\|port\|conversation]` | Chart type (default: port) |

**Examples:**

```bash
# Packet length distribution
netcapanalysis chart -i capture.pcap -o length.png -t length

# Top destination ports
netcapanalysis chart -i capture.pcap -o port.png -t port

# Conversation diagram
netcapanalysis chart -i capture.pcap -o conv.png -t conversation
```

---

### mermaid

Generate mermaid diagrams from a pcap file.

```bash
netcapanalysis mermaid [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-i, --input PATH` | Input pcap file (required) |
| `-o, --output PATH` | Output mermaid file (required) |

**Examples:**

```bash
netcapanalysis mermaid -i capture.pcap -o diagram.mmd
```

---

### timeline

Analyze multiple pcap files and show conversation timeline.

```bash
netcapanalysis timeline [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-i, --inputs PATH` | Input pcap files (required, can specify multiple) |
| `-o, --output PATH` | Output markdown file (default: timeline.md) |
| `--no-png` | Skip PNG chart generation |

**Examples:**

```bash
# Timeline from multiple captures
netcapanalysis timeline -i capture1.pcap -i capture2.pcap -i capture3.pcap -o timeline.md

# Timeline without PNG
netcapanalysis timeline -i *.pcap -o analysis.md --no-png
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show version |
| `--help` | Show help |
