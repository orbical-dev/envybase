FROM python:3.13.3-slim

# install apt-utils and update before installing other packages


RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends apt-utils pip python3 && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory

WORKDIR /app
# Copy the requirements file into the container
COPY requirements.txt .
# Install the required packages
RUN pip3 install --no-cache-dir -r requirements.txt
# Copy the rest of the application code into the container
COPY . .


CMD [ "python3", "main.py" ]