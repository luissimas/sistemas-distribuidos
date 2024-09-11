FROM python:3.12-slim

# Set environment variables to prevent .pyc files and set up buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code to the working directory
COPY trabalho-2 /app/trabalho-2
COPY requirements.txt /app

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment and install dependencies
RUN /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# The target script to run in this image
ARG TARGET
ENV TARGET=$TARGET

# Run the application
CMD ["sh", "-c", "/opt/venv/bin/python trabalho-2/${TARGET}"]
