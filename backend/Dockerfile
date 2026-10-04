# Build context: repository root (see docker-compose.yml)
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY ml ml
COPY backend backend
RUN mkdir -p data && python ml/generate_dataset.py && python ml/train_model.py
WORKDIR /app/backend
EXPOSE 8000
# Seed only if the database is empty, then serve
CMD ["sh", "-c", "python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
