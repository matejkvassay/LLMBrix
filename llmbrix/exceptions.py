class PromptRenderError(Exception):
    """
    Raised when render or partial_render receives invalid or mismatched variables.
    """


class OpenAIResponseError(Exception):
    """
    Raised when OpenAI API call fails and returns error field instead of a response.
    """
