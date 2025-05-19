# we are going to be using python 3.9
FROM python:3.9-slim

# we are creating folder called app!
# this is equiovalent to cd /app in terminal
WORKDIR /app

# Copy all files from your current folder into the Docker!
COPY . /app

# Install necessary Python package
RUN pip install matplotlib

# when I start the container, it will run the following python script
ENTRYPOINT ["python3", "run_sugarscape.py"]

