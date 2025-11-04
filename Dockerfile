FROM python:3.10-slim

WORKDIR /app

COPY ./app ./app

RUN pip install --no-cache-dir -r app/requirements.txt

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]