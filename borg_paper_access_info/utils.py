from urllib.parse import urlparse
from uuid import uuid4

import qrcode


def generate_tmp_file_path(filename: str) -> str:
    uuid = uuid4()
    return f"/tmp/{uuid}_{filename}"


def create_qrcode(text: str, filename: str) -> str:
    img = qrcode.make(text)
    img_path = generate_tmp_file_path(filename)
    img.save(img_path)
    return img_path


def get_hostname_from_url(url: str) -> str:
    return urlparse(url).hostname
