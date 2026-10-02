# GraphQL/Dockerfile
# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that the GraphQL service runs on
EXPOSE 80

# Command to run the application
CMD ["python", "app.py"]
