#!/bin/bash
# Build script for Vercel deployment
# This installs Rust and builds the Python extension

set -e

# Install Rust if not already installed
if ! command -v cargo &> /dev/null; then
    echo "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source $HOME/.cargo/env
fi

# Install maturin
pip install maturin

# Build and install the Rust extension
cd four_in_a_row_rust
maturin build --release
pip install target/wheels/*.whl
cd ..

echo "Rust extension built and installed successfully"
