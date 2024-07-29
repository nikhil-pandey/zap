from functools import wraps


class CommandRegistry:
    def __init__(self):
        self.commands = {}

    def command(self, name, aliases=None, description="", show=True):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            self.register("/" + name, wrapper, description, show)
            if aliases:
                for alias in aliases:
                    prefix = "/" if alias != "!" else ""
                    self.register(prefix + alias, wrapper, f"Alias for {name}", False)
            return wrapper

        return decorator

    def register(self, name, func, description, show=True):
        self.commands[name] = {"func": func, "description": description, "show": show}

    def get(self, name):
        return self.commands.get(name, {}).get("func")

    def starts_with_command(self, text):
        split_text = text.split(" ")
        if not split_text:
            return False
        return self.is_command(split_text[0])

    def is_command(self, name):
        return name in self.commands or '/' + name in self.commands

    def get_all_commands(self, show_hidden=False):
        return [
            {"Command": command, "Description": self.commands[command]["description"]}
            for command in self.commands
            if show_hidden or self.commands[command]["show"]
        ]
