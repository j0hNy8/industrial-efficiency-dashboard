#!/bin/bash

# 1. Start the Simulator in the background (&)
echo "Starting Factory Simulator..."
python sensor_sim.py &

# 2. Start the Streamlit Dashboard in the foreground
echo "Starting Dashboard..."
python -m streamlit run Home.py --server.port=8501 --server.address=0.0.0.0