# config/ollama-wazuh-integration/alert_receiver_api.py
from flask import Flask, request, jsonify
import json
import requests
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration for Ollama
OLLAMA_API_URL = os.getenv("OLLAMA_HOST_URL", "http://ollama:11434") + "/api/generate"

def analyze_alert_with_ollama(alert_data):
    # ... (same analyze_alert_with_ollama function as above)
    prompt = f"""
    Analyze the following security alert. Provide a concise summary, potential impact, and recommended actions.
    Act as a highly experienced SOC analyst. Focus on practical, actionable advice for a security team.
    If the alert is critical, explicitly state 'CRITICAL ALERT' and suggest immediate remediation steps.
    If it's informational or low severity, suggest monitoring or minor adjustments.

    Alert Details:
    {json.dumps(alert_data, indent=2)}

    Analysis and Recommendations:
    """

    headers = {"Content-Type": "application/json"}
    data = {
        "model": "deepseek-r1",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No analysis provided by Ollama.")
    except requests.exceptions.Timeout:
        logging.error(f"Ollama API request timed out.")
        return "Error: Ollama analysis timed out."
    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with Ollama API: {e}")
        return f"Error: Failed to get analysis from Ollama. Details: {e}"
    except json.JSONDecodeError:
        logging.error(f"Could not decode JSON response from Ollama.")
        return "Error: Invalid response from Ollama."


@app.route('/wazuh-alert', methods=['POST'])
def receive_alert():
    if request.is_json:
        alert_data = request.get_json()
        logging.info(f"Received Wazuh Alert: {json.dumps(alert_data, indent=2)}")

        ollama_analysis = analyze_alert_with_ollama(alert_data)
        logging.info(f"Ollama Analysis: {ollama_analysis}")

        # --- Automated Triage and Alerting Logic ---
        if "CRITICAL ALERT" in ollama_analysis.upper():
            logging.warning("ACTION: IMMEDIATE ESCALATION REQUIRED.")
            # Add notification integration here
        elif "LOW SEVERITY" in ollama_analysis.upper() or "INFORMATIONAL" in ollama_analysis.upper():
            logging.info("ACTION: Logged for review. No immediate action required.")

        return jsonify({"status": "success", "ollama_analysis": ollama_analysis}), 200
    logging.error("Received non-JSON request.")
    return jsonify({"status": "error", "message": "Request must be JSON"}), 400

if __name__ == '__main__':
    # Run Flask app, accessible from other Docker services at port 5001
    app.run(host='0.0.0.0', port=5001)
