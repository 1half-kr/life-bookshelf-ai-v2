FROM python:3.9

WORKDIR /app
COPY scripts/ ./scripts/
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "scripts/user_embedding.py"]  # 기본 실행은 step별로 override됨
