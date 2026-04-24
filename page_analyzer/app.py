import os

from dotenv import load_dotenv
from flask import Flask

from page_analyzer.routes.urls import urls


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.register_blueprint(urls)

    return app


app = create_app()

if __name__ == "__main__":
    app.run()
