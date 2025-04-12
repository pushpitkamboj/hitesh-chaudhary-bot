FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables
ENV PORT=5000
ENV RENDER=true

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "index.py"]