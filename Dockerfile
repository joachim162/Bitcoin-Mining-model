# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container
COPY bitcoin_mining_simulation.py .

# Optional: Create a directory for output or logs
RUN mkdir /app/output

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

EXPOSE 8521

# Default command to run the simulation
CMD ["python", "bitcoin_mining_simulation.py"]
