import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from memory import log_attempt, get_personalized_context

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_problem(user_id):
    """Generate a coding problem personalized to this user's weak areas."""
    
    history = get_personalized_context(
        user_id,
        "What topics does this user struggle with? What difficulty level suits them right now?"
    )
    
    prompt = f"""You are CodeCoach, an AI coding mentor.

This student's learning history:
{history}

Based on their history, generate ONE personalized coding problem.
If they have no history, start with an easy beginner problem.

Respond with ONLY a JSON object like this, nothing else:
{{
    "title": "Short problem title",
    "description": "Full problem description with example input/output",
    "topic": "the programming topic (e.g. loops, recursion, arrays)",
    "difficulty": "easy or medium or hard",
    "hint": "A small hint if they get stuck"
}}"""

    response = groq_client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    raw = response.choices[0].message.content
    
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    
    return {
        "title": "FizzBuzz",
        "description": "Print numbers 1 to 20. For multiples of 3 print Fizz, for multiples of 5 print Buzz, for both print FizzBuzz.",
        "topic": "loops",
        "difficulty": "easy",
        "hint": "Use the modulo operator %"
    }

def give_hint(user_id, problem, user_code):
    """Give a personalized hint based on user's past mistakes."""
    
    history = get_personalized_context(
        user_id,
        f"What mistakes has this user made before that might relate to this problem: {problem[:100]}"
    )
    
    prompt = f"""You are CodeCoach, a kind and encouraging coding mentor.

Student's past mistake patterns:
{history}

Current problem:
{problem}

Student's current code:
{user_code if user_code.strip() else "No code written yet"}

Give a helpful, encouraging hint. 
- If they have made similar mistakes before, gently reference that pattern
- Do NOT give away the full solution
- Keep it under 3 sentences
- Be warm and encouraging"""

    response = groq_client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def evaluate_solution(user_id, topic, problem, user_code):
    """Evaluate submitted code and log the result to Hindsight memory."""
    
    prompt = f"""You are CodeCoach evaluating a student's code submission.

Problem:
{problem}

Student's code:
{user_code}

Evaluate their solution. Respond with ONLY a JSON object like this, nothing else:
{{
    "correct": true or false,
    "feedback": "Detailed feedback explaining what they did right or wrong",
    "mistake": "If wrong, describe the specific mistake in one sentence. If correct, write null"
}}"""

    response = groq_client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    raw = response.choices[0].message.content
    
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            log_attempt(
                user_id=user_id,
                topic=topic,
                problem=problem[:100],
                correct=result.get("correct", False),
                mistake=result.get("mistake")
            )
            return result
        except:
            pass
    
    return {
        "correct": False,
        "feedback": "Could not evaluate. Please try again.",
        "mistake": "evaluation error"
    }