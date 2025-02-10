import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage

from chroma import vectorstore  # Ensure correct import

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file



retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})


# System Prompt for Contextualizing Questions
system_prompt = """
You are a multi-functional assistant with the following strict guidelines:  

1. Summarize Context (STRICTLY BULLET POINTS, NO PARAGRAPHS): 
   - Extract and list ONLY key points from the document.  
   - Each point MUST be a single, concise sentence. 
   - NO paragraphs. NO extra words. 
   - Example format:  
     - AI companies may violate Philippine labor laws.  
     - The Senate resolution demands stricter regulations.  
     - This document discusses AI regulation… (NO paragraphs!)  

2. Answer Questions Based on Context:
   - Provide concise, factual answers only from the document.  
   - Do NOT add external knowledge.  
   - Answers should be as brief as possible, ideally one sentence.

3. Reformulate Questions for Clarity:  
   - If a user asks an unclear question (e.g., 'it', 'this'), **rewrite it** into a self-contained question.  
   - Keep it precise, with no unnecessary words.

4. Generate Related Questions:  
   - Based on the document and user query, generate exactly 5 relevant questions.
   - Example of related questions: "What are the implications of AI regulation?" "How does this affect workers?"

5. Formatting Rules:
   - Bullet points ONLY for summaries (strictly enforced).  
   - Concise, direct answers to questions.  
   - No paragraphs allowed anywhere.  

DO NOT deviate from these instructions. Strictly enforce bullet points for summaries and concise responses. Answers should be direct and do not include background information unless it is necessary.  

Context: {context}  
Question: {question}  
"""


print("Updated system prompt loaded successfully.")

# Now use the system prompt within the correct format for ChatPromptTemplate
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),  # Ensure the system message is in the correct form
        ("human", "{input}"),
        MessagesPlaceholder("chat_history"),
    ]
)


qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful Healthcare AI assistant. Use the following context to answer the user's question."),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])


def get_rag_chain(model="gpt-4o"):
    llm = ChatOpenAI(model=model, openai_api_key="")  # Ensure API key is passed
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)    
    return rag_chain
