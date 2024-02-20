# syntax=docker/dockerfile:1 

FROM python:3.11-bookworm as base
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "--host", "0.0.0.0", "--port", "8000", "src.main:app"]
