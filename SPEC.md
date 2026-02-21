# NetCap Analysis Tool - Specification

## Project Overview
- **Project Name**: netcapanalysis
- **Type**: Python CLI tool for network packet capture and analysis
- **Core Functionality**: Capture network packets, analyze traffic patterns, visualize data with graphs and UML diagrams, generate markdown reports
- **Target Users**: Network administrators, security analysts, developers debugging network issues

## Functionality Specification

### Core Features

1. **Packet Capture**
   - Live capture using tshark (Wireshark command-line)
   - Read from existing pcap/pcapng files
   - Filter by BPF filter expression
   - Limit capture count and duration

2. **Packet Length Analysis**
   - Calculate min/max/avg packet lengths
   - Display bar graph of packet length distribution
   - Group by protocol (TCP, UDP, ICMP, etc.)

3. **Destination Port Analysis**
   - Bar chart showing top destination ports
   - Count packets per port
   - Show well-known port service names

4. **Conversation Pairs**
   - Track src IP <-> dst IP conversations
   - Track src port <-> dst port pairs for TCP/UDP
   - Generate UML sequence diagram (mermaid format)
   - Show packet count and bytes per conversation

5. **Report Generation**
   - Generate comprehensive markdown report
   - Include all charts as embedded mermaid diagrams
   - Summary statistics section

6. **Chart Generation**
   - Generate mermaid charts (bar charts, sequence diagrams)
   - Export mermaid to PNG using mermaid-cli
   - Support both inline mermaid in markdown and standalone PNG files

### CLI Interface

```
netcapanalysis capture --interface eth0 --count 100 --output capture.pcap
netcapanalysis analyze --input capture.pcap --output report.md
netcapanalysis chart --input capture.pcat --type length --output length.png
netcapanalysis conversation --input capture.pcap --output conv.png
```

### Data Structures

1. **PacketInfo**: timestamp, src_ip, dst_ip, src_port, dst_port, protocol, length
2. **Conversation**: src, dst, packet_count, total_bytes, packets[]
3. **PortStats**: port, protocol, count, service_name

### Edge Cases
- Empty pcap files
- Non-IP packets (ARP, etc.)
- Fragmented packets
- Very large captures (memory management)

## Acceptance Criteria

1. CLI successfully captures packets from interface or reads pcap file
2. Bar graph displays packet length distribution correctly
3. Bar graph displays destination port distribution
4. UML sequence diagram shows conversation pairs accurately
5. Markdown report includes all statistics and mermaid diagrams
6. PNG generation produces valid image files
7. Works with standard pcap/pcapng files
