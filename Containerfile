FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py resource_queries.py cli.py ./

CMD ["python", "main.py"]
