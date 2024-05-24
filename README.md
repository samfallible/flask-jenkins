# flask-jenkins
This Flask application processes HTTP requests and triggers corresponding jobs on a Jenkins server.

## Setup

Ensure you have Python and Flask installed. You can install Flask using pip:

```pip install Flask requests```

### Using Configuration Mode
To configure the application on the command line, run:

```python app.py --configure```

Follow the prompts inputting your Jenkins server url and auth, then map event keys to jobnames. The script will retrive jobnames from the server. If you dont know what event keys to exepct use capture mode first.

### Using Configuration Files

Alternatively, you can edit the configuration files.

The conf file contains the Jenkins server URL, username, and token:

```
JENKINS_URL=http://your-jenkins-server:8080
JENKINS_USER=your-jenkins-user
JENKINS_TOKEN=your-jenkins-api-token
```

Use the jobs.conf file to map a key from the incoming request to a Jenkins job name:

```
event_key_1=jenkins-job-1
event_key_2=jenkins-job-2
event_key_3=jenkins-job-3
pullrequest:created=jenkins-job-pullrequest-created
```

## Running the Application

### Capture Mode
Incoming requests will be saved as files in the ```capturedRequests/``` directory. run:

```python app.py --capture```

To display requests while capturing, use the -d flag:

```python app.py --capture -d```

### Development Mode
To start the Flask application in development mode, run:

```python app.py --development```

The application will start without a WSGI and ```debug=True```.

### Production Mode
To start the Flask application in production mode using gunicorn, run:

```gunicorn -w 4 -b 0.0.0.0:5000 app:app```

This command starts gunicorn with 4 worker processes.

## Webhook Configuration

Configure your webhook to target ```your.server.fqdn/webhook``` as the main endpoint for processing requests.

### Testing the Webhook Connection

You can use the ```your.server.fqdn/webhook/test``` endpoint to test the connection to the application.
