FROM python:3.12.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install Flask-Cors

COPY . .

ENV ADDR=0.0.0.0
ENV PORT=8080

EXPOSE $PORT

CMD ["python", "API.py"]

