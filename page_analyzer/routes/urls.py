from datetime import datetime
from urllib.parse import urlparse

import validators
from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.models import URL, UrlCheck

urls = Blueprint("urls", __name__, template_folder="templates")


@urls.app_context_processor
def inject_now() -> dict[str, datetime]:
    return {"now": datetime.now()}


@urls.route("/")
def index() -> str:
    return render_template("index.html")


@urls.post("/urls")
def add_url() -> Response | str | tuple[str, int]:
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
    normalized_name = f"{parsed.netloc}{parsed.path}"
    existing_url = URL.find_by_name(normalized_name)
    if existing_url:
        flash("Страница уже существует", "info")
        return redirect(url_for("urls.show_url", url_id=existing_url["id"]))

    # Создание нового URL
    new_url = URL.create(normalized_name)
    if new_url:
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("urls.show_url", url_id=new_url["id"]))
    else:
        flash("Не удалось добавить страницу", "danger")
        return render_template("index.html"), 422


@urls.get("/urls")
def urls_list() -> str:
    urls = URL.get_all()
    return render_template("urls.html", urls=urls)


@urls.get("/urls/<int:url_id>")
def show_url(url_id: int) -> Response | str:
    url = URL.find_by_id(url_id)
    if not url:
        flash("Страница не найдена", "danger")
        return redirect(url_for("urls.urls_list"))
    
    checks = UrlCheck.get_by_url_id(url_id)
    return render_template("url.html", url=url, checks=checks)


@urls.post("/urls/<int:url_id>/checks")
def create_check(url_id: int) -> Response | str:
    url = URL.find_by_id(url_id)
    if not url:
        flash("Страница не найдена", "danger")
        return redirect(url_for("urls.urls_list"))
    
    check = UrlCheck.create(url_id)
    if check:
        flash("Страница успешно проверена", "success")
    else:
        flash("Произошла ошибка при проверке", "danger")
    
    return redirect(url_for("urls.show_url", url_id=url_id))
