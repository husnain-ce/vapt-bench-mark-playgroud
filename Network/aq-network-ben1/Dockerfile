# Multi-service network box: an HTTP recon page (8000) and an unauthenticated
# Redis-like data service (6379) in one container. Ports are pinned; bench maps
# a host-port block from the network domain range.
FROM python:3.12-slim
WORKDIR /app
COPY app.py /app/
EXPOSE 8000 6379
CMD ["python", "app.py"]
