# Wazuh-Ollama SOC Integration for AI-Powered Alert Analysis

This project demonstrates a proof-of-concept integration between Wazuh, a free and open-source security platform, and Ollama, a lightweight local LLM (Large Language Model) server, to provide AI-powered analysis of security alerts. This setup aims to enhance Security Operations Center (SOC) capabilities by leveraging AI for faster context, severity assessment, and response suggestions for security incidents.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Security Research Value](#security-research-value)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

In modern SOC environments, analysts are often overwhelmed by the volume of alerts. This project showcases how to integrate a local Large Language Model (LLM) into the alert analysis workflow. When Wazuh detects a high-severity event (e.g., a brute-force attack), it triggers an active response that sends the alert details to a custom Python script. This script then communicates with a locally hosted Ollama instance (running a model like Llama 3 or similar) to generate an AI-driven summary, potential impact, and suggested actions, which can then be logged back into Wazuh or displayed in the dashboard.

## Features
* **Wazuh:** Comprehensive XDR platform for security monitoring, log analysis, integrity monitoring, and vulnerability detection.
* **Ollama:** Easy-to-use local LLM server for running open-source models offline.
* **Custom Python Integration:** A Flask-based API that acts as a bridge between Wazuh Active Response and Ollama.
* **AI-Powered Alert Analysis:** Leverages LLMs to provide context, severity, and response suggestions for security alerts.
* **Docker Compose Deployment:** Simple setup for all components in a containerized environment.

## Architecture

+----------------+      Active Response     +----------------------------+      HTTP API     +-----------------+
|  Wazuh Manager | ------------------------> | Ollama-Wazuh Integration   | ------------------> |      Ollama     |
| (Alerts)       |                          | (Python Flask API)         |                   | (LLM Model)     |
+----------------+                          +----------------------------+                   +-----------------+
^                                                                                           |
|                                                                                           |
| Log Collection                                                                            | AI Analysis
|                                                                                           |
+----------------+                                                                            (Returned to Integration)
|  Wazuh Agent(s) |
+----------------+


## Prerequisites

Before you begin, ensure you have the following installed:

* **Docker:** [Install Docker Engine](https://docs.docker.com/engine/install/)
* **Docker Compose:** [Install Docker Compose](https://docs.docker.com/compose/install/)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/Wazuh-Ollama-SOC-Integration.git](https://github.com/your-username/Wazuh-Ollama-SOC-Integration.git)
    cd Wazuh-Ollama-SOC-Integration
    ```

2.  **Configure Wazuh (Optional, if using custom rules/settings):**
    The `docker-compose.yml` mounts `config/wazuh_manager/ossec.conf` to the Wazuh Manager. You can customize active response rules and other settings in this file. Ensure the `<active-response>` block is configured for the `ollama-analyze-alert` command, typically for high-severity alerts.

3.  **Build and start the Docker containers:**
    ```bash
    docker-compose up -d --build
    ```
    This will download the necessary Docker images, build the integration service, and start all components. It might take some time to download the Ollama image and the LLM model (e.g., `llama3`).

4.  **Pull an Ollama Model:**
    Once Ollama is running, you need to pull a language model. For example, to pull Llama 3:
    ```bash
    docker exec -it single-node-ollama-1 ollama pull llama3
    ```
    *(You may need to adjust the model name in your `ollama_wazuh_analyzer.py` script if you choose a different one.)*

## Usage

1.  **Access Wazuh Dashboard:**
    Navigate to `https://localhost` (or your Docker host's IP) in your browser. You should be able to log in to the Wazuh Dashboard.

2.  **Trigger a High-Severity Alert:**
    To test the automation, generate an alert that is configured to trigger the `ollama-analyze-alert` active response (e.g., a Level 10 alert). A common way to simulate this is by generating multiple failed SSH login attempts on the Wazuh Manager itself:
    ```bash
    docker exec -it single-node-wazuh.manager-1 logger -p auth.info -t sshd "Failed password for user nonexistent from 192.168.1.100 port 54321 ssh2"
    # Repeat the above command 5-10 times quickly to trigger rule 5503 (brute-force)
    ```

3.  **Observe the Automation:**
    * **Wazuh Active Response Log:**
        Check if Wazuh executed the active response:
        ```bash
        docker exec -it single-node-wazuh.manager-1 tail -f /var/ossec/logs/active-responses.log
        ```
        Look for entries similar to: `Running command: 'ollama-analyze-alert' with arguments '[{"alert": ...}]'`

    * **Ollama-Wazuh Integration Logs:**
        Check the logs of your integration service to see it processing the alert and interacting with Ollama:
        ```bash
        docker logs single-node-ollama-wazuh-integration-1
        ```
        You should see messages indicating an alert was received and an API call made to Ollama.

    * **Ollama Server Logs:**
        Verify Ollama received the request and performed inference:
        ```bash
        docker logs single-node-ollama-1
        ```
        Look for log entries indicating model loading and inference activity.

    * **Wazuh Dashboard/Alerts:**
        Depending on how your `ollama_wazuh_analyzer.py` is designed, it might send the analysis back to Wazuh as a new alert or log entry. Monitor the Wazuh Dashboard for new alerts or insights.

## Security Research Value

This project provides a foundation for exploring various aspects of AI in cybersecurity:
* **Automated Alert Triage:** Reducing the manual burden on SOC analysts.
* **Contextual Enrichment:** LLMs can provide context beyond what traditional SIEM rules can offer.
* **Threat Hunting Assistance:** AI can suggest related threats or TTPs based on initial alert data.
* **Customizable AI Models:** The flexibility of Ollama allows for experimentation with different open-source models tailored for cybersecurity tasks.
* **Privacy and Data Sovereignty:** Running LLMs locally keeps sensitive alert data within your controlled environment.

## Contributing

Feel free to fork this repository, open issues, and submit pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License - see the `LICENSE` file for details
