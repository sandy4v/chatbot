# Use an official Python runtime as a base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container at /app
COPY DockerApp/requirements.txt /app/requirements.txt

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application files into the container
COPY DockerApp /app

# Expose the port that the application will run on (optional)
EXPOSE 8501

# Command to run your application (adjust this depending on your main script)
CMD ["python3", "trevor_main.py"]