# rag.py

import time
from openai import OpenAI
import minsearch
import ingest
import json
import os
from dotenv import load_dotenv


load_dotenv()
api_key=os.getenv('OPENAI_API_KEY')


# Initialize the OpenAI client  
#client = OpenAI(api_key=api_key)
client = OpenAI()


index = ingest.load_index()

def search(query):
    boost = {
    'Questions': 0.20303988721391708,
    'Answers': 1.5766410134276012

    }
    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )
    return results

def build_prompt(query, search_results):
   prompt_template = """
    You're a mental health psychiatrist. Answer the QUESTION based on the CONTEXT from our mental questions and answer database.
    Use only the facts from the CONTEXT when answering the QUESTION.
    
    QUESTION: {question}
    
    CONTEXT:
    {context}
    """.strip()
    
   entry_template = """
    ANSWER: {Answers}
    """.strip()
   context = ""
    
   for doc in search_results:
        context = context + entry_template.format(**doc) + "\n\n"

   prompt = prompt_template.format(question=query, context=context).strip()
   
   return prompt

def llm(prompt, model='gpt-4o-mini'):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def rag(query, model='gpt-4o-mini'):
    # Check if the user is asking who created the bot
    if query.lower() in ["who created you?", "who is your creator?", "who made you?"]:
        return "I was created by W Mohamed."

    # Otherwise, proceed with normal search and LLM response
    search_results = search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt, model=model)
    #time.sleep(1)  # Simulating a delay for the function to work
    return answer
    
