import sys
from collections import defaultdict
from pathlib import Path

from scapy.all import rdpcap, IP, TCP, UDP, ICMP


PORT_SERVICES = {
    20: "FTP-DATA",
    21: "FTP",
    22: "SSH",
    23: "TELNET",
    25: "SMTP",
    53: "DNS",
    67: "DHCP",
    68: "DHCP",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    465: "SMTPS",
    587: "SMTP",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-ALT",
    8443: "HTTPS-ALT",
    27017: "MongoDB",
}


def get_service_name(port):
    return PORT_SERVICES.get(port, "Unknown")


def analyze_pcap_timeline(pcap_file, base_idx=0):
    """Analyze pcap file with timeline data"""
    conversations = []

    try:
        packets = rdpcap(str(pcap_file))
    except Exception as e:
        print(f"Error opening pcap file: {e}", file=sys.stderr)
        sys.exit(1)

    packet_idx = base_idx
    for packet in packets:
        if IP not in packet:
            continue

        packet_idx += 1
        length = len(packet)
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst

        src_port = 0
        dst_port = 0
        protocol = "IP"

        if TCP in packet:
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            protocol = "TCP"
        elif UDP in packet:
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
            protocol = "UDP"
        elif ICMP in packet:
            protocol = "ICMP"

        conversations.append(
            {
                "idx": packet_idx,
                "src": src_ip,
                "dst": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "protocol": protocol,
                "length": length,
                "file": Path(pcap_file).name,
            }
        )

    return conversations, packet_idx


def analyze_multi_capture(pcap_files):
    """Analyze multiple pcap files and build timeline"""
    all_packets = []
    base_idx = 0

    for pcap_file in pcap_files:
        packets, base_idx = analyze_pcap_timeline(pcap_file, base_idx)
        all_packets.extend(packets)

    ip_pairs = {}

    for pkt in all_packets:
        sorted_key = tuple(sorted([pkt["src"], pkt["dst"]]))
        if sorted_key not in ip_pairs:
            ip_pairs[sorted_key] = {
                "packets": [],
                "total_bytes": 0,
                "packet_count": 0,
                "src_counts": {},
                "dst_counts": {},
            }
        ip_pairs[sorted_key]["packets"].append(pkt)
        ip_pairs[sorted_key]["total_bytes"] += pkt["length"]
        ip_pairs[sorted_key]["packet_count"] += 1

        src_counts = ip_pairs[sorted_key]["src_counts"]
        src_counts[pkt["src"]] = src_counts.get(pkt["src"], 0) + 1

        dst_counts = ip_pairs[sorted_key]["dst_counts"]
        dst_counts[pkt["dst"]] = dst_counts.get(pkt["dst"], 0) + 1

    timeline = []
    for pair_key, data in ip_pairs.items():
        packets = sorted(data["packets"], key=lambda x: x["idx"])

        turns = calculate_turns(packets)
        avg_packet_size = (
            data["total_bytes"] / data["packet_count"]
            if data["packet_count"] > 0
            else 0
        )

        if len(packets) > 1:
            first_idx = packets[0]["idx"]
            last_idx = packets[-1]["idx"]
            duration = last_idx - first_idx if last_idx > first_idx else 1
            chattiness = data["packet_count"] / duration
        else:
            chattiness = 1.0

        src_counts = data["src_counts"]
        dst_counts = data["dst_counts"]

        primary_src = max(src_counts.keys(), key=lambda k: src_counts[k])
        primary_dst = max(dst_counts.keys(), key=lambda k: dst_counts[k])

        timeline.append(
            {
                "ip_pair": pair_key,
                "src": primary_src,
                "dst": primary_dst,
                "packet_count": data["packet_count"],
                "total_bytes": data["total_bytes"],
                "avg_packet_size": avg_packet_size,
                "turns": turns,
                "chattiness": chattiness,
                "first_idx": packets[0]["idx"],
                "last_idx": packets[-1]["idx"],
                "packets": packets,
                "files": list(set(p["file"] for p in packets)),
            }
        )

    timeline.sort(key=lambda x: x["first_idx"])

    return timeline, all_packets


def calculate_turns(packets):
    """Calculate number of turns (direction changes) in conversation"""
    if len(packets) < 2:
        return 1

    turns = 1
    prev_src = packets[0]["src"]

    for pkt in packets[1:]:
        if pkt["src"] != prev_src:
            turns += 1
            prev_src = pkt["src"]

    return turns


def get_timeline_summary(timeline):
    """Get summary statistics for timeline"""
    total_packets = sum(t["packet_count"] for t in timeline)
    total_bytes = sum(t["total_bytes"] for t in timeline)
    total_turns = sum(t["turns"] for t in timeline)

    return {
        "total_conversations": len(timeline),
        "total_packets": total_packets,
        "total_bytes": total_bytes,
        "total_turns": total_turns,
        "avg_packets_per_convo": total_packets / len(timeline) if timeline else 0,
        "avg_turns_per_convo": total_turns / len(timeline) if timeline else 0,
    }
