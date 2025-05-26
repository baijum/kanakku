# Kanakku API Documentation

This directory contains the OpenAPI (Swagger) documentation for the Kanakku backend API.

## Viewing the Documentation

There are several ways to view and interact with the Swagger documentation:

### Option 1: Using Swagger Editor Online

1. Go to https://editor.swagger.io/
2. Copy the contents of `swagger.yaml` and paste it into the editor

### Option 2: Generate HTML documentation

You can use various tools to generate static HTML documentation from the swagger.yaml file:

```bash
npm install -g redoc-cli
redoc-cli bundle swagger.yaml -o swagger.html
```

## Integrating with Backend

To integrate Swagger UI directly with the Flask backend:

1. Install the required packages:
```bash
pip install flask-swagger-ui
```

2. Add the following to your Flask application to serve the Swagger UI:

```python
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
API_URL = '/static/swagger.yaml'  # Our API url (can be a local file)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Kanakku API"
    }
)

# Register blueprint at URL
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
```

3. Place the `swagger.yaml` file in your application's static folder.

## Updating the Documentation

The `swagger.yaml` file should be updated whenever API endpoints are added, changed, or removed. It is recommended to keep the documentation in sync with the actual implementation to avoid confusion. 