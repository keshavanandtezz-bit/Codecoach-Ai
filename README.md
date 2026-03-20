\# CodeCoach AI 🧠

\### An AI coding mentor that never forgets your mistakes



CodeCoach is a personalized coding practice platform that uses \*\*Hindsight memory\*\* to remember every mistake you make, detect your weak topics, and generate problems specifically targeting your gaps — across every session.



> Built for the Hindsight Hackathon 2026



\---



\## The Problem

Normal coding platforms forget you the moment you close the tab. Every session starts from zero — no memory of what you struggled with, no personalization, no growth tracking.



\## The Solution

CodeCoach uses \*\*Hindsight\*\* to give every student a persistent memory bank. The AI remembers:

\- Every problem you attempted

\- Every mistake you made and why

\- Which topics you struggle with

\- Your improvement over time



\---



\## How Hindsight Memory is Used



This is the core of CodeCoach — three Hindsight operations power everything:



\### 1. `retain()` — After every attempt

Every time a student submits code, the result is stored in Hindsight:

```python

client.retain(

&#x20;   bank\_id=BANK\_ID,

&#x20;   content="User keshav attempted a recursion problem. 

&#x20;            Mistake: missing base case, syntax error in function definition."

)

```



\### 2. `reflect()` — Before generating a problem

Before creating a new problem, CodeCoach asks Hindsight to reason over the student's full history:

```python

result = client.reflect(

&#x20;   bank\_id=BANK\_ID,

&#x20;   query="For user keshav: what topics does this student struggle with?"

)

\# Returns: "Keshav struggles with recursion base cases and function syntax"

```

This result is passed to the AI which then generates a targeted problem.



\### 3. `recall()` — For the Learning Profile

The "My Learning Profile" button retrieves everything Hindsight knows about the student:

```python

results = client.recall(

&#x20;   bank\_id=BANK\_ID,

&#x20;   query="All mistakes, weak topics and history of user keshav"

)

```



\---



\## Architecture

```

User Browser

&#x20;    │

&#x20;    ▼

app.py (Flask web server)

&#x20;    │

&#x20;    ├──▶ mentor.py (Groq AI)

&#x20;    │         │

&#x20;    │         └──▶ memory.py (Hindsight)

&#x20;    │                   │

&#x20;    │                   └──▶ Hindsight Cloud

&#x20;    │                        retain / recall / reflect

&#x20;    │

&#x20;    └──▶ Returns personalized problem, hint, or feedback

```



\---



\## Tech Stack



| Component | Technology |

|---|---|

| Memory System | Hindsight by Vectorize |

| AI / LLM | Groq — qwen/qwen3-32b |

| Backend | Python + Flask |

| Frontend | HTML + CSS + JavaScript |



\---



\## Features



\- \*\*Personalized problems\*\* — generated based on your weak areas

\- \*\*Memory-aware hints\*\* — references your past mistake patterns

\- \*\*Smart evaluation\*\* — AI grades your code with specific feedback

\- \*\*Learning profile\*\* — shows everything Hindsight remembers about you

\- \*\*Persistent memory\*\* — works across sessions, gets smarter every time



\---



\## Setup \& Run Locally



\### 1. Clone the repo

```bash

git clone https://github.com/keshavanandtezz-bit/Codecoach-Ai.git

cd Codecoach-Ai

```



\### 2. Create virtual environment

```bash

python -m venv venv

venv\\Scripts\\activate  # Windows

```



\### 3. Install dependencies

```bash

pip install hindsight-client groq python-dotenv flask requests

```



\### 4. Create .env file

```

HINDSIGHT\_API\_KEY=your\_hindsight\_key

HINDSIGHT\_BANK\_ID=codecoach

HINDSIGHT\_BASE\_URL=https://api.hindsight.vectorize.io

GROQ\_API\_KEY=your\_groq\_key

```



\### 5. Run

```bash

python app.py

```



Open http://localhost:5000



\---



\## Demo



\[Watch Demo Video](#) | \[Live Demo](#)



\---



\## How Memory Makes It Different



| Without Hindsight | With Hindsight |

|---|---|

| Same random problems every session | Problems target your specific weak areas |

| Generic hints | Hints reference your past mistakes |

| No progress tracking | Full learning profile built over time |

| Forgets you instantly | Remembers you forever |



\---



\## Team

Built by Keshav for the Hindsight Hackathon 2026

