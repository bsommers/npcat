import subprocess
import shutil
import sys
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")

from .analyzer import get_length_distribution, get_top_ports, get_service_name


def mermaid_to_png(mermaid_code, output_path):
    """Convert mermaid code to PNG using mermaid-cli"""
    mmd_path = Path(output_path).with_suffix(".mmd")
    mmd_path.write_text(mermaid_code)

    node_modules_mm = shutil.which("mmdc") or shutil.which("mermaid")

    if not node_modules_mm:
        try:
            subprocess.run(
                [
                    "npx",
                    "-y",
                    "@mermaid-js/mermaid-cli",
                    "-i",
                    str(mmd_path),
                    "-o",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Could not generate PNG: {e}", file=sys.stderr)
            return False
    else:
        subprocess.run(
            [node_modules_mm, "-i", str(mmd_path), "-o", str(output_path)],
            check=True,
            capture_output=True,
        )

    return True


def generate_length_chart(stats, output):
    """Generate packet length distribution bar chart"""
    dist = get_length_distribution(stats)

    if not dist:
        print("No packet length data available")
        return

    categories = list(dist.keys())
    counts = list(dist.values())

    plt.figure(figsize=(10, 6))
    bars = plt.bar(
        categories,
        counts,
        color=["#3498db", "#2ecc71", "#f39c12", "#e74c3c", "#9b59b6"],
    )

    plt.xlabel("Packet Length (bytes)", fontsize=12)
    plt.ylabel("Packet Count", fontsize=12)
    plt.title("Packet Length Distribution", fontsize=14, fontweight="bold")

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()


def generate_port_chart(stats, output):
    """Generate destination port bar chart"""
    top_ports = get_top_ports(stats, 10)

    if not top_ports:
        print("No port data available")
        return

    ports = []
    counts = []
    labels = []

    for port, data in top_ports:
        ports.append(port)
        counts.append(data["count"])
        service = get_service_name(port)
        labels.append(f"{port}\n({service})")

    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(ports)), counts, color="#3498db")

    plt.xlabel("Destination Port", fontsize=12)
    plt.ylabel("Packet Count", fontsize=12)
    plt.title("Top Destination Ports", fontsize=14, fontweight="bold")
    plt.xticks(range(len(ports)), labels, rotation=45, ha="right")

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()


def generate_conversation_diagram(stats, output):
    """Generate mermaid sequence diagram for conversations"""
    conversations = stats.get("conversations", {})

    if not conversations:
        return "sequenceDiagram\n    note: No conversations found"

    sorted_convs = sorted(
        conversations.items(), key=lambda x: x[1]["packets"], reverse=True
    )[:15]

    lines = ["sequenceDiagram"]

    participants = set()
    for key, data in sorted_convs:
        participants.add(data["src"])
        participants.add(data["dst"])

    for p in sorted(participants):
        lines.append(f"    participant {p}")

    lines.append("")

    for key, data in sorted_convs:
        src = data["src"]
        dst = data["dst"]
        packets = data["packets"]
        bytes_ = data["bytes"]

        lines.append(f"    {src}->>{dst}: {packets} packets, {bytes_} bytes")

    mermaid_code = "\n".join(lines)

    if output:
        if output.endswith(".png"):
            mermaid_to_png(mermaid_code, output)
        else:
            Path(output).write_text(mermaid_code)

    return mermaid_code


def generate_length_mermaid(stats):
    """Generate mermaid code for length distribution"""
    dist = get_length_distribution(stats)

    if not dist:
        return "pie title Packet Length Distribution\n    No data: 0"

    lines = ["pie title Packet Length Distribution"]
    for label, count in dist.items():
        lines.append(f'    "{label}": {count}')

    return "\n".join(lines)


def generate_port_mermaid(stats):
    """Generate mermaid code for port distribution"""
    top_ports = get_top_ports(stats, 10)

    if not top_ports:
        return "pie title Port Distribution\n    No data: 0"

    lines = ["pie title Top Destination Ports"]
    for port, data in top_ports:
        service = get_service_name(port)
        lines.append(f'    "Port {port} ({service})": {data["count"]}')

    return "\n".join(lines)
