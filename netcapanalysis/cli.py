import click
import sys
from pathlib import Path

from .capture import capture_packets
from .analyzer import analyze_pcap
from .charts import (
    generate_length_chart,
    generate_port_chart,
    generate_conversation_diagram,
    generate_timeline_chart,
    generate_timeline_sequence,
    generate_chattiness_chart,
)
from .multianalyze import analyze_multi_capture, get_timeline_summary
from .report import generate_report


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Network Capture and Analysis Tool"""
    pass


@cli.command()
@click.option(
    "-i", "--interface", default=None, help="Network interface to capture from"
)
@click.option("-c", "--count", default=100, help="Number of packets to capture")
@click.option("-o", "--output", required=True, help="Output pcap file")
@click.option("-f", "--filter", default="", help="BPF filter expression")
@click.option(
    "-d", "--duration", default=None, type=int, help="Capture duration in seconds"
)
def capture(interface, count, output, filter, duration):
    """Capture network packets to a pcap file"""
    capture_packets(interface, count, output, filter, duration)


@cli.command()
@click.option("-i", "--input", "input_file", required=True, help="Input pcap file")
@click.option("-o", "--output", default="report.md", help="Output markdown report")
@click.option("--no-png", is_flag=True, help="Skip PNG generation")
def analyze(input_file, output, no_png):
    """Analyze pcap file and generate report"""
    if not Path(input_file).exists():
        click.echo(f"Error: Input file '{input_file}' not found", err=True)
        sys.exit(1)

    stats = analyze_pcap(input_file)

    generate_report(stats, input_file, output, not no_png)
    click.echo(f"Report generated: {output}")


@cli.command()
@click.option("-i", "input_file", required=True, help="Input pcap file")
@click.option("-o", "--output", required=True, help="Output chart file")
@click.option(
    "-t",
    "--type",
    "chart_type",
    type=click.Choice(["length", "port", "conversation"]),
    default="port",
    help="Chart type",
)
def chart(input_file, output, chart_type):
    """Generate chart from pcap file"""
    if not Path(input_file).exists():
        click.echo(f"Error: Input file '{input_file}' not found", err=True)
        sys.exit(1)

    stats = analyze_pcap(input_file)

    if chart_type == "length":
        generate_length_chart(stats, output)
    elif chart_type == "port":
        generate_port_chart(stats, output)
    elif chart_type == "conversation":
        generate_conversation_diagram(stats, output)

    click.echo(f"Chart generated: {output}")


@cli.command()
@click.option("-i", "input_file", required=True, help="Input pcap file")
@click.option("-o", "--output", required=True, help="Output mermaid file")
def mermaid(input_file, output):
    """Generate mermaid diagrams from pcap file"""
    if not Path(input_file).exists():
        click.echo(f"Error: Input file '{input_file}' not found", err=True)
        sys.exit(1)

    stats = analyze_pcap(input_file)

    mermaid_code = generate_conversation_diagram(stats, None)

    Path(output).write_text(mermaid_code)
    click.echo(f"Mermaid diagram saved: {output}")


@cli.command()
@click.option(
    "-i",
    "--inputs",
    "input_files",
    required=True,
    multiple=True,
    help="Input pcap files (can specify multiple)",
)
@click.option("-o", "--output", default="timeline.md", help="Output markdown report")
@click.option("--no-png", is_flag=True, help="Skip PNG generation")
def timeline(input_files, output, no_png):
    """Analyze multiple pcap files and show timeline of conversations"""
    for f in input_files:
        if not Path(f).exists():
            click.echo(f"Error: Input file '{f}' not found", err=True)
            sys.exit(1)

    timeline_data, all_packets = analyze_multi_capture(list(input_files))
    summary = get_timeline_summary(timeline_data)

    output_path = Path(output)
    output_dir = output_path.parent
    base_name = output_path.stem

    if not no_png:
        generate_chattiness_chart(
            timeline_data, str(output_dir / f"{base_name}_chattiness.png")
        )
        generate_timeline_chart(
            timeline_data, str(output_dir / f"{base_name}_timeline.png")
        )
        generate_timeline_sequence(
            timeline_data, str(output_dir / f"{base_name}_sequence.png")
        )

    mermaid_timeline = generate_timeline_chart(timeline_data, None)
    mermaid_sequence = generate_timeline_sequence(timeline_data, None)

    markdown = f"""# Multi-Capture Timeline Analysis

**Input Files**: {", ".join(input_files)}
**Generated**: {Path(output).name}

---

## Summary

| Metric | Value |
|--------|-------|
| Total Conversations | {summary["total_conversations"]:,} |
| Total Packets | {summary["total_packets"]:,} |
| Total Bytes | {summary["total_bytes"]:,} |
| Total Turns | {summary["total_turns"]:,} |
| Avg Packets/Conversation | {summary["avg_packets_per_convo"]:.1f} |
| Avg Turns/Conversation | {summary["avg_turns_per_convo"]:.1f} |

---

## Timeline Chart (Past -> Present)

![Timeline]({base_name}_timeline.png)

```mermaid
{mermaid_timeline}
```

---

## Conversation Flow Sequence

![Sequence]({base_name}_sequence.png)

```mermaid
{mermaid_sequence}
```

---

## Chattiness Analysis

![Chattiness]({base_name}_chattiness.png)

---

## Conversation Details

| Source IP | Dest IP | Packets | Bytes | Avg Size | Turns | Chattiness |
|-----------|---------|---------|-------|----------|-------|------------|
"""

    for conv in timeline_data:
        markdown += f"| {conv['src']} | {conv['dst']} | {conv['packet_count']:,} | {conv['total_bytes']:,} | {conv['avg_packet_size']:.1f} | {conv['turns']} | {conv['chattiness']:.2f} |\n"

    markdown += """

---

*Timeline generated by NetCap Analysis Tool*
"""

    Path(output).write_text(markdown)
    click.echo(f"Timeline analysis generated: {output}")


if __name__ == "__main__":
    cli()
