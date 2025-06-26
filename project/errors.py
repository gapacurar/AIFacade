from flask import Blueprint, render_template

bp = Blueprint('errors', __name__)

# Handle 404 errors
@bp.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404
# Handle 505 errors
@bp.errorhandler(505)
def http_version_not_supported(e):
    return render_template("errors/505.html"), 505

