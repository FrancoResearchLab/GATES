# Conda base image
FROM continuumio/miniconda3:latest

# Set environment variables
ENV GATES_HOME="/app"
ENV PATH="/app/bin:/opt/conda/envs/gates/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    build-essential \
    libz-dev \
    libbz2-dev \
    liblzma-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and create environment
COPY environment.yaml /app/environment.yaml
RUN conda env create -f /app/environment.yaml && \
    conda clean -afy

# Copy all gates scripts
COPY . /app

# Make all scripts executable
RUN find /app/bin /app/scripts -type f -exec chmod +x {} \;

# Entry point is gates env
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "gates"]
CMD ["gates", "--help"]