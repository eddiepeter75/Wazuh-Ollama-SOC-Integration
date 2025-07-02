# config/ollama-wazuh-integration/ollama_wazuh_analyzer.py
#!/usr/bin/env python3
import json
import requests
import sys
import os

# Configuration for Ollama
# Use the service name defined in docker-compose for inter-service communication
OLLAMA_API_URL = os.getenv("OLLAMA_HOST_URL", "http://ollama:11434") + "/api/generate"

def analyze_alert_with_ollama(alert_data):
    """Sends alert data to Ollama for analysis."""
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
        "model": "deepseek-r1", # Ensure this model is pulled in your Ollama instance
        "prompt": prompt,
        "stream": False # We want a single complete response
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data, timeout=120) # Increased timeout
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        return result.get("response", "No analysis provided by Ollama.")
    except requests.exceptions.Timeout:
        print(f"Error: Ollama API request timed out.", file=sys.stderr)
        return "Error: Ollama analysis timed out."
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}", file=sys.stderr)
        return f"Error: Failed to get analysis from Ollama. Details: {e}"
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON response from Ollama.", file=sys.stderr)
        return "Error: Invalid response from Ollama."


def process_wazuh_alert():
    """Reads alert from stdin, processes it, and prints Ollama's analysis."""
    try:
        alert_input = sys.stdin.read()
        alert_data = json.loads(alert_input)

        # For debugging, log the received alert
        with open("/tmp/ollama_wazuh_debug.log", "a") as f:
            f.write(f"Received alert: {json.dumps(alert_data, indent=2)}\n")

        ollama_analysis = analyze_alert_with_ollama(alert_data)

        # Print analysis to stdout (Wazuh active response captures this)
        print(f"Ollama Analysis:\n{ollama_analysis}")

        # --- Automated Triage and Alerting Logic ---
        # You can add more sophisticated logic here based on ollama_analysis
        # For example, if "CRITICAL ALERT" is in the analysis, trigger a separate notification.
        if "CRITICAL ALERT" in ollama_analysis.upper():
            print("ACTION: IMMEDIATE ESCALATION REQUIRED. Sending high-priority notification.")
            # You could integrate with a notification service here (e.g., Slack webhook, PagerDuty API)
            # Example: requests.post("YOUR_SLACK_WEBHOOK_URL", json={"text": f"CRITICAL: {alert_data['rule']['description']}\nOllama Analysis: {ollama_analysis}"})
        elif "LOW SEVERITY" in ollama_analysis.upper() or "INFORMATIONAL" in ollama_analysis.upper():
            print("ACTION: Logged for review. No immediate action required.")

    except json.JSONDecodeError:
        print("Error: Invalid JSON received from Wazuh (expected alert JSON).", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during alert processing: {e}", file=sys.stderr)

if __name__ == "__main__":
    process_wazuh_alert()
