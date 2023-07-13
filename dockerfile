FROM python:3.8-slim

WORKDIR /app

RUN pip install boto3 flask amazon-dax-client

COPY . .

CMD ["python3", "main.py"]
