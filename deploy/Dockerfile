FROM python:3.12-slim-bullseye
LABEL authors="kamilrybacki"

# Install Taskfile
RUN pip install go-task-bin

# Copy source code and Taskfile
COPY . /app
WORKDIR /app

# Use Taskfile for building the image
RUN task initialize-venv
RUN task install-prod

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["task", "start-api"]
