#!/bin/bash
# CHRONOS Pipeline Runner
# Activates heritage conda environment and runs the pipeline

echo "🚀 CHRONOS Pipeline Runner"
echo "================================"
echo ""
echo "Activating heritage conda environment..."

# Source conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate heritage environment
conda activate heritage

# Check if activation was successful
if [ "$CONDA_DEFAULT_ENV" = "heritage" ]; then
    echo "✅ Heritage environment activated"
    echo ""

    # Run the pipeline
    cd app
    python main.py

else
    echo "❌ Failed to activate heritage environment"
    echo "Please run manually: conda activate heritage"
    exit 1
fi
