Bootstrap: docker
From: continuumio/miniconda3:latest

%post
    # Set environment variables
    export PATH="/opt/conda/envs/gates/bin:$PATH"

    # Update and install system dependencies
    apt-get update && apt-get install -y \
        wget \
        git \
        build-essential \
        libz-dev \
        libbz2-dev \
        liblzma-dev \
        && apt-get clean

    # Install Conda dependencies
    conda env create -f /app/environment.yaml
    conda clean -a -y

    # Activate the environment
    echo "source activate gates" >> ~/.bashrc

    # Make scripts executable
    chmod +x /app/bin/* /app/scripts/*

%files
    # Copy the GATES repository into the container
    . /app

%environment
    # Set environment variables for runtime
    export PATH="/opt/conda/envs/gates/bin:$PATH"
    export GATES_HOME="/app"

%runscript
    # Default command to run when the container is executed
    exec gates --help