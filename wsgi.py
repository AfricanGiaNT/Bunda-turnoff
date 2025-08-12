"""
WSGI entry point for the Service Station Operations Bot.
This file serves as an alternative entry point for deployment.
"""

from main import app

# For WSGI servers that expect this variable
application = app

if __name__ == "__main__":
    app.run()
