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
    """Use reflect() to reason over THIS user's history only."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = get_client()
        result = loop.run_until_complete(
            client.areflect(
                bank_id=BANK_ID,
                query=f"Specifically for user {user_id} only (ignore other users): {question}"
            )
        )
        loop.close()
        print(f"[Memory] Reflect successful for {user_id}")
        return result.text
    except Exception as e:
        print(f"[Memory] Reflect error: {e}")
        return f"No history yet for {user_id}."

def get_user_history(user_id, question):
    """Recall memories about this specific user only."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = get_client()
        results = loop.run_until_complete(
            client.arecall(
                bank_id=BANK_ID,
                query=f"user {user_id}: {question}"
            )
        )
        loop.close()
        
        # Filter to only this user's memories
        memories = []
        for r in results.results:
            if user_id.lower() in r.text.lower():
                memories.append(r.text)
        
        return "\n".join(memories) if memories else "No history yet."
    except Exception as e:
        print(f"[Memory] Recall error: {e}")
        return "No history yet."
def get_learning_profile(user_id):
    """Get full learning profile for a specific user only."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = get_client()
        
        # Search specifically for this user only
        results = loop.run_until_complete(
            client.arecall(
                bank_id=BANK_ID,
                query=f"mistakes and history of user {user_id}"
            )
        )
        loop.close()
        print(f"[Memory] Profile loaded: {len(results.results)} memories")
        
        if not results.results:
            return f"No learning history yet for {user_id}. Solve some problems to build your profile!"
        
        # Filter results to only show this specific user's memories
        user_memories = []
        for r in results.results:
            text = r.text.lower()
            if user_id.lower() in text:
                user_memories.append(f"• {r.text}")
        
        if not user_memories:
            return f"No learning history yet for {user_id}. Solve some problems to build your profile!"
        
        return "\n".join(user_memories)
        
    except Exception as e:
        print(f"[Memory] Profile error: {e}")
        return f"Could not load profile: {e}"