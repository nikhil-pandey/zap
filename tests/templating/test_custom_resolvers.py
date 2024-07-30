import pytest
from zap.templating.engine import ZapTemplateEngine
from zap.templating.resolver import PathResolver

class CustomPathResolver(PathResolver):
    async def resolve_file(self, path: str) -> str:
        # Custom logic for resolving file paths
        return f"Custom resolved content for {path}"

    async def resolve_http(self, url: str) -> str:
        # Custom logic for resolving URLs
        return f"Custom resolved content for {url}"

@pytest.mark.asyncio
async def test_custom_path_resolver():
    custom_resolver = CustomPathResolver()
    template_engine = ZapTemplateEngine(resolver=custom_resolver, templates={'index.html': '{{ i("custom/path/to/file") }}'})

    rendered = await template_engine.render_file('index.html')
    assert rendered == 'Custom resolved content for custom/path/to/file'