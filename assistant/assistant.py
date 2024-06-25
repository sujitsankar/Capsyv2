import re
from openai import OpenAI
from . import config
import os

def saveFileOpenAI(location):
    client = OpenAI(api_key=config.API_KEY)
    try:
        with open(location, "rb") as f:
            file = client.files.create(file=f, purpose='assistants')
        return file.id
    finally:
        # Ensure the file is properly closed before attempting to delete it
        if os.path.exists(location):
            try:
                os.remove(location)
            except Exception as e:
                print(f"Error removing file: {e}")

def createVectorStore(file_ids, name):
    client = OpenAI(api_key=config.API_KEY)
    vector_store = client.beta.vector_stores.create(name=name, file_ids=file_ids)
    return vector_store.id

def startAssistantThread(prompt, vector_id):
    messages = [{"role": "user", "content": prompt}]
    client = OpenAI(api_key=config.API_KEY)
    tool_resources = {"file_search": {"vector_store_ids": [vector_id]}}
    thread = client.beta.threads.create(messages=messages, tool_resources=tool_resources)
    return thread.id

def runAssistant(thread_id):
    client = OpenAI(api_key=config.API_KEY)
    assistant_id = config.ASSISTANT_ID
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    return run.id

def checkRunStatus(thread_id, run_id):
    client = OpenAI(api_key=config.API_KEY)
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    return run.status

def retrieveThread(thread_id):
    client = OpenAI(api_key=config.API_KEY)
    thread_messages = client.beta.threads.messages.list(thread_id)
    list_messages = thread_messages.data
    thread_messages = []
    for message in list_messages:
        obj = {}
        obj['content'] = message.content[0].text.value
        obj['role'] = message.role
        obj['timestamp'] = message.created_at  # Include the timestamp
        thread_messages.append(obj)
    return thread_messages[::-1]


def addMessageToThread(thread_id, prompt):
    client = OpenAI(api_key=config.API_KEY)
    thread_message = client.beta.threads.messages.create(thread_id, role="user", content=prompt)

def extract_company_name(content):
    match = re.search(r'\b[A-Z]{3,}\b', content)
    return match.group(0) if match else "Company"

