from os import remove
from subprocess import run
from uuid import uuid4

import click
import pdfkit
import qrcode
from jinja2 import Environment, PackageLoader, select_autoescape


def generate_pdf(html: str) -> str:
    pdf_filepath = generate_tmp_file_path("borg_access_info.pdf")
    pdfkit.from_string(html, pdf_filepath, options={"enable-local-file-access": None})
    click.echo(f"Wrote pdf to file://{pdf_filepath}")


def render_html(vars: dict) -> str:
    env = Environment(
        loader=PackageLoader("paper_backup"), autoescape=select_autoescape()
    )
    template = env.get_template("main.html")
    return template.render(**vars)


def generate_tmp_file_path(filename: str):
    uuid = uuid4()
    return f"/tmp/{uuid}_{filename}"


def create_ssh_qrcode(ssh_key_path: str) -> str:
    with open(ssh_key_path, "r") as f:
        ssh_private_key = f.read()
    img = qrcode.make(ssh_private_key)
    img_path = generate_tmp_file_path("_ssh_qrcode.png")
    img.save(img_path)
    return img_path


def create_ssh_key_melt(ssh_key_path: str) -> str:
    result = run(f"melt {ssh_key_path}", shell=True, capture_output=True)
    if result.returncode != 0:
        raise click.ClickException(f"melt returned: {result.stderr.decode()}")
    else:
        return result.stdout.decode()


@click.command()
@click.argument("ssh_key_path", type=click.Path(exists=True))
@click.argument("borg_repo_url")
@click.argument("borg_repo_ssh_fingerprint")
def generate(ssh_key_path: str, borg_repo_url: str, borg_repo_ssh_fingerprint: str):
    """generate pdf with information to access you borg backup repo"""
    ssh_key_melt = create_ssh_key_melt(ssh_key_path)
    ssh_qrcode_image_path = create_ssh_qrcode(ssh_key_path)
    vars = {
        "borg_repo_url": borg_repo_url,
        "borg_repo_ssh_fingerprint": borg_repo_ssh_fingerprint,
        "ssh_key_melt": ssh_key_melt,
        "ssh_qrcode_image_path": ssh_qrcode_image_path,
    }
    html = render_html(vars)
    generate_pdf(html)
    remove(ssh_qrcode_image_path)


if __name__ == "__main__":
    generate()
