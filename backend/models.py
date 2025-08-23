from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(alias="query")   # user query


class AskResponse(BaseModel):
    answer: str
    sources: list[str]      # titles of the docs that were used