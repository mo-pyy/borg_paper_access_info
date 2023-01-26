from importlib.resources import read_text

from jinja2 import Environment, FunctionLoader, select_autoescape


def load_jinja_template(name: str) -> str:
    if name == "main.html":
        return read_text(__package__, "main.html")
    else:
        return None


def render_html(vars: dict) -> str:
    env = Environment(
        loader=FunctionLoader(load_jinja_template), autoescape=select_autoescape()
    )
    template = env.get_template("main.html")
    return template.render(**vars)
