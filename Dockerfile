FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY modules ./modules

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "modules.voice.api:app", "--host", "0.0.0.0", "--port", "8000"]


