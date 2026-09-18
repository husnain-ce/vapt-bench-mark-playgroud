FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY icon.png /app/icon.png
COPY app.py /app/app.py
RUN pip install --no-cache-dir -r /app/requirements.txt
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app:app", "-w", "2", "-b", "0.0.0.0:8000"]
