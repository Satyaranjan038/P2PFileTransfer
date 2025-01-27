# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Start the application with eventlet
CMD ["python", "-m", "eventlet", "app.py"]
