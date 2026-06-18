FROM python:3.10-slim

WORKDIR /app

# Copy requirements if they exist, otherwise just install fastapi and uvicorn
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir fastapi uvicorn; fi

COPY . .

# Run the app
CMD ["python", "main.py"]
