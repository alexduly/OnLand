FROM rust:1.81-slim-bullseye

# Install additional dependencies if necessary
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /workspace

# Copy the project files
COPY .. .

# Install the Rust toolchain
RUN cargo install cargo-audit
