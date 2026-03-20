import os
import asyncio
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

API_KEY = os.getenv("HINDSIGHT_API_KEY")
BASE_URL = os.getenv("HINDSIGHT_BASE_URL")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID")

def get_client():
    return Hindsight(base_url=BASE_URL, api_key=API_KEY)

def log_attempt(user_id, topic, problem, correct, mistake=None):
    """Store a coding attempt in Hindsight memory."""
    if correct:
        content = f"User {user_id} successfully solved a {topic} problem: '{problem[:80]}'."
    else:
        content = f"User {user_id} attempted a {topic} problem: '{problem[:80]}'. Mistake: {mistake}"
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = get_client()
        loop.run_until_complete(client.aretain(bank_id=BANK_ID, content=content))
        loop.close()
        print(f"[Memory] Logged attempt successfully")
    except Exception as e:
        print(f"[Memory] Log error: {e}")

def get_personalized_context(user_id, question):
    """Use reflect() to reason over user history."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = get_client()
        result = loop.run_until_complete(
            client.areflect(bank_id=BANK_ID, query=f"For user {user_id}: {question}")
        )
        loop.close()
        print(f"[Memory] Reflect successful")
        return result.text
    except Exception as e:
        print(f"[Memory] Reflect error: {e}")
        return "No history yet for this user."

def get_user_history(user_id, question):
    """Recall memories about this user."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = get_client()
        results = loop.run_until_complete(
            client.arecall(bank_id=BANK_ID, query=f"User {user_id}: {question}")
        )
        loop.close()
        memories = [r.text for r in results.results]
        return "\n".join(memories) if memories else "No history yet."
    except Exception as e:
        print(f"[Memory] Recall error: {e}")
        return "No history yet."

def get_learning_profile(user_id):
    """Get full learning profile."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = get_client()
        results = loop.run_until_complete(
            client.arecall(
                bank_id=BANK_ID,
                query=f"All mistakes, weak topics, strengths and history of user {user_id}"
            )
        )
        loop.close()
        print(f"[Memory] Profile loaded: {len(results.results)} memories")
        
        if not results.results:
            return "No learning history yet. Solve some problems to build your profile!"
        
        return "\n".join([f"• {r.text}" for r in results.results])
    except Exception as e:
        print(f"[Memory] Profile error: {e}")
        return f"Could not load profile: {e}"