 FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/logs data/uploads data/outputs data/captures

# Expose port (Render/Railway will set PORT env var)
EXPOSE 8000

# Set environment variable defaults
ENV DUMMY_MODEL=true \
    PORT=8000

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
