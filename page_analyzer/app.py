import os

from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)
load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


def main():
    register_blueprints()
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug)


def register_blueprints():
    from page_analyzer.routes.urls import urls

    app.register_blueprint(urls)


if __name__ == "__main__":
    main()
else:
    register_blueprints()
