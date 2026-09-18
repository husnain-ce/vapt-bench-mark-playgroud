# Minimal self-contained target. Serve your app on the port declared in
# benchmark.yml (default 80). Keep it deterministic and offline-buildable.
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask
EXPOSE 80
CMD ["python", "app.py"]
