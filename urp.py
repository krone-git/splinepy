from pathlib import Path


class URPCommand:
    pass


class URPCompiler:
    pass


class URPBuilder:
    def __init__(self):
        self._commands = []

    def add_command(self, command, *args, **kwargs): raise NotImplementedError

    def __iadd__(self, command): self.add_command()

    def __enter__(self): return self
    def __exit__(self): pass


class URPEncoder:
    pass