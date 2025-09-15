FROM python:3.12-bullseye
LABEL authors="kamilrybacki"

# Install Taskfile
RUN pip install go-task-bin

# Copy source code and Taskfile
COPY . /app
WORKDIR /app

RUN python -m pip install virtualenv
RUN python -m virtualenv --python=python3.12 .venv
RUN . .venv/bin/activate || source .venv/bin/activate || true
RUN .venv/bin/python -m pip install --upgrade poetry

RUN .venv/bin/poetry config virtualenvs.path .venv
RUN .venv/bin/poetry config virtualenvs.create false
RUN .venv/bin/poetry config cache-dir .cache/pypoetry
RUN .venv/bin/poetry config virtualenvs.in-project true
RUN .venv/bin/poetry lock
RUN .venv/bin/poetry install

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD [".venv/bin/python", "-m", "uvicorn", "src.mtgapi.entrypoint:API", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]
