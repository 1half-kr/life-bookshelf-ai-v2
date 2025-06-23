import json
from flows.interviews.rag.retriever import get_user_embedding

def main():
    with open('/app/input/user.json', 'r') as f:
        user_info = json.load(f)

    embedding = get_user_embedding(user_info)

    with open('/app/output/user_embedding.json', 'w') as f:
        json.dump({"embedding": embedding}, f)

if __name__ == "__main__":
    main()
