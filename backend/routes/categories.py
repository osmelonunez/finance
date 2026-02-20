from flask import Blueprint, render_template, request, redirect, session, url_for

from db import get_db


categories_bp = Blueprint("categories", __name__)


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
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()
    if not name:
        return redirect("/categories")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO categories (name, description) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                (name, description or None)
            )
            conn.commit()

    return redirect("/categories")


@categories_bp.route("/categories/<int:category_id>/update", methods=["POST"])
def update_category(category_id):
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()
    if not name:
        return redirect("/categories")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE categories SET name=%s, description=%s WHERE id=%s",
                (name, description or None, category_id)
            )
            conn.commit()

    return redirect("/categories")


@categories_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
def delete_category(category_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM records WHERE category_id=%s LIMIT 1", (category_id,))
            if cur.fetchone():
                return redirect("/categories?error=Category%20in%20use.%20It%20cannot%20be%20deleted.")
            cur.execute("DELETE FROM categories WHERE id=%s", (category_id,))
            conn.commit()

    return redirect("/categories")
