#!/bin/bash
cd Client
python3 simulation.py
echo "new graphs have been created for vizualization A1 and A2"
docker rm -f server_1