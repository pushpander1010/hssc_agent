from typing import Annotated,Optional,Literal
from pydantic import BaseModel,Field

MODEL="google|gemini-2.5-flash"

class Question(BaseModel):
    question:Optional[str]=Field(default=None,description="Question generated based on topic")
    answer:Optional[str]=Field(default=None,description="Answer to the generated question based on topic")
    options:Optional[list[str]]=Field(default=None,description="Four Options for the question one of which is the correct answer")
    source:Optional[str]=Field(default="AI generated",description="Source of the generated question based on topic")

class Questions(BaseModel):
    questions:Optional[list[Question]]=Field(default=None,description="questions generated on the topic")

class ModelState(BaseModel):
    topic: Optional[str] = Field(default="hssc cet haryana gk static", description="topic for which we want questons generated")
    level: Optional[Literal["mains", "prelims", "easy", "medium", "hard"]] = Field(default="mains", description="difficulty level")
    model: Optional[str] = Field(default="google|gemini-2.5-flash", description="model used to generate questions")  # <== ADD THIS
    questions: Optional[Questions] = Field(default=None, description="questions generated on the topic")
