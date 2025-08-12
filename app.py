"""
App entry point for the Service Station Operations Bot.
This file serves as an alternative entry point for deployment.
"""

from main import app

# For platforms that expect this variable
application = app

if __name__ == "__main__":
    app.run()
