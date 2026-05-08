#!/bin/bash

echo "🦀 Building Rust Opening Book Generator..."
echo ""

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust not found!"
    echo ""
    echo "Install Rust with:"
    echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo ""
    exit 1
fi

echo "✓ Rust found: $(rustc --version)"
echo ""

# Build with release optimizations
echo "🔨 Compiling with optimizations (this may take a minute)..."
cargo build --release

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Run with:"
    echo "  ./target/release/opening_book_generator"
    echo ""
    echo "Or use:"
    echo "  cargo run --release"
else
    echo ""
    echo "❌ Build failed"
    exit 1
fi
