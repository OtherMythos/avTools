#!/bin/bash

for i in {1..5}; do
  echo "Running iteration $i of 5..."
  python3 testRunner.py -l /tmp/testLogs -e /Users/edward/Documents/avEngine/build/Debug/av.app/Contents/MacOS/av -p /Users/edward/Documents/avTests/avTestsIntegration.cfg
  echo "Iteration $i completed."
  echo ""
done

echo "All 5 iterations completed."
