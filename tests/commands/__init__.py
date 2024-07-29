import pytest

from zap.commands.command_registry import CommandRegistry


@pytest.fixture
def registry():
    return CommandRegistry()


async def dummy_command():
    return "Dummy command executed"


def test_register_command(registry):
    registry.register("test", dummy_command, "Test command")
    assert "test" in registry.commands
    assert registry.commands["test"]["description"] == "Test command"


def test_command_decorator(registry):
    @registry.command("decorated", aliases=["d"], description="Decorated command")
    async def decorated_command():
        return "Decorated command executed"

    assert "decorated" in registry.commands
    assert "d" in registry.commands
    assert registry.commands["decorated"]["description"] == "Decorated command"
    assert registry.commands["d"]["description"] == "Alias for decorated"


def test_get_command(registry):
    registry.register("test", dummy_command, "Test command")
    assert registry.get("test") == dummy_command


def test_is_command(registry):
    registry.register("test", dummy_command, "Test command")
    assert registry.is_command("test")
    assert not registry.is_command("nonexistent")


def test_get_all_commands(registry):
    registry.register("test1", dummy_command, "Test command 1")
    registry.register("test2", dummy_command, "Test command 2", show=False)

    visible_commands = registry.get_all_commands()
    all_commands = registry.get_all_commands(show_hidden=True)

    assert len(visible_commands) == 1
    assert len(all_commands) == 2
