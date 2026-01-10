import dotenv
from pydantic import BaseModel, Field

from llmbrix.gemini_model import GeminiModel
from llmbrix.msg import UserMsg

dotenv.load_dotenv()

REVIEWS = [
    (
        "This movie was total disaster in box office but I loved it. "
        "Mostly the visual effects and sounds, I'm very simple viewer. "
        "The ending was disappointing though, "
        "I wish all characters would end better, but what can you do."
    ),
    "Not very nice, I didnt like the music neither actors, story quite shallow. Action scenes where great though.",
    "Idk it was kinda meh.",
    "GOAT, what can I say, everyone loves Titanic, so romantic and Leonardo is an added bonus.",
]

model = GeminiModel(model="gemini-2.5-flash-lite")


class MovieClassification(BaseModel):
    is_positive: bool
    reasoning: str = Field(
        description="Make it a list of reasons with super brief sentences. "
        "Use bullet points: '+' for positive and '-' for negative aspects."
    )
    confidence: int = Field(
        ge=1,
        le=10,
        description="Confidence score from 1 to 10 indicating how certain the model is about the classification.",
    )


def classify_review(model, review_content):
    response = model.generate(
        system_instruction="Classify if movie review from a viewer is positive or negative",
        messages=[UserMsg(review_content)],
        response_schema=MovieClassification,
    )
    print(f'Predicted class: {"POSITIVE" if response.parsed.is_positive else "NEGATIVE"}')
    print(response.parsed.reasoning)
    print(f"CONFIDENCE (1-10): {response.parsed.confidence}")


for review in REVIEWS:
    print("\n\n___________________________________\n\nREVIEW:", review)
    classify_review(model, review)
