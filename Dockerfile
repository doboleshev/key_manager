FROM python:3.11-slim

WORKDIR /app

# Устанавливаем совместимые версии
RUN pip install pymongo==4.6.1 fastapi uvicorn cryptography python-jose python-dotenv

COPY . .

# Устанавливаем PYTHONPATH чтобы видеть модули в src/
ENV PYTHONPATH=/app/src:$PYTHONPATH

EXPOSE 8000

CMD ["python", "-m", "src.main"]