

# Minimal, robust Dockerfile for Streamlit + OpenAI + certifi CA trust
FROM python:3.9-slim

# Set workdir
WORKDIR /app

# Copy the certificate into the container
COPY idexx.crt /usr/local/share/ca-certificates/idexx.crt
COPY idexx2.crt /usr/local/share/ca-certificates/idexx2.crt
COPY idexx.pem /usr/local/share/ca-certificates/idexx.pem

# Install CA tools
RUN apt-get update && apt-get install -y ca-certificates 

# UUpdate CA certificates
RUN update-ca-certificates

# Copy app codeopen
COPY app/requirements.txt requirements.txt
COPY app/ app/

ENV SSL_CERT_DIR=/etc/ssl/certs

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Healthcheck (optional)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit app
ENTRYPOINT ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]