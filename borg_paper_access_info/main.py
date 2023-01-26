from os import remove
from subprocess import run
from urllib.parse import urlparse
from uuid import uuid4

import click
import pdfkit
import qrcode
from jinja2 import Environment, PackageLoader, select_autoescape


def generate_pdf(html: str, debug=False) -> str:
    if debug:
        pdf_filepath = "out.pdf"
    else:
        pdf_filepath = generate_tmp_file_path("borg_access_info.pdf")
    pdfkit.from_string(html, pdf_filepath, options={"enable-local-file-access": None})
    click.echo(f"Wrote pdf to file://{pdf_filepath}")


def render_html(vars: dict) -> str:
    env = Environment(
        loader=PackageLoader("borg_paper_access_info"), autoescape=select_autoescape()
    )
    template = env.get_template("main.html")
    return template.render(**vars)


def generate_tmp_file_path(filename: str) -> str:
    uuid = uuid4()
    return f"/tmp/{uuid}_{filename}"


def create_ssh_qrcode(ssh_key_path: str) -> str:
    with open(ssh_key_path, "r") as f:
        ssh_private_key = f.read()
    return create_qrcode(ssh_private_key, "ssh_qrcode.png")


def create_qrcode(text: str, filename: str) -> str:
    img = qrcode.make(text)
    img_path = generate_tmp_file_path(filename)
    img.save(img_path)
    return img_path


def create_ssh_key_melt(ssh_key_path: str) -> str:
    result = run(f"melt {ssh_key_path}", shell=True, capture_output=True)
    if result.returncode != 0:
        raise click.ClickException(f"melt returned: {result.stderr.decode()}")
    else:
        return result.stdout.decode()


def get_hostname_from_url(url: str) -> str:
    return urlparse(url).hostname


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


@click.command()
@click.argument("ssh_key_path", type=click.Path(exists=True))
@click.argument("borg_repo_url")
@click.argument("borg_repo_ssh_fingerprint")
@click.argument("borg_repo_password")
@click.option("--debug", is_flag=True, default=False)
def generate(
    ssh_key_path: str,
    borg_repo_url: str,
    borg_repo_ssh_fingerprint: str,
    borg_repo_password: str,
    debug: bool,
):
    """generate pdf with information to access you borg backup repo"""
    randomart = create_ssh_randomart(
        get_hostname_from_url(borg_repo_url), borg_repo_ssh_fingerprint
    )
    ssh_key_melt = create_ssh_key_melt(ssh_key_path)
    ssh_qrcode_image_path = create_ssh_qrcode(ssh_key_path)
    borg_repo_info = {
        "url": borg_repo_url,
        "ssh_fingerprint": borg_repo_ssh_fingerprint,
        "password": borg_repo_password,
    }
    borg_repo_qrcode_image_path = create_qrcode(borg_repo_info, "borg_repo_info.png")
    vars = {
        "borg_repo_url": borg_repo_url,
        "borg_repo_ssh_fingerprint": borg_repo_ssh_fingerprint,
        "borg_repo_password": borg_repo_password,
        "ssh_key_melt": ssh_key_melt,
        "ssh_qrcode_image_path": ssh_qrcode_image_path,
        "borg_repo_ssh_fingerprint_randomart": randomart,
        "borg_repo_qrcode_image_path": borg_repo_qrcode_image_path,
    }
    html = render_html(vars)
    if debug:
        with open("out.html", "w") as f:
            f.write(html)
    generate_pdf(html, debug)
    if not debug:
        remove(ssh_qrcode_image_path)
        remove(borg_repo_qrcode_image_path)


if __name__ == "__main__":
    generate(auto_envvar_prefix="BORG_PAPER_ACCESS_INFO")
