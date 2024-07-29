import asyncio
import dataclasses
import os
import sys
import time
from pathlib import Path
from typing import Optional

import tiktoken
from rich.align import Align
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from zap.agent_manager import AgentManager
from zap.agents.base import ChatAgent, Agent
from zap.agents.chat_message import ChatMessage
from zap.app_state import AppState
from zap.cliux import UI
from zap.commands import Commands
from zap.config import AppConfig, load_config
from zap.constants import FILE_ICONS
from zap.contexts.agent_template_context import AgentTemplateContext
from zap.contexts.context import Context
from zap.contexts.context_manager import ContextManager
from zap.contexts.context_command_manager import ContextCommandManager
from zap.git_analyzer import GitAnalyzer
from zap.templating import ZapTemplateEngine
from zap.tools.basic_tools import register_tools
from zap.tools.tool_manager import ToolManager


class ZapApp:
    def __init__(self):
        self.template_engine: Optional[ZapTemplateEngine] = None
        self.interrupt_count = 0
        self.last_interrupt_time = time.time()
        self.config: Optional[AppConfig] = None
        self.state: Optional[AppState] = None
        self.ui: Optional[UI] = None
        self.git_analyzer: Optional[GitAnalyzer] = None
        self.commands: Optional[Commands] = None
        self.chat_agent: Optional[ChatAgent] = None

    async def initialize(self, args):
        # Load config
        config_paths = [
            Path.cwd() / "zap_config.yaml",
            Path.home() / ".zap" / "config.yaml",
        ]
        self.config = load_config(config_paths, args)
        self.state = AppState()

        # Initialize UI
        self.ui = UI(self.config.ui_config)
        await self._show_startup_banner()

        # Initialize Git Analyzer
        self.git_analyzer = GitAnalyzer(args.repo_path, self.config.git_analyzer_config)
        repo_info = await self.git_analyzer.analyze()
        self.state.repo_metadata = repo_info
        self.state.git_repo = self.git_analyzer.git_repo
        self.state.config = self.config

        # Initialize ContextManager and ChatAgent
        self.template_engine = ZapTemplateEngine(root_path=self.state.git_repo.root,
                                                 templates_dir=self.config.templates_dir)

        # Initialize Commands
        self.tool_manager = ToolManager()
        register_tools(tool_manager=self.tool_manager, app_state=self.state, ui=self.ui)
        self.agent_manager = AgentManager(
            Path(self.config.templates_dir) / "agents",
            self.tool_manager, self.ui, self.template_engine)
        default_agent = self.agent_manager.get_agent(self.config.agent)
        self.state.tokenizer = tiktoken.encoding_for_model(default_agent.config.model)
        self.context_manager = ContextManager(self.agent_manager, self.config.agent)
        if self.config.auto_archive_contexts:
            archive_name = f"AutoArchive-{time.strftime('%Y-%m-%d-%H-%M-%S')}"
            if self.context_manager.archive_all_contexts(archive_name):
                self.ui.print(f"Archived old context to {archive_name}")
        if self.config.auto_load_contexts:
            if self.context_manager.load_all_contexts():
                self.ui.print(f"Loaded {len(self.context_manager.contexts)} contexts")
                self.ui.print(f"Resuming context: {self.context_manager.current_context}")
            else:
                self.ui.print("No contexts loaded. Starting a 'default' context")
        self.ccm = ContextCommandManager(self.context_manager, self.ui, self.agent_manager)
        self.commands = Commands(self.config, self.state, self.ui, self.ccm, self.agent_manager)

    async def run(self):
        while True:
            try:
                context = self.context_manager.get_current_context()
                agent = self.agent_manager.get_agent(context.current_agent)

                user_input = await self.commands.advanced_input.input_async(
                    f"{context.name}:{agent.config.name} {FILE_ICONS['zap']}")

                await self.handle_input(user_input, context, agent)
            except KeyboardInterrupt:
                current_time = time.time()
                diff = current_time - self.last_interrupt_time

                if diff < 5 and self.interrupt_count:
                    self.ui.debug(
                        f"Received another keyboard interrupt after {diff} seconds"
                    )
                    self.interrupt_count += 1
                else:
                    self.ui.debug(
                        f"Received another keyboard interrupt after {diff} seconds"
                    )
                    self.interrupt_count = 1

                self.last_interrupt_time = current_time

                if self.interrupt_count >= 2:
                    self.ui.print(
                        "Received two keyboard interrupts within 5 seconds. Exiting..."
                    )
                    sys.exit()
            except EOFError:
                return
            except Exception as e:
                self.ui.exception(e, "An error occurred")

    async def _show_startup_banner(self):
        self.ui.raw(
            Panel(
                Align.left(
                    Text.assemble(
                        f"Welcome to Zap {FILE_ICONS['zap']}\n",
                        "Type /help to see available commands\n",
                        "Type /exit to exit",
                    ),
                    vertical="middle",
                ),
                style="bold blue",
            ),
        )

        if self.config.verbose:
            self.ui.print("Verbose mode enabled")
            self.ui.data_view(self.config, False, "App Config")

    async def perform_tasks(self, tasks: list[str], parallel: bool):
        if parallel:
            # TODO: needs some work as everything the state management is not thread safe
           raise NotImplementedError("Parallel task execution is not implemented yet")

        self.ui.print(f"Performing {len(tasks)} tasks")
        final_tasks = []
        for task in tasks:
            current_tasks = []
            if os.path.exists(task):
                self.ui.print(f"Reading tasks from {task}")
                with open(task, "r") as f:
                    tasks = f.readlines()
                    for t in tasks:
                        if t and t.strip() != "":
                            current_tasks.append(t.strip())
            else:
                current_tasks.append(task)
            final_tasks.append((task, current_tasks))

        async_tasks = []
        for (name, task_group) in final_tasks:
            async_tasks.append(self._run_task_group(name, task_group))
            if not parallel:
                await async_tasks[-1]

        if parallel:
            await asyncio.gather(*async_tasks)

    async def _run_task_group(self, group_name, task_group):
        self.ui.print(f"Running {len(task_group)} in {group_name}")
        for task in task_group:
            self.ui.print(f"Task[{group_name}]: {task}")
            context = self.context_manager.get_current_context()
            agent = self.agent_manager.get_agent(context.current_agent)
            await self.handle_input(task, context, agent)

    async def handle_input(self, user_input, context, agent):
        if user_input.startswith("/"):
            await self.commands.run_command(user_input)
        elif user_input in ["exit", "quit", "q", "/exit"]:
            self.ui.print("Exiting...")
            sys.exit()
        else:
            await self.chat_async(user_input, context, agent)

    async def chat_async(self, user_input: str, context: Context, agent: Agent):
        template_context = await AgentTemplateContext.build(user_input, context, agent, self.state, self.config)
        template_context_dict = dataclasses.asdict(template_context)
        rendered_input = await self.template_engine.render(user_input, template_context_dict)
        output = await agent.process(rendered_input, context, template_context_dict)
        self.ui.print(f"{type(agent).__name__}: {escape(output.content)}")

        for msg in output.message_history:
            chat_message = ChatMessage.from_agent_output(msg, agent.config.name)
            chat_message.metadata['raw_input'] = user_input
            if user_input != rendered_input:
                chat_message.metadata['rendered_input'] = rendered_input
            context.add_message(chat_message)
        if self.config.auto_persist_contexts:
            self.context_manager.save_context(context.name)
