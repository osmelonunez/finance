import logging
from flask import Blueprint, render_template, request, redirect, session, url_for
from urllib.parse import quote

from db import get_db
from validators import (
    MAX_CATEGORY_DESCRIPTION_LENGTH,
    MAX_CATEGORY_NAME_LENGTH,
    validate_text_length,
)


categories_bp = Blueprint("categories", __name__)
logger = logging.getLogger("finance.categories")


@categories_bp.route("/management/categories")
def management_categories():
    if session.get("role") not in {"admin", "editor"}:
        return redirect(url_for("dashboard.dashboard"))
    return redirect("/categories")


@categories_bp.route("/categories")
def categories():
    error = request.args.get("error")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, description FROM categories ORDER BY name")
            categories = cur.fetchall()

    return render_template(
        "categories.html",
        categories=categories,
        current_page="categories",
        error=error
    )


@categories_bp.route("/categories/add", methods=["POST"])
def add_category():
    name, name_error = validate_text_length(
        request.form.get("name"),
        "Category name",
        MAX_CATEGORY_NAME_LENGTH,
        required=True,
    )
    description, description_error = validate_text_length(
        request.form.get("description"),
        "Category description",
        MAX_CATEGORY_DESCRIPTION_LENGTH,
    )
    if name_error or description_error:
        return redirect(f"/categories?error={quote(name_error or description_error)}")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO categories (name, description) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                (name, description or None)
            )
            inserted = cur.rowcount
            conn.commit()
            logger.info(
                "category_create user=%s name=%s inserted=%s",
                session.get("user_name"),
                name,
                inserted,
            )

    return redirect("/categories")


@categories_bp.route("/categories/<int:category_id>/update", methods=["POST"])
def update_category(category_id):
    name, name_error = validate_text_length(
        request.form.get("name"),
        "Category name",
        MAX_CATEGORY_NAME_LENGTH,
        required=True,
    )
    description, description_error = validate_text_length(
        request.form.get("description"),
        "Category description",
        MAX_CATEGORY_DESCRIPTION_LENGTH,
    )
    if name_error or description_error:
        return redirect(f"/categories?error={quote(name_error or description_error)}")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE categories SET name=%s, description=%s WHERE id=%s",
                (name, description or None, category_id)
            )
            updated = cur.rowcount
            conn.commit()
            logger.info(
                "category_update user=%s id=%s name=%s updated=%s",
                session.get("user_name"),
                category_id,
                name,
                updated,
            )

    return redirect("/categories")


@categories_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
def delete_category(category_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM records WHERE category_id=%s LIMIT 1", (category_id,))
            if cur.fetchone():
                logger.info(
                    "category_delete_blocked user=%s id=%s reason=in_use",
                    session.get("user_name"),
                    category_id,
                )
                return redirect("/categories?error=Category%20in%20use.%20It%20cannot%20be%20deleted.")
            cur.execute("DELETE FROM categories WHERE id=%s", (category_id,))
            deleted = cur.rowcount
            conn.commit()
            logger.info(
                "category_delete user=%s id=%s deleted=%s",
                session.get("user_name"),
                category_id,
                deleted,
            )

    return redirect("/categories")
