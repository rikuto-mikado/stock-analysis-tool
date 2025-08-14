from flask import Blueprint, render_template

# create a Blueprint
bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """
    Homepage

    Returns:
    str: Rendered HTML page
    """
    return render_template("index.html", title="Stock Analysis Tool")


@bp.route("/about")
def about():
    """
    About page

    Returns:
    str: Rendered HTML page
    """
    return render_template(
        "index.html",
        title="About - Stock Analysis Tool",
        page_title="About This Application",
        message="This is a stock analysis tool. It provides ticker search, watchlist management, and real-time updates.",
    )
