import os
import signal
import subprocess
import shutil
import sys
import click
from pathlib import Path

from scapy.all import sniff, wrpcap


def capture_packets(interface, count, output, filter_expr, duration):
    """Capture packets using tshark (with scapy fallback)"""

    duration = duration or 10
    tshark_path = shutil.which("tshark")

    if tshark_path:
        cmd = [tshark_path, "-w", output, "-F", "pcap", "-a", f"duration:{duration}"]

        if interface:
            cmd.extend(["-i", interface])
        else:
            cmd.extend(["-i", "any"])

        if count:
            cmd.extend(["-c", str(count)])

        if filter_expr:
            cmd.extend(["-f", filter_expr])

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )

            try:
                proc.wait(timeout=duration + 5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                proc.wait(timeout=2)
                click.echo(f"Capture timed out after {duration}s", err=True)

            if proc.returncode == 0:
                click.echo(f"Captured packets saved to: {output}")
                return
            else:
                stderr = proc.stderr.read().decode() if proc.stderr else ""
                click.echo(f"tshark capture failed: {stderr}", err=True)
        except Exception as e:
            click.echo(f"tshark error: {e}", err=True)
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except:
                pass

    try:
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

        click.echo(f"Capturing on {iface} for {duration} seconds...")

        def timeout_handler(signum, frame):
            raise TimeoutError("Capture duration exceeded")

        if duration:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(duration + 2)

        kwargs = {}
        if count:
            kwargs["count"] = count
        if filter_expr:
            kwargs["filter"] = filter_expr

        packets = sniff(iface=iface, timeout=duration, **kwargs)

        signal.alarm(0)

        wrpcap(output, packets)
        click.echo(f"Captured {len(packets)} packets saved to: {output}")

    except TimeoutError:
        click.echo(f"Capture timed out after {duration}s", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error capturing packets: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", default=None)
    parser.add_argument("-c", "--count", type=int, default=None)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("-f", "--filter", default="")
    parser.add_argument("-d", "--duration", type=int, default=10)
    args = parser.parse_args()

    capture_packets(args.interface, args.count, args.output, args.filter, args.duration)
