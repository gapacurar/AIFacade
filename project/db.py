from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import click
from flask.cli import with_appcontext

db = SQLAlchemy()
migrate = Migrate()

@click.command("init-db")
@with_appcontext
def init_db():
    """ Creates the database based on the models."""
    db.create_all()
    print("Your database has been created.")

@click.command("delete-tables")
@with_appcontext
def delete_db():
    """Deletes all the tables."""
    db.drop_all()
    print("All tables have been dropped.")

@click.command("reset-tables")
@with_appcontext
def reset_db_command():
    """Drop and recreate all tables — dev use only! Also deletes alembic_version if exists. """
    db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.session.commit()
    db.drop_all()
    db.create_all()
    print("Database dropped and re-created.")
    



def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(init_db)
    app.cli.add_command(delete_db)







