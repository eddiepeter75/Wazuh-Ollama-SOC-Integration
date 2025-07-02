FROM python:3.9-slim-buster

WORKDIR /app

# Install any necessary Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script(s)
COPY . .

# If running a Flask/FastAPI app (assuming you are using alert_receiver_api.py):
CMD ["python", "alert_receiver_api.py"]

# If you prefer to have Wazuh call a standalone script via active response:
# CMD ["tail", "-f", "/dev/null"] # Keep container running for debugging, active response calls it.
