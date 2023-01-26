from os import remove

import click
import pdfkit

from borg_paper_access_info.html import render_html
from borg_paper_access_info.ssh import (
    create_ssh_key_melt,
    create_ssh_qrcode,
    create_ssh_randomart,
)
from borg_paper_access_info.utils import (
    create_qrcode,
    generate_tmp_file_path,
    get_hostname_from_url,
)


def generate_pdf(html: str, debug=False) -> str:
    if debug:
        pdf_filepath = "out.pdf"
    else:
        pdf_filepath = generate_tmp_file_path("borg_access_info.pdf")
    pdfkit.from_string(html, pdf_filepath, options={"enable-local-file-access": None})
    click.echo(f"Wrote pdf to file://{pdf_filepath}")


def create_borg_repo_qrcode(
    borg_repo_url: str, borg_repo_ssh_fingerprint: str, borg_repo_password: str
) -> str:
    borg_repo_info = {
        "url": borg_repo_url,
        "ssh_fingerprint": borg_repo_ssh_fingerprint,
        "password": borg_repo_password,
    }
    return create_qrcode(borg_repo_info, "borg_repo_info.png")


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
    borg_repo_qrcode_image_path = create_borg_repo_qrcode(
        borg_repo_url, borg_repo_ssh_fingerprint, borg_repo_password
    )
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
