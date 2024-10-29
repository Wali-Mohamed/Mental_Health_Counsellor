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
    start_time = time.time()
        
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content
    tokens = {
        'prompt_tokens': response.usage.prompt_tokens,
        'completion_tokens': response.usage.completion_tokens,
        'total_tokens': response.usage.total_tokens
    }


    end_time = time.time()
    response_time = end_time - start_time
        
    return answer, tokens, response_time
def calculate_openai_cost(model_choice, tokens):
    openai_cost = 0

    if model_choice == 'gpt-3.5-turbo':
        openai_cost = (tokens['prompt_tokens'] * 0.003 + tokens['completion_tokens'] * 0.006) / 1000
    elif model_choice in ['gpt-4o-mini']:
        openai_cost = (tokens['prompt_tokens'] * 0.00015 + tokens['completion_tokens'] * 0.0006) / 1000

    return openai_cost
def evaluate_relevance(question, answer):
    prompt_template = """
    You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
    Your task is to analyze the relevance of the generated answer to the given question.
    Based on the relevance of the generated answer, you will classify it
    as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

    Here is the data for evaluation:

    Question: {question}
    Generated Answer: {answer}

    Please analyze the content and context of the generated answer in relation to the question
    and provide your evaluation in parsable JSON without using code blocks:

    {{
      "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
      "Explanation": "[Provide a brief explanation for your evaluation]"
    }}
    """.strip()

    prompt = prompt_template.format(question=question, answer=answer)
    evaluation, tokens, _ = llm(prompt, 'gpt-4o-mini')
    
    try:
        json_eval = json.loads(evaluation)
        return json_eval['Relevance'], json_eval['Explanation'], tokens
    except json.JSONDecodeError:
        return "UNKNOWN", "Failed to parse evaluation", tokens
def get_answer(query, model_choice='gpt-4o-mini'):
    
    search_results = search(query)

    prompt = build_prompt(query, search_results)
    answer, tokens, response_time = llm(prompt, model=model_choice)
    
    relevance, explanation, eval_tokens = evaluate_relevance(query, answer)

    prompt_openai_cost = calculate_openai_cost(model_choice, tokens)
    eval_openai_cost = calculate_openai_cost(model_choice, eval_tokens)
 
    return {
        'answer': answer,
        'response_time': round(response_time,3),
        'relevance': relevance,
        'relevance_explanation': explanation,
        'model_used': model_choice,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
        'prompt_openai_cost': round(prompt_openai_cost,4),
        'eval_openai_cost': round(eval_openai_cost,4)
    }
    
