FROM python:3.12

WORKDIR /app

ENV PYTHONPATH=/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "__main__.py"]
