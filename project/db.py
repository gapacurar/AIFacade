from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize DB using Flask-Migrate (apply latest migrations)."""
        from flask_migrate import upgrade
        with app.app_context():
            upgrade()
            print("Database initialized via migration.")
    @app.cli.command("reset-db")
    def reset_db_command():
        """Drop and recreate all tables — dev use only!"""
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("⚠️ Database dropped and re-created.")
    
    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_db_command)














