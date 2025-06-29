
def test_clear_db_command(runner):
    """
    GIVEN a cli command
    WHEN using the cli command to initialize the db
    THEN check if it properly works
    """
    result = runner.invoke(args=["init-db"])
    assert "Your database has been created." in result.output
    assert result.exit_code == 0


def test_reset_db_command(runner):
    """
    GIVEN a cli command
    WHEN trying to use the command to drop all tables and to create them again
    THEN check if it properly works
    """
    result = runner.invoke(args=["reset-tables"])
    assert "Database dropped and re-created." in result.output
    assert result.exit_code == 0