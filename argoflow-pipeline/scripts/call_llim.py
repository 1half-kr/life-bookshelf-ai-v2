import json
from flows.interviews.rag.llm import call_openai_llm

def main():
    with open('/app/output/prompt.json') as f:
        prompt = json.load(f)["prompt"]

    response = call_openai_llm(prompt)

    with open('/app/output/llm_response.json', 'w') as f:
        json.dump({"response": response}, f)

if __name__ == "__main__":
    main()
