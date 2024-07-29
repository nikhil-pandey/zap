import os

import pytest

from zap.templating.default_resolver import DefaultPathResolver
from zap.templating.engine import ZapTemplateEngine


@pytest.fixture
def engine():
    return ZapTemplateEngine({}, os.getcwd())


@pytest.fixture
def resolver():
    return DefaultPathResolver(os.getcwd())
