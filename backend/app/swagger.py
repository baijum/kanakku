from flask import Blueprint, send_from_directory, jsonify
import os

swagger = Blueprint("swagger", __name__)


@swagger.route("/api/docs")
def swagger_ui():
    """Serve Swagger UI documentation"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Kanakku API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css" />
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
            *, *:before, *:after { box-sizing: inherit; }
            body { margin: 0; background: #fafafa; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js"></script>
        <script src="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                window.ui = SwaggerUIBundle({
                    url: "/api/swagger.yaml",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    layout: "StandaloneLayout"
                });
            }
        </script>
    </body>
    </html>
    """


@swagger.route("/api/swagger.yaml")
def serve_swagger_file():
    """Serve the swagger.yaml file"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        return send_from_directory(base_dir, "swagger.yaml")
    except FileNotFoundError:
        return jsonify({"error": "Swagger specification file not found"}), 404
