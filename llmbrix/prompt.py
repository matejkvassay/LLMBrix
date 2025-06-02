from jinja2 import Environment, StrictUndefined, Undefined, meta

from llmbrix.exceptions import PromptRenderError


class Prompt:
    """
    Prompt in form of Jinja template.
    Enables rendering and partial rendering of variables.
    Rendering is strict in order to avoid human errors:
    - for render() include precisely all vars, no extra vars allowed, no missing vars allowed
    - for partial_render() include subset of vars, no extra vars allowed
    """

    def __init__(self, template_str: str):
        """
        :param template_str: str, Jinja2-compatible template string.
        """
        self.strict_env = Environment(undefined=StrictUndefined)
        self.relaxed_env = Environment(undefined=_PreserveUndefined)
        self.template_str = template_str
        self.template = self.strict_env.from_string(template_str)
        self._undeclared = meta.find_undeclared_variables(self.strict_env.parse(template_str))

    def render(self, kwargs: dict) -> str:
        """
        Fully render the prompt.
        All required variables must be provided.
        Extra variables are not allowed.

        :param kwargs: Dictionary of variables to insert into the prompt template.

        :raises PromptRenderError: If required variables are missing or extra variables were passed.
        :raises jinja2.exceptions.UndefinedError: If template evaluation fails.

        :return: str, Fully rendered template.
        """
        missing = self._undeclared - kwargs.keys()
        extra = kwargs.keys() - self._undeclared

        if missing:
            raise PromptRenderError(f"Missing required variables: {sorted(missing)}")
        if extra:
            raise PromptRenderError(f"Unexpected variables: {sorted(extra)}")

        return self.template.render(**kwargs)

    def partial_render(self, kwargs: dict) -> "Prompt":
        """
        Partially render the prompt with a subset of declared variables.
        Extra variables are not allowed.
        Returns a new Prompt instance with the partially rendered template string.

        :param kwargs: Subset of variables to render.

        :raises PromptRenderError: If extra variables are passed.
        :raises jinja2.exceptions.UndefinedError: If rendering with partial data fails
                                                  (e.g. in logic).

        :return: Prompt, New Prompt with updated template.
        """
        extra = kwargs.keys() - self._undeclared
        if extra:
            raise PromptRenderError(f"Unexpected variables: {sorted(extra)}")

        new_template_str = self.relaxed_env.from_string(self.template_str).render(**kwargs)
        return Prompt(template_str=new_template_str)

    def __str__(self):
        return self.template_str


class _PreserveUndefined(Undefined):
    """
    Custom Jinja undefined handler.
    Leaves {{ variable }} in output instead of replacing it with an empty string.
    """

    def __str__(self):
        return f"{{{{ {self._undefined_name} }}}}"
