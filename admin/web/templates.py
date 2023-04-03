from aiohttp.web_app import Application
import jinja2
import aiohttp_jinja2


def setup_templates(app: Application) -> None:
    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader("./admin/web/templates")
    )
