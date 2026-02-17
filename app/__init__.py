from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
oauth = OAuth()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    oauth.init_app(app)

    # Register Google OAuth client
    if app.config.get('GOOGLE_CLIENT_ID'):
        oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )

    from app.models import User, Event, EventParticipation, KnowledgeUnit, Certificate, Library, Follow, Activity

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.events import events_bp
    from app.routes.profiles import profiles_bp
    from app.routes.certificates import certificates_bp
    from app.routes.library import library_bp
    from app.routes.scan import scan_bp
    from app.routes.settings import settings_bp
    from app.routes.collect import collect_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(certificates_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(collect_bp)

    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    @app.route('/verify/<verification_hash>')
    def verify_certificate(verification_hash):
        from flask import render_template
        cert = Certificate.query.filter_by(verification_hash=verification_hash).first()
        return render_template('certificates/verify.html', certificate=cert)

    @app.route('/p/<int:user_id>')
    def profile_shortlink(user_id):
        from flask import redirect, url_for, request
        # Forward query params
        return redirect(url_for('profiles.view_profile', user_id=user_id, **request.args))

    @app.route('/')
    def index():
        from flask import redirect, url_for, render_template
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.dashboard'))
        # Landing page for non-authenticated users
        stats = {
            'events': Event.query.count(),
            'certificates': Certificate.query.count(),
            'users': User.query.count()
        }
        return render_template('landing.html', stats=stats)

    return app
