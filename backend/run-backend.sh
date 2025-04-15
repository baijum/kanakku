#!/bin/bash
# Run the backend server like this:
# ./run-backend.sh
FLASK_APP=app FLASK_ENV=development flask run --port 8000 --debug