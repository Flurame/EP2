from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
import os
import io

from database import init_db


def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")

    app.config.from_object("config.Config")
    init_db(app)
    CORS(app)

    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.requests import requests_bp
    from routes.stat import statistics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(statistics_bp)

    @app.get("/qr/feedback")
    def qr_feedback():
        import qrcode  # pip install qrcode[pil]

        url = app.config.get("FEEDBACK_FORM_URL")
        if not url:
            return {"error": "FEEDBACK_FORM_URL is not set"}, 500

        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")

    @app.route("/")
    @app.route("/index.html")
    def index():
        return send_from_directory("frontend", "index.html")

    @app.route("/<path:path>")
    def catch_all(path):
        if path.startswith("api/"):
            return {"error": "Not found"}, 404

        full_path = os.path.join("frontend", path)
        if os.path.exists(full_path):
            return send_from_directory("frontend", path)

        return send_from_directory("frontend", "index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="192.168.0.21", port=5000, debug=True)
