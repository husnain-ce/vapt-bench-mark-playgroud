FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY . .
COPY flag.txt /flag.txt
EXPOSE 8000
CMD ["python","main.py"]
