# Examples

## Basic Analysis

### Analyze a Single Capture

```bash
# Capture some traffic
sudo netcapanalysis capture -c 100 -o capture.pcap

# Analyze the capture
netcapanalysis analyze -i capture.pcap -o report.md
```

### Analyze Existing PCAP

```bash
# If you have a pcap from Wireshark
netcapanalysis analyze -i /path/to/capture.pcap -o report.md
```

---

## Multi-Capture Timeline

### Compare Traffic Over Time

```bash
# Capture at different times
sudo netcapanalysis capture -c 100 -o capture_morning.pcap
sudo netcapanalysis capture -c 100 -o capture_afternoon.pcap
sudo netcapanalysis capture -c 100 -o capture_evening.pcap

# Analyze timeline
netcapanalysis timeline \
  -i capture_morning.pcap \
  -i capture_afternoon.pcap \
  -i capture_evening.pcap \
  -o timeline.md
```

### Analyze Multiple PCAP Files

```bash
# From a directory of captures
netcapanalysis timeline -i *.pcap -o all_captures.md
```

---

## Docker Usage

### Basic Docker Commands

```bash
# Build image
docker build -t netcapanalysis:latest .

# Capture packets (requires --privileged)
docker run --rm -it --privileged \
  -v $(pwd)/data:/data \
  netcapanalysis capture -c 100 -o /data/capture.pcap

# Analyze
docker run --rm -it \
  -v $(pwd)/data:/data \
  netcapanalysis analyze -i /data/capture.pcap -o /data/report.md

# Timeline
docker run --rm -it \
  -v $(pwd)/data:/data \
  netcapanalysis timeline \
    -i /data/capture1.pcap \
    -i /data/capture2.pcap \
    -o /data/timeline.md
```

### Docker Compose

```yaml
version: '3.8'
services:
  netcapanalysis:
    build: .
    image: netcapanalysis:latest
    volumes:
      - ./data:/data
    privileged: true
```

```bash
docker compose run --rm netcapanalysis capture -c 100 -o /data/capture.pcap
```

---

## Filter Examples

### Capture Only HTTP Traffic

```bash
sudo netcapanalysis capture -i eth0 -f "tcp port 80" -c 100 -o http.pcap
```

### Capture Only HTTPS Traffic

```bash
sudo netcapanalysis capture -i eth0 -f "tcp port 443" -c 100 -o https.pcap
```

### Capture DNS Queries

```bash
sudo netcapanalysis capture -i eth0 -f "udp port 53" -c 50 -o dns.pcap
```

### Capture From Specific Host

```bash
sudo netcapanalysis capture -i eth0 -f "host 192.168.1.100" -c 100 -o host.pcap
```

---

## Generate Specific Charts

### Packet Length Distribution

```bash
netcapanalysis chart -i capture.pcap -o length.png -t length
```

### Port Distribution

```bash
netcapanalysis chart -i capture.pcap -o port.png -t port
```

### Conversation Diagram

```bash
netcapanalysis chart -i capture.pcap -o conv.png -t conversation
```

---

## Extract Mermaid Diagrams

### For Documentation

```bash
netcapanalysis mermaid -i capture.pcap -o diagram.mmd
```

The mermaid file can be used in:
- Markdown files with mermaid preview
- Mermaid Live Editor
- GitHub/GitLab markdown (native support)

---

## Real-World Scenarios

### Monitor Web Server Traffic

```bash
# Capture web traffic
sudo netcapanalysis capture -i eth0 -f "tcp port 80 or tcp port 443" -c 500 -o web.pcap

# Analyze
netcapanalysis analyze -i web.pcap -o web_report.md
```

### Investigate Network Issue

```bash
# Capture during issue
sudo netcapanalysis capture -i eth0 -d 60 -o issue.pcap

# Analyze
netcapanalysis analyze -i issue.pcap -o issue_report.md
```

### Compare Before/After Changes

```bash
# Before
sudo netcapanalysis capture -c 200 -o before.pcap

# Make changes to system...

# After
sudo netcapanalysis capture -c 200 -o after.pcap

# Compare
netcapanalysis timeline -i before.pcap -i after.pcap -o comparison.md
```
