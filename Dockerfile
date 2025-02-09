# Use the official Python image as the base
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the app's port
EXPOSE 8050

# Define the command to run the application
CMD ["python", "app.py"]
