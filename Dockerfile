# from python latest
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# add conf dir
RUN mkdir -p /var/lib/schurli/config

# install poetry
RUN pip install poetry

# Copy initial necessary files to container
COPY pyproject.toml \
poetry.lock ./

# Install poetry deps
RUN poetry install

# Copy module
COPY schurli ./schurli

# Start bot
CMD ["poetry", "run", "main"]
