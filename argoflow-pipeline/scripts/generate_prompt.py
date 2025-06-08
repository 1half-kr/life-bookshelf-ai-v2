import json
from flows.interviews.rag.prompt import build_prompt

def main():
    with open('/app/output/questions.json') as f:
        questions = json.load(f)

    with open('/app/input/chat_history.json') as f:
        history = json.load(f)

    prompt = build_prompt(questions=questions, chat_history=history)

    with open('/app/output/prompt.json', 'w') as f:
        json.dump({"prompt": prompt}, f)

if __name__ == "__main__":
    main()
