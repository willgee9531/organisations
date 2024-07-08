FROM python:3-alpine AS builder

WORKDIR /app

RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
# Update pip to the latest version
RUN pip install --upgrade pip
# Increase the default timeout and use a faster mirror
RUN pip install --timeout=600 -r requirements.txt

# Stage 2
FROM python:3-alpine AS runner

WORKDIR /app

COPY --from=builder /app/venv venv
COPY run.py run.py
COPY app/ app/

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FLASK_APP=run.py

EXPOSE 8080

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "run:app"]
