from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Load configurations from file
def load_configurations():
    config = {}
    with open('conf', 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split('=')
            config[key] = value
    return config

config = load_configurations()
JENKINS_URL = config['JENKINS_URL']
JENKINS_USER = config['JENKINS_USER']
JENKINS_TOKEN = config['JENKINS_TOKEN']

# Load job mappings from file
def load_job_mappings():
    job_mapping = {}
    with open('jobs.conf', 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split('=')
            job_mapping[key] = value
    return job_mapping

JOB_MAPPING = load_job_mappings()

def trigger_jenkins_job(job_name):
    """Triggers a Jenkins job and returns the status."""
    url = f'{JENKINS_URL}/job/{job_name}/build'
    auth = (JENKINS_USER, JENKINS_TOKEN)
    
    response = requests.post(url, auth=auth)
    return response.status_code

@app.route('/bitbucket-webhook', methods=['POST'])
def bitbucket_webhook():
    try:
        # Parse the incoming request
        data = request.json
        event_key = data.get('eventKey', '')

        # Determine the corresponding Jenkins job
        job_name = JOB_MAPPING.get(event_key)

        if not job_name:
            return jsonify({'message': 'No corresponding Jenkins job found'}), 400
        
        # Trigger the Jenkins job
        status_code = trigger_jenkins_job(job_name)
        
        if status_code == 201:
            return jsonify({'message': 'Jenkins job triggered successfully'}), 200
        else:
            return jsonify({'message': 'Failed to trigger Jenkins job', 'status_code': status_code}), 500

    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/bitbucket-webhook/test', methods=['POST'])
def bitbucket_webhook_test():
    """A route for testing webhook connectivity from Bitbucket."""
    try:
        return jsonify({'message': 'Webhook received successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/capture', methods=['POST'])
def capture_request():
    """Capture any incoming request and save it to a file with a timestamp."""
    try:
        # Ensure the directory exists
        os.makedirs('capturedRequests', exist_ok=True)

        # Create a filename with a timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = os.path.join('capturedRequests', f'request_{timestamp}.json')

        # Save the request data to the file
        with open(filename, 'w') as file:
            json.dump(request.json, file, indent=4)

        return jsonify({'message': 'Request captured successfully', 'filename': filename}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
