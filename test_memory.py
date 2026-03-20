import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

api_key = os.getenv("HINDSIGHT_API_KEY")
base_url = os.getenv("HINDSIGHT_BASE_URL")
bank_id = os.getenv("HINDSIGHT_BANK_ID")

print("API Key loaded:", api_key[:10] if api_key else "NOT FOUND")
print("Bank ID loaded:", bank_id if bank_id else "NOT FOUND")

client = Hindsight(
    base_url=base_url,
    api_key=api_key
)

print("\nStep 1: Storing a memory in Hindsight...")
client.retain(
    bank_id=bank_id,
    content="User keshav attempted a recursion problem in Python and made a mistake. He forgot the base case and got infinite recursion."
)
print("Memory stored successfully!")

print("\nStep 2: Recalling the memory...")
results = client.recall(
    bank_id=bank_id,
    query="What mistakes has keshav made?"
)

print("Recall result:")
for r in results.results:
    print("-", r.text)