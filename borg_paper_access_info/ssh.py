from subprocess import run

import click

from borg_paper_access_info.utils import create_qrcode


def create_ssh_qrcode(ssh_key_path: str) -> str:
    with open(ssh_key_path, "r") as f:
        ssh_private_key = f.read()
    return create_qrcode(ssh_private_key, "ssh_qrcode.png")


def create_ssh_key_melt(ssh_key_path: str) -> str:
    result = run(f"melt {ssh_key_path}", shell=True, capture_output=True)
    if result.returncode != 0:
        raise click.ClickException(f"melt returned: {result.stderr.decode()}")
    else:
        return result.stdout.decode()


def create_ssh_randomart(hostname: str, host_fingerprint: str):
    result = run(
        ["bash", "-c", f"ssh-keygen -lv -f <(ssh-keyscan -t ed25519 {hostname})"],
        capture_output=True,
    )
    output = result.stdout.decode()
    lines = output.splitlines()
    reported_fingerprint = lines[0].split(" ")[1]
    if not reported_fingerprint == host_fingerprint:
        raise click.ClickException(
            f"ssh fingerprints did not match. user specified {host_fingerprint} but server reported {reported_fingerprint}"  # noqa: long string
        )
    else:
        return "\n".join(lines[1:])
