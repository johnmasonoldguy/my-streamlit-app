# Streamlit Hackathon Project

## Installation Instructions Mac -Virtual Environment

## local dev - no docker

python3 -m venv .venv
source .venv/bin/activate
pip install streamlit
streamlit hello

## Docker

docker build -t streamlit .

docker images

docker run -p 8501:8501 streamlit

http://0.0.0.0:8501 or http://localhost:8501