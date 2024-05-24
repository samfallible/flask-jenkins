import argparse
from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuration file paths
CONFIG_FILE = 'conf'
JOBS_FILE = 'jobs.conf'

# Load configurations from file
def load_configurations():
    config = {}
    with open(CONFIG_FILE, 'r') as file:
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
    with open(JOBS_FILE, 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split('=')
            job_mapping[key] = value
    return job_mapping

JOB_MAPPING = load_job_mappings()

def handle_error(message, status_code=500):
    """Handles errors by returning a JSON response with the error message and status code."""
    response = {'message': 'An error occurred', 'error': message}
    return jsonify(response), status_code

def trigger_jenkins_job(job_name, parameters=None):
    """Triggers a Jenkins job and returns the status."""
    url = f'{JENKINS_URL}/job/{job_name}/buildWithParameters' if parameters else f'{JENKINS_URL}/job/{job_name}/build'
    auth = (JENKINS_USER, JENKINS_TOKEN)
    
    response = requests.post(url, auth=auth, params=parameters)
    return response.status_code

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Parse the incoming request
        data = request.json
        event_key = data.get('eventKey', '')

        # Determine the corresponding Jenkins job
        job_name = JOB_MAPPING.get(event_key)

        if not job_name:
            return handle_error('No corresponding Jenkins job found', 400)
        
        # Example of extracting data for a specific Bitbucket pull request event
        parameters = None
        if event_key == 'pullrequest:created':
            parameters = {
                'PR_ID': data['pullrequest']['id'],
                'REPO_NAME': data['repository']['name']
            }
        
        # Trigger the Jenkins job
        status_code = trigger_jenkins_job(job_name, parameters)
        
        if status_code == 201:
            return jsonify({'message': 'Jenkins job triggered successfully'}), 200
        else:
            return handle_error(f'Failed to trigger Jenkins job, status code: {status_code}')
    except Exception as e:
        return handle_error(str(e))

@app.route('/webhook/test', methods=['POST'])
def webhook_test():
    """A route for testing webhook connectivity."""
    try:
        return jsonify({'message': 'Webhook received successfully'}), 200
    except Exception as e:
        return handle_error(str(e))

def configure_application():
    """Run the application in configuration mode."""
    # Prompt user for Jenkins server configurations
    jenkins_url = input('Enter Jenkins URL: ')
    jenkins_user = input('Enter Jenkins User: ')
    jenkins_token = input('Enter Jenkins API Token: ')

    # Save configurations to conf file
    with open(CONFIG_FILE, 'w') as file:
        file.write(f'JENKINS_URL={jenkins_url}\n')
        file.write(f'JENKINS_USER={jenkins_user}\n')
        file.write(f'JENKINS_TOKEN={jenkins_token}\n')

    # Load configurations
    global config, JENKINS_URL, JENKINS_USER, JENKINS_TOKEN
    config = load_configurations()
    JENKINS_URL = config['JENKINS_URL']
    JENKINS_USER = config['JENKINS_USER']
    JENKINS_TOKEN = config['JENKINS_TOKEN']

    # Fetch job names from Jenkins server
    response = requests.get(f'{JENKINS_URL}/api/json', auth=(JENKINS_USER, JENKINS_TOKEN))
    if response.status_code == 200:
        jobs = response.json()['jobs']
        job_names = [job['name'] for job in jobs]
        
        # Pagination setup
        page_size = 10
        total_pages = (len(job_names) + page_size - 1) // page_size
        
        print('Available Jenkins jobs:')
        current_page = 0
        while True:
            start_index = current_page * page_size
            end_index = min(start_index + page_size, len(job_names))
            for job_name in job_names[start_index:end_index]:
                print(job_name)
            
            print(f'\nPage {current_page + 1} of {total_pages}')
            if current_page < total_pages - 1:
                next_page = input('Press Enter to see more jobs or type "done" to finish: ')
                if next_page.lower() == 'done':
                    break
                current_page += 1
            else:
                break
        
        # Prompt user to configure job mappings
        job_mapping = {}
        print('\nConfigure job mappings:')
        while True:
            event_key = input('Enter event key (or press Enter to finish): ')
            if not event_key:
                break
            job_name = input(f'Enter Jenkins job name for event key "{event_key}": ')
            if job_name in job_names:
                job_mapping[event_key] = job_name
            else:
                print(f'Error: Jenkins job "{job_name}" does not exist. Please enter a valid job name.')

        # Save job mappings to jobs.conf file
        with open(JOBS_FILE, 'w') as file:
            for event_key, job_name in job_mapping.items():
                file.write(f'{event_key}={job_name}\n')
        
        print('Configuration completed successfully.')
    else:
        print(f'Error fetching Jenkins jobs: {response.status_code} {response.text}')

def capture_request(display=False):
    """Run the application in capture mode."""
    try:
        # Ensure the directory exists
        os.makedirs('capturedRequests', exist_ok=True)

        # Simulate an incoming request for capturing (you can replace this with actual request data for real scenarios)
        data = {
            'key': 'value',
            'eventKey': 'example:event'
        }

        # Create a filename with a more human-readable timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = os.path.join('capturedRequests', f'request_{timestamp}.json')

        # Save the request data to the file
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

        if display:
            print(json.dumps(data, indent=4))

        print(f'Request captured successfully: {filename}')
    except Exception as e:
        print(f'An error occurred: {str(e)}')

def main():
    parser = argparse.ArgumentParser(description='Flask Webhook Processor and Jenkins Integration')
    parser.add_argument('--configure', action='store_true', help='Run the application in configuration mode')
    parser.add_argument('--capture', action='store_true', help='Run the application in capture mode')
    parser.add_argument('-d', '--display', action='store_true', help='Display captured request data')
    parser.add_argument('--development', action='store_true', help='Run the application in development mode')

    args = parser.parse_args()

    if args.configure:
        configure_application()
    elif args.capture:
        capture_request(display=args.display)
    elif args.development:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        from gunicorn.app.wsgiapp import run
        run()

if __name__ == '__main__':
    main()
