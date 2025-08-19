# Use official Python 3.13 image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get clean \
    && pip install --upgrade pip \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Set default command to run main.py
CMD ["python", "main.py"]