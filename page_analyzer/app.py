import os
from datetime import datetime
from urllib.parse import urlparse

import validators
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    Response,
    url_for,
)

from .models import URL

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.context_processor
def inject_now() -> dict[str, datetime]:
    return {"now": datetime.now()}


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.post("/urls")
def add_url() -> Response | str:
    url = request.form.get("url", "").strip()
    
    # Валидация
    errors = []
    
    if not url:
        errors.append("URL не может быть пустым")
    elif len(url) > 255:
        errors.append("URL не должен превышать 255 символов")
    elif not validators.url(url):
        errors.append("Некорректный URL")
    
    if errors:
        for error in errors:
            flash(error, "danger")
        return render_template("index.html"), 422
    
    # Проверка на существование (с нормализацией)
    parsed = urlparse(url)
    normalized_name = f"{parsed.scheme}://{parsed.netloc}"
    existing_url = URL.find_by_name(normalized_name)
    if existing_url:
        flash("Страница уже существует", "info")
        return redirect(url_for("show_url", id=existing_url["id"]))
    
    # Создание нового URL
    new_url = URL.create(normalized_name)
    if new_url:
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("show_url", id=new_url["id"]))
    else:
        flash("Не удалось добавить страницу", "danger")
        return render_template("index.html"), 422


@app.get("/urls")
def urls_list() -> str:
    urls = URL.get_all()
    return render_template("urls.html", urls=urls)


@app.get("/urls/<int:url_id>")
def show_url(url_id: int) -> Response | str:
    url = URL.find_by_id(url_id)
    if not url:
        flash("Страница не найдена", "danger")
        return redirect(url_for("urls_list"))
    return render_template("url.html", url=url)


if __name__ == "__main__":
    app.run()
