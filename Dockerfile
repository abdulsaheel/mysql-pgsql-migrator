# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (if needed for debugging or extensions)
EXPOSE 8000

# Set environment variables file
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "app.py"]
