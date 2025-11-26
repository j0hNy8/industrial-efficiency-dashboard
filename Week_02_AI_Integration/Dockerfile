# Base Image
FROM python:3.9-slim

# Setup
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy Code
COPY . .

# Copy the entrypoint script and make it executable (Crucial step!)
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Network
EXPOSE 8501

# Run the Master Switch
ENTRYPOINT ["./entrypoint.sh"]