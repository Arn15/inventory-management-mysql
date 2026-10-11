FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/config.example.yaml config/config.yaml
COPY data ./data
COPY src ./src
COPY tests ./tests
COPY pytest.ini .

# run as an unprivileged user
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

CMD ["python", "src/app.py"]
