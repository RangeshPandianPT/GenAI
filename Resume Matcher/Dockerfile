FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Wait, resume matcher has backend.py
CMD ["python", "backend.py"]
