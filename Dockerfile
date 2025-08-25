
# app/Dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


COPY app/requirements.txt requirements.txt
COPY app/ app/
COPY app/backend/input.json app/backend/input.json
RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]