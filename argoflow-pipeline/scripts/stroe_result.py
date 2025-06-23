import json
import os

def main():
    with open('/app/output/llm_response.json') as f:
        result = json.load(f)

    os.makedirs('/app/final', exist_ok=True)

    with open('/app/final/question.txt', 'w') as f:
        f.write(result["response"])

    print("✅ 저장 완료: /app/final/question.txt")

if __name__ == "__main__":
    main()
