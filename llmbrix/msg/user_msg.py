import PIL.Image
from google.genai import Client, types

from llmbrix.msg.user_msg_file_types import UserMsgFileTypes

FILE_LIMIT = 5
USER_ROLE_NAME = "user"


class UserMsg(types.Content):
    """
    Message from user.
    Can optionally contain additional attachments (e.g. image, sound, etc.).
    """

    def __init__(
        self,
        text: str,
        images: list[PIL.Image.Image] | None = None,
        files: list[tuple[bytes, UserMsgFileTypes]] | None = None,
        youtube_url: str | None = None,
        gcs_uris: list[tuple[str, UserMsgFileTypes]] | None = None,
    ):
        """
        Text has to be filled.
        Other params serve to pass optional attachments that can be sent to the LLM.
        Parts for message sent to the LLM are ordered in following way:
            - YouTube video
            - images
            - URI-read files
            - files passed as bytes
            - text
        => First large attachments are mentioned and then text instructions how to handle them are presented to the LLM.

        Args:
            text: str text message from User.
            images: Image attachments loaded into PIL. Maximum 5 images are supported.
            files: list of Tuple (bytes, modality). Note files are supported only up to 20MB limit.
            youtube_url: URL of YouTube video
            gcs_uris: Tuple (URI, modality)
                      URI for content from GCS bucket, e.g. tuple (gs://bucket/file.pdf, Modality.PDF).
        """
        images = images or []
        files = files or []
        gcs_uris = gcs_uris or []
        n_attachments = len(images) + len(files) + len(gcs_uris) + (1 if youtube_url else 0)
        if n_attachments > FILE_LIMIT:
            raise ValueError(f"Maximum {FILE_LIMIT} file attachments allowed. {n_attachments} attachments received.")
        parts = []
        if youtube_url:
            parts.append(types.Part.from_uri(file_uri=youtube_url, mime_type="video/youtube"))
        for img in images:
            parts.append(types.Part.from_image(img))
        for uri, modality in gcs_uris:
            parts.append(types.Part.from_uri(file_uri=uri, mime_type=modality.value))
        for file_bytes, modality in files:
            parts.append(types.Part.from_bytes(data=file_bytes, mime_type=modality.value))
        parts.append(types.Part.from_text(text=text))
        super().__init__(role=USER_ROLE_NAME, parts=parts)

    def count_tokens(self, client: Client, model: str, config: types.CountTokensConfigOrDict | None = None) -> int:
        """
        Compute exact number of tokens this message will produce on input in Gemini API,
        including hidden framing tokens.

        Args:
            client: Gemini client instance from SDK.
            model: ID of Gemini model. E.g. "gemini-2.0-flash"
            config: CountTokensConfigOrDict object

        Returns: int number of tokens this message will produce on input.

        """
        response = client.models.count_tokens(model=model, contents=[self], config=config)
        return response.total_tokens
