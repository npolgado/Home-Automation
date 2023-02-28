# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /mancave_flask
WORKDIR /mancave_flask

# Copy the current directory contents into the container at /mancave_flask
COPY . /mancave_flask

RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
