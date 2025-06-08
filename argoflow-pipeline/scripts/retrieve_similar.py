import json
from flows.interviews.rag.retriever import search_similar_questions

def main():
    with open('/app/output/user_embedding.json') as f:
        user_vector = json.load(f)["embedding"]

    similar_questions = search_similar_questions(user_vector)

    with open('/app/output/questions.json', 'w') as f:
        json.dump(similar_questions, f)

if __name__ == "__main__":
    main()
