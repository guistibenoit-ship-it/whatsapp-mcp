FROM golang:1.26-bookworm AS bridge
WORKDIR /src
COPY whatsapp-bridge/ ./
COPY cloud-patch.py /tmp/cloud-patch.py
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*
RUN python3 /tmp/cloud-patch.py && go get go.mau.fi/whatsmeow@v0.0.0-20260917111002-2e338d0ee73d && go mod tidy && CGO_ENABLED=1 go build -buildvcs=false -o /whatsapp-bridge .

FROM python:3.12-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libsqlite3-0 && rm -rf /var/lib/apt/lists/*
COPY cloud-requirements.txt ./
RUN pip install --no-cache-dir -r cloud-requirements.txt
COPY --from=bridge /whatsapp-bridge /app/bridge
COPY cloud.py ./
ENV PYTHONUNBUFFERED=1
CMD ["python", "cloud.py"]
