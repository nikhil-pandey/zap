import argparse
import asyncio
import dataclasses
import os
from pathlib import Path

import aiofiles
import yaml
from dotenv import load_dotenv

from zap.app import ZapApp
from zap.config import load_config, AppConfig


def parse_arguments():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Zap CLI")
    parser.add_argument(
        "--tasks",
        type=str,
        nargs="*",
        default=None,
        help="Specify the tasks to be performed either inline or file path",
    )
    parser.add_argument("--parallel", action="store_true", help="Run tasks in parallel")
    parser.add_argument(
        "--openai-api-key", type=str, default=None, help="OpenAI API key"
    )
    parser.add_argument(
        "--openai-api-base", type=str, default=None, help="OpenAI API base URL"
    )
    parser.add_argument(
        "--anthropic-api-key", type=str, default=None, help="Anthropic API key"
    )
    parser.add_argument(
        "--replicate-api-key", type=str, default=None, help="Replicate API key"
    )
    parser.add_argument(
        "--togetherai-api-key", type=str, default=None, help="TogetherAI API key"
    )
    parser.add_argument(
        "--azure-api-base", type=str, default=None, help="Azure API base URL"
    )
    parser.add_argument(
        "--azure-api-version", type=str, default=None, help="Azure API version"
    )
    parser.add_argument(
        "--azure-api-key", type=str, default=None, help="Azure API Key"
    )
    parser.add_argument(
        "--azure-api-type", type=str, default=None, help="Azure API type"
    )

    parser.add_argument("--verbose", action="store_true", help="Use verbose mode")
    parser.add_argument(
        "--templates-dir",
        type=str,
        default=None,
        help="Path to the templates directory",
    )
    parser.add_argument("--agent", type=str, default="chat", help="Agent to start with")
    parser.add_argument(
        "--repo-path", type=str, default=".", help="Path to the Git repository"
    )

    # Initialize config and templates
    parser.add_argument(
        "--init-config",
        action="store_true",
        help="Initialize a sample config file at ~/.zap/config.yaml",
    )
    parser.add_argument(
        "--init-templates",
        action="store_true",
        help="Initialize the templates directory in config",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force the operation for init-config and init-templates",
    )

    return parser.parse_args()


def set_environment_variables(args):
    if args.openai_api_key:
        os.environ["OPENAI_API_KEY"] = args.openai_api_key
    if args.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = args.anthropic_api_key
    if args.replicate_api_key:
        os.environ["REPLICATE_API_KEY"] = args.replicate_api_key
    if args.togetherai_api_key:
        os.environ["TOGETHERAI_API_KEY"] = args.togetherai_api_key
    if args.azure_api_base:
        os.environ["AZURE_API_BASE"] = args.azure_api_base
    if args.azure_api_version:
        os.environ["AZURE_API_VERSION"] = args.azure_api_version
    if args.azure_api_type:
        os.environ["AZURE_API_TYPE"] = args.azure_api_type
    if args.azure_api_key:
        os.environ["AZURE_API_KEY"] = args.azure_api_key
    if args.openai_api_base:
        os.environ["OPENAI_API_BASE"] = args.openai_api_base

    callbacks = []
    if os.getenv("LANGFUSE_PUBLIC_KEY") is not None:
        callbacks.append("langfuse")
    if os.getenv("LUNARY_PUBLIC_KEY") is not None:
        callbacks.append("lunary")
    if os.getenv("HELICONE_API_KEY") is not None:
        callbacks.append("helicone")

    import litellm

    if len(callbacks) > 0:
        litellm.success_callbacks = callbacks
    litellm.drop_params = True

    if args.verbose:
        # print env variables partially for debugging
        litellm.set_verbose = True
        print("Environment Variables:")
        print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', '')[:6]}...")
        print(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY', '')[:6]}...")
        print(f"REPLICATE_API_KEY: {os.getenv('REPLICATE_API_KEY', '')[:6]}...")
        print(f"TOGETHERAI_API_KEY: {os.getenv('TOGETHERAI_API_KEY', '')[:6]}...")
        print(f"AZURE_API_BASE: {os.getenv('AZURE_API_BASE', '')}")
        print(f"AZURE_API_VERSION: {os.getenv('AZURE_API_VERSION', '')}")
        print(f"AZURE_API_TYPE: {os.getenv('AZURE_API_TYPE', '')}")
        print(f"OPENAI_API_BASE: {os.getenv('OPENAI_API_BASE', '')}...")
        print()


async def initialize_config(args):
    config_path = Path.home() / ".zap" / "config.yaml"
    if not config_path.parent.exists():
        config_path.parent.mkdir(parents=True)
    if os.path.exists(config_path) and not args.force:
        print("Config file already exists.")
        return
    with open(config_path, "w") as f:
        config: AppConfig = load_config(args)
        yaml.safe_dump(dataclasses.asdict(config), f)

    print(f"Config file initialized at {config_path}")


async def initialize_templates(args):
    templates_dir = Path(__file__).parent / "templates"
    dest_dir = Path.home() / ".zap" / "templates"
    if dest_dir.exists():
        if not args.force:
            print("Templates directory already exists.")
            return
        else:
            for file in dest_dir.rglob("*"):
                if file.is_file():
                    file.unlink()
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True)
    for file in templates_dir.rglob("*"):
        if file.is_file():
            dest_file = dest_dir / file.relative_to(templates_dir)
            if not dest_file.parent.exists():
                dest_file.parent.mkdir(parents=True)
            async with aiofiles.open(file, "r") as f:
                content = await f.read()
                async with aiofiles.open(dest_file, "w") as f:
                    await f.write(content)

    print(f"Templates directory initialized at {dest_dir}")
    print()
    print("Please make sure to update the templates_dir in the config file.")
    print("You can find the config file at ~/.zap/config.yaml")
    print(
        "If you haven't initialized the config file, you can do so using --init-config"
    )
    print()
    print("Happy Zapping!")
    return


async def main():
    args = parse_arguments()
    set_environment_variables(args)

    if args.init_config:
        await initialize_config(args)
    elif args.init_templates:
        await initialize_templates(args)
    else:
        app = ZapApp()
        await app.initialize(args)

        if args.tasks:
            await app.perform_tasks(args.tasks, args.parallel)
            return

        await app.run()


if __name__ == "__main__":
    asyncio.run(main())
