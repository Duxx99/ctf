# API/Dockerfile
# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/ ./src
COPY db/ ./db
COPY scripts/ ./scripts

# Expose the port that the API service runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "src/app.py"]
