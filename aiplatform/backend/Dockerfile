FROM python:3.11-slim

# Set working directory inside container
WORKDIR /code

# Copy dependencies file first (better for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend app code
COPY ./app ./app
