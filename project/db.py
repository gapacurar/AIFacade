from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, inspect, text
import click
from flask.cli import with_appcontext

db = SQLAlchemy()
migrate = Migrate()


            
@click.command("reset-db")
@with_appcontext
def reset_db_command():
    """Drop and recreate all tables — dev use only! Also deletes alembic_version if exists. """
    db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.session.commit()
    db.drop_all()
    db.create_all()
    print("⚠️ Database dropped and re-created.")
    
@click.command("clear-db")
@with_appcontext
def clear_db_command():
    meta = MetaData()
    with db.engine.connect() as conn:
        meta.reflect(bind=db.engine)
        trans = conn.begin()
        for table in reversed(meta.sorted_tables):
            conn.execute(table.delete())
        trans.commit()
        print("✅ The DB has been cleared.")


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(clear_db_command)







