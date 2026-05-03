# 🧠 MemoryStack: Agentic Interview Prep

**MemoryStack** is a micro-learning platform designed to turn the "Pull" model of interview preparation into a "Push" model. Instead of cramming hundreds of LeetCode problems, MemoryStack uses AI to break down complex Data Structures and System Design topics into a **3-Layer Hierarchy** and pushes them to you via **Telegram** based on spaced repetition.

![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-05998b)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![OpenAI](https://img.shields.io/badge/GPT--4o-Agentic-orange)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Key Features

- **Agentic Micro-Learning**: Don't write notes. Tell the AI a topic (e.g., "Trie" or "Consistent Hashing"), and it generates a structured 3-layer revision card instantly.
- **The 3-Layer Hierarchy**:
    - **Layer 1: The Gist** (High-level mental model)
    - **Layer 2: The Pattern** (The "how" and "why" for interviews)
    - **Layer 3: Top Challenges** (Curated LeetCode/System Design problems)
- **Spaced Repetition (FSRS)**: Uses the Free Spaced Repetition Scheduler algorithm to predict when you are about to forget a topic.
- **Telegram Push Integration**: Revision notes are delivered directly to your phone. No need to visit the website to stay on track.
- **Discovery Handshake**: Secure Deep Linking to connect your web account to your Telegram bot in one click.

---

## 🛠️ The Tech Stack

- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Lucide Icons, Headless UI.
- **Backend**: FastAPI (Python), SQLAlchemy ORM, Pydantic.
- **Database**: PostgreSQL.
- **AI**: OpenAI GPT-4o (Structured Outputs).
- **Architecture**: Strategy Design Pattern for multi-channel notifications (Telegram, Email, etc.).

---

### 🏛️ High-Level System Architecture
![System Architecture](images/MemoryStackArchitecture.png)

The product is divided into five distinct layers, each decoupled to allow for independent scaling and modification.

1. The Interaction Layer (Next.js 14)
   The Dashboard: The "Control Center." It handles state for topic selection and sprint configuration.

The Revision Engine (Sprint Mode): A specialized UI that handles the 3-Layer Disclosure (Gist → Pattern → Questions). This ensures the user doesn't get overwhelmed and focuses on the mental model first.

2. The API & Logic Layer (FastAPI)
   The Orchestrator: Acts as the brain. It coordinates between the database, the AI agent, and the notification manager.

Asynchronous Processing: Uses Python's asyncio and BackgroundTasks to ensure that heavy operations (like calling OpenAI or sending Telegram messages) don't block the user's web experience.

3. The Intelligence Layer (AI Agent & FSRS)
   The Content Agent: This is an agentic workflow. It doesn't just "chat"; it performs Structured Data Extraction. It takes a raw topic and maps it to our proprietary 3-layer schema using GPT-4o.

The FSRS Engine: Implements the Free Spaced Repetition Scheduler. It processes user "Recall Ratings" (1-4) to calculate the Stability and Difficulty of a memory, determining the exact timestamp for the next "Push."

4. The Persistence Layer (PostgreSQL)
   Relational Mapping: Stores the atomic notes, user progress, and the FSRS states. We use PostgreSQL because memory tracking requires transactional integrity (we can't lose a user's revision history).

5. The Delivery Layer (Strategy-Pattern Gateway)
   Decoupled Broadcasting: This is where the Telegram integration sits. By using the Strategy Pattern, the application treats "Delivery" as a black box. The core logic doesn't know it's Telegram; it just knows it's sending a RevisionPayload to a RegisteredProvider.

### 🔄 The Data Journey (The Flow)
To understand how the product works, follow a single topic (e.g., "Trie"):

Ingestion: User enters "Trie" on the Dashboard.

Synthesis: The API triggers the AI Agent. The Agent researches the topic and returns a JSON object containing the Gist, Pattern, and LeetCode questions.

Storage: The topic is saved to the atomic_notes table.

Planning: User sets a "Sprint" for 2 days. The FSRS Engine creates a schedule.

Broadcast: On the scheduled time, a Background Task wakes up, pulls the 3-Layer content, and hands it to the Notification Manager.

Delivery: The Manager pushes the "Gist" and "Pattern" to the user's Telegram.

Closure: User reviews the note on their phone, clicks back to the web to rate their recall, and the loop starts again with an updated "Stability" score.

### 🎯 Why This Architecture?
Decoupled Discovery: The Telegram "Handshake" (Webhook) is handled by a separate router, meaning you could swap Telegram for a native mobile app later without changing the AI or Database.

Schema-Driven Intelligence: By enforcing Structured Outputs from the AI, we ensure the UI never breaks due to "AI hallucinations."

Open-Closed Design: We can add new "Push" channels (Email, WhatsApp, Slack) by simply adding a new strategy class, fulfilling the Open-Closed Principle.

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- [ngrok](https://ngrok.com/) (for local Telegram webhook testing)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Create a .env file in the backend/ directory:

Plaintext
DATABASE_URL=postgresql://user:password@localhost:5432/memorystack
OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TEST_TELEGRAM_CHAT_ID=your_id
```

### 3. Frontend Setup
```bash
cd frontend
npm install
Create a .env.local file in the frontend/ directory:

Plaintext
NEXT_PUBLIC_API_URL=http://localhost:8000
4. Database Initialization
Make sure your PostgreSQL server is running, then start the backend. SQLAlchemy will automatically create the tables:

npm run dev
```

### 3. Telegram Webhook Setup
```bash
# 1. Start your local server
uvicorn app.main:app --reload

# 2. Expose with ngrok
ngrok http 8000

# 3. Register the webhook with Telegram
# Visit: [https://api.telegram.org/bot](https://api.telegram.org/bot)<TOKEN>/setWebhook?url=<NGROK_URL>/telegram-webhook
# Click Connect Telegram on the MemoryStack Dashboard.
```

### 📝 License
Copyright (c) 2026 Abhishek Sharma.
This project is licensed under the MIT License - see the LICENSE file for details.