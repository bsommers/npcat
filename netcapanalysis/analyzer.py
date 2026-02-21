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


def analyze_pcap(pcap_file):
    """Analyze pcap file and return statistics"""
    stats = {
        "total_packets": 0,
        "total_bytes": 0,
        "protocols": defaultdict(int),
        "lengths": [],
        "port_stats": defaultdict(lambda: {"count": 0, "protocol": None}),
        "conversations": defaultdict(
            lambda: {"packets": 0, "bytes": 0, "protocols": set()}
        ),
    }

    try:
        packets = rdpcap(str(pcap_file))
    except Exception as e:
        print(f"Error opening pcap file: {e}", file=sys.stderr)
        sys.exit(1)

    for packet in packets:
        stats["total_packets"] += 1
        length = len(packet)
        stats["total_bytes"] += length
        stats["lengths"].append(length)

        if IP in packet:
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

            stats["protocols"][protocol] += 1

            if dst_port > 0:
                stats["port_stats"][dst_port]["count"] += 1
                stats["port_stats"][dst_port]["protocol"] = protocol

            conv_key = f"{src_ip}:{src_port} <-> {dst_ip}:{dst_port}"
            stats["conversations"][conv_key]["packets"] += 1
            stats["conversations"][conv_key]["bytes"] += length
            stats["conversations"][conv_key]["protocols"].add(protocol)
            stats["conversations"][conv_key]["src"] = src_ip
            stats["conversations"][conv_key]["dst"] = dst_ip
            stats["conversations"][conv_key]["src_port"] = src_port
            stats["conversations"][conv_key]["dst_port"] = dst_port
        else:
            stats["protocols"]["Non-IP"] = stats["protocols"].get("Non-IP", 0) + 1

    stats["protocols"] = dict(stats["protocols"])
    stats["port_stats"] = dict(stats["port_stats"])
    stats["conversations"] = dict(stats["conversations"])

    return stats


def get_length_distribution(stats):
    """Get packet length distribution"""
    lengths = stats.get("lengths", [])
    if not lengths:
        return {}

    bins = {
        "0-100": 0,
        "101-500": 0,
        "501-1000": 0,
        "1001-1500": 0,
        "1500+": 0,
    }

    for length in lengths:
        if length <= 100:
            bins["0-100"] += 1
        elif length <= 500:
            bins["101-500"] += 1
        elif length <= 1000:
            bins["501-1000"] += 1
        elif length <= 1500:
            bins["1001-1500"] += 1
        else:
            bins["1500+"] += 1

    return bins


def get_top_ports(stats, n=10):
    """Get top N destination ports"""
    port_stats = stats.get("port_stats", {})
    sorted_ports = sorted(port_stats.items(), key=lambda x: x[1]["count"], reverse=True)
    return sorted_ports[:n]
