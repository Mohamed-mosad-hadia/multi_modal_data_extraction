import json
import random
from pathlib import Path


def load_qa_pairs(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)["qa_pairs"]


def build_conversations(qa_pairs, num_conversations=10):
    conversations = []
    used_qas = set()
    qa_pool = [
        qa
        for qa in qa_pairs
        if qa["category"] in ("symptoms", "definition", "treatment", "cause")
    ]

    for conv_id in range(1, num_conversations + 1):
        available_qas = [qa for qa in qa_pool if qa["id"] not in used_qas]
        if len(available_qas) < 3:
            break

        convo = {
            "conversation_id": f"conv_{conv_id:03d}",
            "topic": "Cholera Case Discussion",
            "turns": [],
        }

        turn_id = 1
        k = min(len(available_qas), random.randint(3, 5))
        selected_qas = random.sample(available_qas, k=k)

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

    return {"conversations": conversations}


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


def save_conversations(convo_data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(convo_data, f, ensure_ascii=False, indent=2)
    print(f"[✓] Saved conversations to {output_path}")


def main():
    input_path = Path(r"D:\Data_Engineer_Task\task1_multimodal\outputs\qa_pairs.json")
    output_path = Path(
        r"D:\Data_Engineer_Task\task1_multimodal\outputs\conversations.json"
    )

    qa_pairs = load_qa_pairs(input_path)
    conversations = build_conversations(qa_pairs, num_conversations=10)
    save_conversations(conversations, output_path)


if __name__ == "__main__":
    main()
