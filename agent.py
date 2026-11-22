
import os

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from tool import web_search, web_scrapper

load_dotenv()


# Gemini API Configuration
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)


# SEARCH AGENT
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )


# READER AGENT
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[web_scrapper]
    )


# WRITER AGENT
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that can search the web
    and scrape content from websites. Use the tools provided to gather
    information and provide accurate responses."""),

    ("human", """Write a detailed research report on the topic:
    Artificial Intelligence in Healthcare.

    Topic: {topic}
    Research Gathered: {research}

    Structure the report with:
    - Introduction
    - Key Findings (3-5 points)
    - Conclusion
    - Sources (with links to original documents)

    Be detailed, factual and professional.""")
])

writer_chain = writer_prompt | llm | StrOutputParser()


# CRITIC AGENT
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a web content critic.
    Evaluate the quality and reliability of the content.
    Be honest and specific."""),

    ("human", """Review the research report below and evaluate it strictly.

    Report: {report}

    Respond in this exact format:

    Score: X/10

    Strengths:
    - ...

    Areas to improve:
    - ...

    One line verdict:
    ...""")
])

critic_chain = critic_prompt | llm | StrOutputParser()
