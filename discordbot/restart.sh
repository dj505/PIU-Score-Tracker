#!/bin/bash
echo "Restarting Amadeus..."
sudo pkill -f run.py
sudo python3 run.py
echo "Restart complete!"
