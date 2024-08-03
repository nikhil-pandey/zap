import inspect
import shlex

from fuzzywuzzy import fuzz

from zap.agent_manager import AgentManager
from zap.app_state import AppState
from zap.cliux import UIInterface
from zap.commands.advanced_input import AdvancedInput
from zap.commands.command_registry import CommandRegistry
from zap.commands.development_workflow import DevelopmentWorkflow
from zap.commands.file_context_manager import FileContextManager
from zap.commands.git_manager import GitManager
from zap.commands.utility_commands import UtilityCommands
from zap.config import AppConfig
from zap.contexts.context_command_manager import ContextCommandManager


class Commands:
    def __init__(
        self,
        config: AppConfig,
        state: AppState,
        ui: UIInterface,
        ccm: ContextCommandManager,
        agent_manager: AgentManager,
    ):
        self.config = config
        self.state = state
        self.ui = ui
        self.registry = CommandRegistry()
        self.ccm = ccm
        self.agent_manager = agent_manager
        self.file_manager = FileContextManager(state, ui)
        self.git_manager = GitManager(state, ui)
        self.dev_workflow = DevelopmentWorkflow(config, ui)
        self.utilities = UtilityCommands(state, ui)

        self._register_commands()

    def _register_commands(self):
        # File management commands
        self.registry.command(
            "add", aliases=["a"], description="Add files to the context"
        )(self.file_manager.add)
        self.registry.command(
            "remove", aliases=["rm"], description="Remove files from the context"
        )(self.file_manager.remove)
        self.registry.command(
            "drop", aliases=["d"], description="Clear all files from the context"
        )(self.file_manager.clear)
        self.registry.command(
            "list", aliases=["ls"], description="List all files in the context"
        )(self.file_manager.list)

        # Git commands
        self.registry.command("diff", aliases=["d"], description="Show git diff")(
            self.git_manager.diff
        )

        # Development workflow commands
        self.registry.command("lint", aliases=["l"], description="Run linting")(
            self.dev_workflow.lint
        )
        self.registry.command("build", aliases=["b"], description="Run build process")(
            self.dev_workflow.build
        )
        self.registry.command("test", aliases=["t"], description="Run tests")(
            self.dev_workflow.test
        )

        # Utility commands
        self.registry.command(
            "copy", aliases=["cp"], description="Copy file content to clipboard"
        )(self.utilities.copy_to_clipboard)

        self.registry.command(
            "shell", aliases=["!"], description="Execute a shell command"
        )(self.utilities.shell)

        # Context commands
        self.registry.command(
            "switch_context", aliases=["s"], description="Switch to a different context"
        )(self.ccm.switch_context)
        self.registry.command(
            "show_contexts", aliases=["c"], description="List all available contexts"
        )(self.ccm.show_contexts)
        self.registry.command("save_context", description="Save the current context")(
            self.ccm.save_context
        )
        self.registry.command("load_contexts", description="Load all saved contexts")(
            self.ccm.load_all_contexts
        )
        self.registry.command(
            "list_saved", aliases=["lsc"], description="List all saved contexts"
        )(self.ccm.list_saved_contexts)
        self.registry.command(
            "delete_context", aliases=["dc"], description="Delete a context"
        )(self.ccm.delete_context)
        self.registry.command(
            "rename_context", aliases=["rc"], description="Rename a context"
        )(self.ccm.rename_context)
        self.registry.command(
            "clear_context", aliases=["clc"], description="Clear messages in a context"
        )(self.ccm.clear_context)
        self.registry.command(
            "switch_agent",
            aliases=["sa"],
            description="Switch to a different agent in the current context",
        )(self.ccm.switch_agent)
        self.registry.command(
            "show_agents", aliases=["la"], description="List all available agents"
        )(self.ccm.show_agents)
        self.registry.command("archive_context", description="Archive all contexts")(
            self.ccm.archive_all_contexts
        )
        self.registry.command(
            "show_archives", aliases=["laa"], description="List all archived contexts"
        )(self.ccm.show_archives)
        self.registry.command("load_archived", description="Load an archived context")(
            self.ccm.load_archived_context
        )

        # Help and exit commands
        self.registry.command(
            "help", aliases=["h"], description="Show help information"
        )(self.show_help)

    async def run_command(self, input_string: str) -> None:
        try:
            parts = shlex.split(input_string)
            command = parts[0]
            args = parts[1:]

            cmd_func = self.registry.get(command)
            if cmd_func:
                # Get the number of required arguments for the command
                sig = inspect.signature(cmd_func)
                required_args = sum(
                    1
                    for param in sig.parameters.values()
                    if param.default == param.empty
                    and param.kind != param.VAR_POSITIONAL
                )

                if len(args) < required_args:
                    # If there are not enough arguments, show an error message
                    self.ui.error(
                        f"Not enough arguments for command '{command}'. Expected {required_args}, got {len(args)}."
                    )
                    self.ui.print(
                        f"Usage: {command} {' '.join(param.name for param in sig.parameters.values() if param.default == param.empty and param.kind != param.VAR_POSITIONAL)}"
                    )
                else:
                    await cmd_func(*args)
            else:
                self.ui.print(f"Unknown command: {command}")
                await self.print_closest_commands(command)
        except Exception as e:
            self.ui.exception(e, "Command failed")

    async def show_help(self):
        """Show help information."""
        self.ui.display_table("Available Commands", self.registry.get_all_commands())

    async def print_closest_commands(self, user_input):
        commands = [item["Command"] for item in self.registry.get_all_commands()]
        closest_commands = sorted(
            commands,
            key=lambda x: fuzz.ratio(user_input.lower(), x.lower()),
            reverse=True,
        )[:4]
        if closest_commands:
            self.ui.display_table(
                None, [{"Did you mean?": cmd} for cmd in closest_commands]
            )
        else:
            self.ui.debug("No similar commands found.")
