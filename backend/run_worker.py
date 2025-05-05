# Apply eventlet monkey patch *before* importing celery or tasks
import eventlet
eventlet.monkey_patch()

import sys
import os

# Ensure the current directory is in the Python path *before* importing tasks
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the Celery app instance from tasks.py *after* patching
from tasks import celery_app

if __name__ == '__main__':
    # Prepare arguments for the worker_main method
    # These are the arguments that normally follow 'celery -A tasks worker'
    worker_argv = [
        'worker', # The command
        '--pool=eventlet',
        '--loglevel=info',
    ]
    # Append any additional arguments passed to this script
    # worker_argv.extend(sys.argv[1:]) # Optional: if you want to pass extra args like -Q queue_name

    print(f"Starting Celery worker using app.worker_main with argv: {worker_argv}")
    # Call the worker_main method on the app instance
    celery_app.worker_main(argv=worker_argv)
