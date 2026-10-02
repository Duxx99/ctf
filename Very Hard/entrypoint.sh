#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Print the commands being executed (useful for debugging)
set -x

# Run the database population scripts
echo "Running database population scripts..."
python populate_database.py
python populate_specific_chat_1.py
python populate_specific_chat_2.py

# Start the Flask application
echo "Starting Flask application..."
exec python app.py
