# Generic image for native Node.js benchmark targets that ship a server.js /
# index.js but no Dockerfile of their own. Build context is the target dir.
FROM node:20-slim

WORKDIR /app
COPY . /app

# Install dependencies when a manifest is present; ignore failures so
# zero-dependency targets still build.
RUN if [ -f package-lock.json ]; then npm ci --omit=dev 2>/dev/null || npm install --omit=dev 2>/dev/null || true; \
    elif [ -f package.json ]; then npm install --omit=dev 2>/dev/null || true; fi

ARG ENTRY=server.js
ENV BENCH_ENTRY=${ENTRY}
ENV HOST=0.0.0.0

CMD ["sh", "-c", "node ${BENCH_ENTRY:-server.js}"]
