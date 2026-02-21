import click
import sys
from pathlib import Path

from .capture import capture_packets
from .analyzer import analyze_pcap
from .charts import (
    generate_length_chart,
    generate_port_chart,
    generate_conversation_diagram,
)
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


if __name__ == "__main__":
    cli()
