# Use the official Python image as the base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir flask flask-cors flask-socketio eventlet

# Expose the port that Flask will run on
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Start the application using eventlet
CMD ["python", "-m", "eventlet", "-wsgi", "app:app"]
