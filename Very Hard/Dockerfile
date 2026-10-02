# Use official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app source code into the container
COPY app.py .
COPY templates ./templates

# Copy data scripts
COPY populate_database.py .
COPY populate_specific_chat_1.py .
COPY populate_specific_chat_2.py .
COPY print_database.py .

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh
# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set the entrypoint to the script
ENTRYPOINT ["/app/entrypoint.sh"]
