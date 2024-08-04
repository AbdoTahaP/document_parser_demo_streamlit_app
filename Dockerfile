FROM ubuntu:22.04
FROM python:3.10-slim

WORKDIR /

RUN apt-get update && apt-get -y install sudo

RUN apt-get update -y && apt-get install build-essential -y

RUN apt-get update -y && apt-get install wget -y

COPY packages.txt .

RUN sudo apt-get update -y && apt-get upgrade -y && xargs apt-get install < packages.txt -y

# Copy the requirements file to the working directory
COPY requirements.txt .

RUN pip install -r requirements.txt

# Clean up after installations
RUN pip cache purge

# EXPOSE 8501

# Copy the application code to the working directory
COPY . .

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the Streamlit application
ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=80", "--server.address=0.0.0.0"]

