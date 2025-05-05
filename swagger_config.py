swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Library Automation API",
        "description": "All endpoints for auth, books and users.",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token: 'Bearer {your_token}'"
        }
    },
    "security": [{"Bearer": []}]
}