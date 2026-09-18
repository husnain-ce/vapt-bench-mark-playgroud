FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y --no-install-recommends ncat \
    && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["ncat"]
CMD ["-kl", "80"]
