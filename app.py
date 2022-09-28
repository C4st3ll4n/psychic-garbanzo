import base64

from flask import Flask, g
from flask.sessions import SecureCookieSessionInterface
from flask_migrate import Migrate
from flask_login import LoginManager
from routes import user_blueprint
import models

app = Flask(__name__)

app.config['SECRET_KEY'] = "rl3D4rG5W4THv0RsiGVj7TVMWgK1SmDEU1c2FjNrwkI"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///./database/user.db'
login_manager = LoginManager(app)
models.init_app(app)

app.register_blueprint(user_blueprint)

migrate = Migrate(app, models.db)


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get("Authorization")
    if api_key:
        api_key = api_key.replace("Basic ", "", 1)
        user = models.User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    return None


class CustomSessionInterface(SecureCookieSessionInterface):
    def save_session(self, *args, **kwargs):
        if g.get('login_via_headers'):
            return
        return super(CustomSessionInterface, self).save_session(*args, **kwargs)


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")

