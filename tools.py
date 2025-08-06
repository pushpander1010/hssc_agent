from langchain_google_genai import GoogleGenerativeAI
from langchain_perplexity import ChatPerplexity
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from models import ModelState,Questions,MODEL
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser,PydanticOutputParser

load_dotenv()

model=GoogleGenerativeAI(temperature=1.8,model="gemini-2.5-pro")

def question_setter(state: ModelState):
    if state.model is None:
        raise ValueError("Model not specified in state.")

    provider, model_name = state.model.split("|")
    
    if provider == "google":
        model = GoogleGenerativeAI(temperature=0.3, model=model_name)
    elif provider == "perplexity":
        model = ChatPerplexity(temperature=0.3, model=model_name)
    elif provider == "groq":
        model = ChatGroq(temperature=0.3, model=model_name)
    else:
        raise ValueError("Unsupported model provider.")
    parser = PydanticOutputParser(pydantic_object=Questions)
    
    prompt = PromptTemplate(
        template="""You are an expert paper setter and you excel at making questions for competitive exams.\n
        For the given topic: {topic}, generate 10 questions. Level: {level}.\n
        *Instructions for generating questions*\n
        1. Each question must have 4 options, one of which is correct.\n
        2. Prefer previous year questions from real exams.\n
        3. Question-answer pairs must be accurate.\n
        4. For GK, questions must be current.\n
        5. Exactly 10 questions.

        Return the output in this format:\n{format}""",
        input_variables=["topic", "level"],
        partial_variables={"format": parser.get_format_instructions()}
    )
    
    chain = prompt | model | parser
    return chain.invoke({"topic": state.topic, "level": state.level})
