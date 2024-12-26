#!/bin/bash

# Conda 환경 활성화
source /home/hojae/miniconda3/bin/activate base 

# Python 스크립트 실행
python /home/hojae/gpu_track_slack_bot_for_repo/gpu_track.py

# Conda 환경 비활성화
conda deactivate
