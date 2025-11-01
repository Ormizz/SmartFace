#!/bin/bash

echo "🍓 Starting SmartFace on Raspberry Pi Zero 2W"
echo "=============================================="

# Check if running on Pi
if [ ! -f /sys/firmware/devicetree/base/model ]; then
    echo "⚠️  Warning: Not running on Raspberry Pi"
fi

# Activate venv
source venv/bin/activate

# Set memory limits
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Reduce TensorFlow verbosity
export TF_CPP_MIN_LOG_LEVEL=2

# Use config for Pi
export SMARTFACE_CONFIG=config_rpi

# Check memory
echo "📊 Memory status:"
free -h

# Run SmartFace with lower priority (nice)
nice -n 10 python3 run.py --no-visual

echo ""
echo "✅ SmartFace stopped"