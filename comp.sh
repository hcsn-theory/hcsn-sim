#!/bin/bash

# This command prevents sleep when the lid is closed
systemd-inhibit --what=handle-lid-switch --why="Running simulation and uploading" bash <<EOF

echo "Waiting for simulation (run_all.sh) to finish..."
while pgrep -f "run_variants.sh" > /dev/null; do
    sleep 30
done

echo "Simulation finished. Uploading to GitHub..."
git add .
git commit -m "Results for variants 1-4"
git push origin main

echo "Push complete. Shutting down in 60 seconds..."
sudo shutdown -h +1
EOF
