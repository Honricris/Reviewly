FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["flask", "run",  "--host=0.0.0.0", "--port=5000"]
