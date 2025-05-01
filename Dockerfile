FROM python:3.13-slim

WORKDIR /app

# Copy app files
COPY . /app

# Install Python requirements
RUN pip install -r requirements.txt

# Expose ports
EXPOSE 5000

# Run app
CMD ["python3", "src/main.py"]
