# Use a stable Python 3.12 image
FROM python:3.12-slim-bookworm

# Set the working directory
WORKDIR /app

# Install dependencies and Korean fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    fonts-nanum \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the official installer script
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

# Copy uv lock and pyproject
COPY uv.lock pyproject.toml ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the code
COPY . .

# Ensure necessary directories exist
RUN mkdir -p cache chart csv db excel json send

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
CMD ["python", "main.py"]
