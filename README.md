This Flask app processes an incoming request and triggers a corresponding Jenkins job.

Use the conf file to load the Jenkins server URL, username, and token.

Use the route /test to test connection to the Flask app.

Use the route /capture to capture incoming for inspection, this will inform your jobs.conf mappings.

Use the jobs.conf file to map a key from the incoming request to a jenkins jobname.

