FROM python:3.12-slim

WORKDIR /app

# Install CPU-only PyTorch first before everything else.
# Without this, sentence-transformers pulls the full CUDA build (~2.5GB).
# CPU-only is ~500MB — saves ~2GB on the final image.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
