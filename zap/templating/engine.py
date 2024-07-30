import os
from urllib.parse import urlparse

from jinja2 import Environment, BaseLoader, TemplateNotFound

from .default_resolver import DefaultPathResolver
from .resolver import PathResolver


class ZapTemplateLoader(BaseLoader):
    def __init__(self, templates: dict[str, str]):
        self.templates = templates

    def get_source(
        self, environment: Environment, template: str
    ) -> tuple[str, str, callable]:
        if template in self.templates:
            return self.templates[template], template, lambda: True
        raise TemplateNotFound(template)


class ZapTemplateEngine:
    def __init__(
        self,
        templates: dict[str, str] = None,
        root_path: str = None,
        resolver: PathResolver = None,
        templates_dir: str = None,
    ):
        self.templates = templates or {}
        if templates_dir:
            self._load_templates_from_dir(templates_dir)
        self.root_path = root_path or os.getcwd()
        self.resolver = resolver or DefaultPathResolver(self.root_path)
        self.env = self._create_environment()

    def _create_environment(self) -> Environment:
        env = Environment(
            loader=ZapTemplateLoader(self.templates),
            extensions=[],
            enable_async=True,
        )
        # Register custom functions
        env.globals.update(
            {
                "i": self.include_url,
            }
        )
        return env

    async def render_file(self, file_path: str, context: dict[str, any] = None) -> str:
        template = self.env.get_template(file_path)
        return await template.render_async(context or {})

    async def render(self, template_string: str, context: dict[str, any] = None) -> str:
        self.env.globals.update(context or {})
        template = self.env.from_string(template_string)
        return await template.render_async()

    async def include_url(self, url: str) -> str:
        parsed_url = urlparse(url)
        if parsed_url.scheme in ["http", "https"]:
            return await self.resolver.resolve_http(url)
        else:
            return await self.resolver.resolve_file(url)

    def _load_templates_from_dir(self, templates_dir):
        for root, _, files in os.walk(templates_dir):
            for file in files:
                with open(os.path.join(root, file), "r") as f:
                    p = os.path.relpath(
                        str(os.path.join(root, file)), templates_dir
                    ).replace("\\", "/")
                    self.templates[p] = f.read()
