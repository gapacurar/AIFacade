from sqlalchemy import inspect # inspect: SQLAlchemy utility to introspect database schema
from project.db import db # db: SQLAlchemy database instance for ORM operations

def test_clear_db_command(runner, app):
    """
    GIVEN a CLI command
    WHEN invoking the CLI command to initialize the DB
    THEN check that the DB tables are created properly
    """
    with app.app_context():
        # Ensure DB is clean before test
        db.drop_all()

    result = runner.invoke(args=["init-db"])
    assert "Your database has been created." in result.output
    assert result.exit_code == 0

    with app.app_context():
        inspector = inspect(db.engine)
        assert inspector.get_table_names(), "Tables should exist after init-db"

def test_reset_db_command(runner, app):
    """
    GIVEN a CLI command
    WHEN invoking the command to drop and recreate all tables
    THEN verify it completes successfully and tables exist afterwards
    """
    with app.app_context():
        # Create tables to ensure there is something to drop
        db.create_all()

    result = runner.invoke(args=["reset-tables"])
    assert "Database dropped and re-created." in result.output
    assert result.exit_code == 0

    with app.app_context():
        inspector = inspect(db.engine)
        assert inspector.get_table_names(), "Tables should exist after reset-tables"

def test_delete_tables_command(app, runner):
    """
    GIVEN the Flask CLI runner
    WHEN the 'delete-tables' command is called
    THEN it should drop all tables and print a confirmation message
    """
    # Ensure tables exist before deleting
    with app.app_context():
        db.create_all()
        inspector = inspect(db.engine)
        assert inspector.get_table_names()  # Sanity check

    # Run the command
    result = runner.invoke(args=["delete-tables"])

    # Validate CLI output and that it ran successfully
    assert result.exit_code == 0
    assert "All tables have been dropped." in result.output

    # Confirm tables are now dropped
    with app.app_context():
        inspector = inspect(db.engine)
        assert not inspector.get_table_names()
