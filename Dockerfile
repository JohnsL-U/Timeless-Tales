# Use an official Python runtime as a parent image
FROM python:3.10.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory in the container
WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       postgresql-client

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /code
COPY . /code/


# Make port 8000 available to the world outside this container
EXPOSE 8000

CMD sh -c 'python manage.py migrate && python manage.py runserver 0.0.0.0:8000'
