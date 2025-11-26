# Base Image
FROM python:3.9-slim

# Setup
WORKDIR /app

# --- TIMEZONE FIX ---
# 1. Install tzdata (Timezone Database)
RUN apt-get update && apt-get install -y tzdata

# 2. Set the Timezone to Central Europe (Slovakia)
ENV TZ=Europe/Bratislava

# 3. Apply the settings
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# --------------------

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