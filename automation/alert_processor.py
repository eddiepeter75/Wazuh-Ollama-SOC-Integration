import requests
import json
import subprocess

# Configuration
ELASTICSEARCH_URL = "http://wazuh.indexer:9200"
OLLAMA_URL = "http://ollama:11434"
MODEL_NAME = "deepseek-r1"

def fetch_alerts():
    """Get recent high-priority alerts from Wazuh"""
    query = {
        "query": {"range": {"rule.level": {"gte": 7}}},
        "sort": [{"timestamp": {"order": "desc"}}],
        "size": 5
    }
    response = requests.post(
        f"{ELASTICSEARCH_URL}/wazuh-alerts-*/_search",
        json=query,
        headers={"Content-Type": "application/json"}
    )
    return response.json().get('hits', {}).get('hits', [])

def analyze_with_ai(alert):
    """Send alert to DeepSeek for analysis"""
    prompt = f"""
    Analyze this security alert and provide:
    1. Severity (1-10)
    2. Recommended action
    3. True/False for whether it requires immediate attention

    Alert: {json.dumps(alert, indent=2)}
    """
    cmd = f'curl -s {OLLAMA_URL}/api/generate -d \'{{"model": "{MODEL_NAME}", "prompt":"{prompt}"}}\''
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return json.loads(result.stdout)

if __name__ == "__main__":
    alerts = fetch_alerts()
    for alert in alerts:
        analysis = analyze_with_ai(alert['_source'])
        print(f"Alert {alert['_id']} analysis:")
        print(analysis.get('response', 'No response'))
