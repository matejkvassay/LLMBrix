class Prompt:
    def __init__(self, template: str):
        self.template = template

    def render(self, vars: dict):
        raise NotImplementedError

    def partial_render(self, vars: dict) -> "Prompt":
        raise NotImplementedError
