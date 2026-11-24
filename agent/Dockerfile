FROM python:3.11-slim

WORKDIR /app

ENV MALLOC_ARENA_MAX=2 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libsndfile1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=300 --retries=10 -r requirements.txt

COPY . .

CMD ["python", "main.py", "start"]
