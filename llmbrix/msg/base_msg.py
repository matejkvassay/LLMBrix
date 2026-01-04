from google.genai import Client, types


class BaseMsg(types.Content):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_user(self):
        return self.role == "user"

    def is_model(self):
        return self.role == "model"

    def is_tool(self):
        return self.role == "function"

    def count_tokens(self, client: Client, model_name: str, config: types.CountTokensConfigOrDict | None = None) -> int:
        """
        Compute exact number of tokens this message will produce on input in Gemini API,
        including hidden framing tokens.

        Args:
            client: Gemini client instance from SDK.
            model_name: Name of Gemini model. E.g. "gemini-2.0-flash"
            config: CountTokensConfigOrDict object

        Returns: int number of tokens this message will produce on input.

        """
        response = client.models.count_tokens(model=model_name, contents=[self], config=config)
        return response.total_tokens
