# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install PostgreSQL development packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application code into the container
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8000

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]
