# ollama_wazuh_analyzer.py
import json
import requests
import os
import sys

# Configuration for Ollama
OLLAMA_API_URL = "http://ollama:11434/api/generate" # 'ollama' is the service name in docker-compose

def analyze_alert_with_ollama(alert_data):
    prompt = f"""
    Analyze the following security alert and provide a concise summary, potential impact, and recommended actions.
    Behave as a SOC analyst and use your knowledge base to provide the best and most accurate recommendations for the alert
    If possible provide remediation steps if not then recommend next steps for SOC.

    Alert:
    {json.dumps(alert_data, indent=2)}

    Analysis:
    """
    
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "deepseek-r1", # Ensure this model is pulled in Ollama
        "prompt": prompt,
        "stream": False # We want a single complete response
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        return result.get("response", "No response from Ollama.")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}", file=sys.stderr)
        return f"Error: Could not get analysis from Ollama. {e}"

def process_wazuh_alert(alert_json_str):
    try:
        alert_data = json.loads(alert_json_str)
        print(f"Received Wazuh Alert: {json.dumps(alert_data, indent=2)}")

        ollama_analysis = analyze_alert_with_ollama(alert_data)
        print("\n--- Ollama Analysis ---")
        print(ollama_analysis)
        print("-----------------------")

        # Implement your automated triage and alerting logic here
        # Example: if analysis suggests critical, send email/slack alert
        if "critical" in ollama_analysis.lower() or "high severity" in ollama_analysis.lower():
            print("Action: This is a critical alert based on Ollama's analysis. Consider immediate escalation.")
            # Example: Trigger an external notification (e.g., email, Slack, PagerDuty)
            # You would integrate with your notification service API here.
        elif "low severity" in ollama_analysis.lower():
            print("Action: Low severity, consider logging for review.")

    except json.JSONDecodeError:
        print("Error: Invalid JSON received from Wazuh.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    # When Wazuh calls an active response script, it passes the alert JSON
    # as an argument. For `integratord` or `wodles`, it might be stdin.
    # For active response, typically read from stdin.
    
    # Read the alert JSON from stdin (how active response typically works)
    alert_input = sys.stdin.read()
    process_wazuh_alert(alert_input)
