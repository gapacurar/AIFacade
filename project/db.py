"""
db.py
This module sets up the database layer for a Flask application using SQLAlchemy and Flask-Migrate.
It provides CLI commands for initializing, deleting, and resetting database tables, and integrates
these commands with the Flask app.
Modules and Objects:
--------------------
- db: SQLAlchemy database instance for ORM operations.
CLI Commands:
-------------
- init_db: Creates all database tables based on the defined models.
- delete_tables: Drops all tables from the database.
- reset_tables_command: Drops all tables, removes the Alembic version table if it exists,
    and recreates all tables. Intended for development use only.
Functions:
----------
- init_app(app): Initializes the database and migration objects with the Flask app,
    and registers the CLI commands for database management.
Usage:
------
Import and call `init_app(app)` in your Flask application factory to enable database
integration and CLI commands.
Example:
--------
        def create_app():
                app = Flask(__name__)
                # ... other setup ...
                init_app(app)
                return app
"""

from flask_sqlalchemy import SQLAlchemy
# SQLAlchemy: Provides ORM capabilities for database operations in Flask

from sqlalchemy import text
# text: Allows execution of raw SQL statements (used for dropping alembic_version table)

import click
# click: Used to create command-line interface (CLI) commands for Flask

from flask.cli import with_appcontext
# with_appcontext: Ensures CLI commands run within the Flask application context

db = SQLAlchemy()
# db: SQLAlchemy database instance used throughout the app for ORM operations


@click.command("init-db")
@with_appcontext
def init_db():
    """ Creates the database based on the models."""
    db.create_all()
    print("Your database has been created.")

@click.command("delete-tables")
@with_appcontext
def delete_tables():
    """Deletes all the tables."""
    db.drop_all()
    print("All tables have been dropped.")

@click.command("reset-tables")
@with_appcontext
def reset_tables_command():
    """Drop and recreate all tables — dev use only! Also deletes alembic_version if exists. """
    db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.session.commit()
    db.drop_all()
    db.create_all()
    print("Database dropped and re-created.")
    



def init_app(app):
    db.init_app(app)
    app.cli.add_command(reset_tables_command)
    app.cli.add_command(init_db)
    app.cli.add_command(delete_tables)







