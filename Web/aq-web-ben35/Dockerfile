FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask flask-session pycryptodome
COPY . .
EXPOSE 5000
CMD ["python","app.py"]
