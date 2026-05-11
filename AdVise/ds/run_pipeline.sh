#!/bin/bash
# AdVise DS Pipeline — run from AdVise/ds/
# Usage: bash run_pipeline.sh
set -e

echo "========================================"
echo "  AdVise DS Pipeline"
echo "========================================"

echo ""
echo "[1/3] Training models..."
python train.py

echo ""
echo "[2/3] Running predictions..."
python predict.py

echo ""
echo "[3/3] Generating visual outputs..."
python generate_visuals.py

echo ""
echo "========================================"
echo "  Pipeline complete. Check outputs/"
echo "========================================"