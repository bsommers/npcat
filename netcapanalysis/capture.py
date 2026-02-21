import subprocess
import shutil
import sys
import click
from pathlib import Path

from scapy.all import sniff, wrpcap


def capture_packets(interface, count, output, filter_expr, duration):
    """Capture packets using scapy (or tshark if available)"""

    tshark_path = shutil.which("tshark")
    if tshark_path:
        cmd = [tshark_path, "-w", output, "-F", "pcap"]

        if interface:
            cmd.extend(["-i", interface])
        else:
            cmd.extend(["-i", "any"])

        if count:
            cmd.extend(["-c", str(count)])

        if duration:
            cmd.extend(["-a", f"duration:{duration}"])

        if filter_expr:
            cmd.extend(["-f", filter_expr])

        try:
            subprocess.run(cmd, check=True)
            click.echo(f"Captured packets saved to: {output}")
            return
        except subprocess.CalledProcessError as e:
            click.echo(f"tshark capture failed, trying scapy...", err=True)

    try:
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Capture duration exceeded")

        if duration:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(duration)

        kwargs = {}
        if count:
            kwargs["count"] = count
        if filter_expr:
            kwargs["filter"] = filter_expr

        from scapy.all import get_if_list

        if not interface:
            available = get_if_list()
            if "any" in available:
                iface = "any"
            elif available:
                iface = available[0]
            else:
                click.echo("Error: No network interfaces available", err=True)
                sys.exit(1)
        else:
            iface = interface

        click.echo(f"Capturing on {iface}...")
        packets = sniff(iface=iface, **kwargs)

        wrpcap(output, packets)
        click.echo(f"Captured {len(packets)} packets saved to: {output}")

    except Exception as e:
        click.echo(f"Error capturing packets: {e}", err=True)
        sys.exit(1)
