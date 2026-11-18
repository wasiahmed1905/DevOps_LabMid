FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG GIT_COMMIT=local
ENV GIT_COMMIT=${GIT_COMMIT}

# Ensure artifacts/model.joblib and artifacts/metrics.json always exist inside the image
RUN python3 train.py

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
