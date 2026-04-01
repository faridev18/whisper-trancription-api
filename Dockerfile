FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main_render.py .

CMD ["sh", "-c", "uvicorn main_render:app --host 0.0.0.0 --port $PORT"]
