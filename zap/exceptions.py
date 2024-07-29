class ZapException(Exception):
    pass


class AgentNotFoundError(ZapException):
    pass


class ContextNotFoundError(ZapException):
    pass


class ToolExecutionError(ZapException):
    pass
