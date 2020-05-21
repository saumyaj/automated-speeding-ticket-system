#!/bin/sh
conda activate detector
cd detection_and_recognition
python detector.py --image $1
