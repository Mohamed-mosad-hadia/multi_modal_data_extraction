import json
import random
import sqlite3
from pathlib import Path
import logging
import argparse
from datetime import datetime


# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("create_conversations_db")


# === 1. Load Q&A pairs from SQLite ===
def load_qa_pairs_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, question, answer, source_document, page_number, category
        FROM qa_pairs
        WHERE category IN ('symptoms', 'definition', 'treatment', 'cause')
    """
    )

    rows = cur.fetchall()
    conn.close()

    qa_pairs = [
        {
            "id": r[0],
            "question": r[1],
            "answer": r[2],
            "source_document": r[3],
            "page_number": r[4],
            "category": r[5],
        }
        for r in rows
    ]

    logger.info(f"📘 Loaded {len(qa_pairs)} QA pairs from database")
    return qa_pairs


# === 2. Build conversations ===
def build_conversations(qa_pairs, num_conversations=10):
    conversations = []
    used_qas = set()

    for conv_id in range(1, num_conversations + 1):
        available_qas = [qa for qa in qa_pairs if qa["id"] not in used_qas]
        if len(available_qas) < 3:
            break

        convo = {
            "conversation_id": f"conv_{conv_id:03d}",
            "topic": "Medical Consultation",
            "created_at": datetime.now().isoformat(),
            "turns": [],
        }

        k = min(len(available_qas), random.randint(3, 5))
        selected_qas = random.sample(available_qas, k=k)

        turn_id = 1
        for qa in selected_qas:
            used_qas.add(qa["id"])

            convo["turns"].append(
                {
                    "turn_id": turn_id,
                    "speaker": "patient",
                    "text": simulate_patient_question(qa["question"]),
                }
            )
            turn_id += 1

            convo["turns"].append(
                {
                    "turn_id": turn_id,
                    "speaker": "doctor",
                    "text": simulate_doctor_answer(qa["answer"]),
                    "source_reference": f"{qa['source_document']}:p{qa['page_number']}",
                }
            )
            turn_id += 1

        conversations.append(convo)

    logger.info(f"💬 Generated {len(conversations)} conversations")
    return conversations


# === 3. Simulate Q&A dialog ===
def simulate_patient_question(original_q):
    lower_q = original_q.lower()
    if "what are the symptoms" in lower_q:
        return "I've been feeling unwell lately. Could these be symptoms of something serious?"
    elif "how is" in lower_q:
        return "How can this condition be treated?"
    elif "what causes" in lower_q:
        return "Do we know what causes this condition?"
    elif "what is" in lower_q:
        return "Can you explain what this disease is?"
    return "I have some concerns about my health. Can you help explain?"


def simulate_doctor_answer(answer):
    return f"Based on your description, {answer.lower().strip('.')}."


# === 4. Save conversations to SQLite ===
def save_conversations_to_db(db_path, conversations):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            topic TEXT,
            created_at TEXT,
            content TEXT
        )
    """
    )

    for convo in conversations:
        content_json = json.dumps(convo, ensure_ascii=False, indent=2)
        cur.execute(
            """
            INSERT OR REPLACE INTO conversations (conversation_id, topic, created_at, content)
            VALUES (?, ?, ?, ?)
        """,
            (
                convo["conversation_id"],
                convo["topic"],
                convo["created_at"],
                content_json,
            ),
        )

    conn.commit()
    conn.close()
    logger.info(f"✅ Saved {len(conversations)} conversations to database: {db_path}")


# === 5. Main flow ===
def main():
    parser = argparse.ArgumentParser(
        description="Generate simulated medical conversations from QA pairs (SQLite version)."
    )
    parser.add_argument(
        "--db",
        type=str,
        default="outputs/qa_data.db",
        help="Path to SQLite database file",
    )
    parser.add_argument(
        "--num_conversations",
        type=int,
        default=10,
        help="Number of conversations to generate",
    )
    args = parser.parse_args()

    db_path = Path(args.db)

    logger.info("🚀 Starting conversation generation pipeline...")
    qa_pairs = load_qa_pairs_from_db(db_path)
    conversations = build_conversations(
        qa_pairs, num_conversations=args.num_conversations
    )
    save_conversations_to_db(db_path, conversations)
    logger.info("🏁 Conversation generation completed successfully!")


if __name__ == "__main__":
    main()
