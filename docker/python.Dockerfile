# Generic image for native Python (Flask) benchmark targets that ship an
# app.py/main.py/server.py but no Dockerfile of their own.
#
# Build context is the target directory. A small launcher (baked in below)
# forces the Flask bind address to 0.0.0.0 so the app is always reachable
# through Docker's published port, regardless of how the target hardcodes
# its host. The target's own listen port is preserved unchanged.
FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Install the target's declared dependencies if present, always ensure Flask.
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true \
 && pip install --no-cache-dir flask

# Which file to execute (overridden per target via --build-arg ENTRY=...).
ARG ENTRY=app.py
ENV BENCH_ENTRY=${ENTRY}

# Launcher: monkeypatch Flask.run to force host=0.0.0.0, keep the app's port.
RUN printf '%s\n' \
  'import os, runpy' \
  'try:' \
  '    import flask' \
  '    _orig = flask.Flask.run' \
  '    def _run(self, *a, **k):' \
  '        port = k.get("port")' \
  '        if port is None and len(a) >= 2: port = a[1]' \
  '        if port is None and len(a) == 1 and isinstance(a[0], int): port = a[0]' \
  '        k.pop("host", None); k.pop("port", None)' \
  '        return _orig(self, host="0.0.0.0", port=port, **k)' \
  '    flask.Flask.run = _run' \
  'except Exception:' \
  '    pass' \
  'runpy.run_path(os.environ.get("BENCH_ENTRY", "app.py"), run_name="__main__")' \
  > /bench_run.py

CMD ["python", "/bench_run.py"]
