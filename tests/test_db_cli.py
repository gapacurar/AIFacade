
def test_clear_db_command(runner):
    """
    GIVEN a cli command
    WHEN trying to clear all the entries in the db without recreating the db
    THEN check if it properly works
    """
    result = runner.invoke(args=["clear-db"])
    assert "The DB has been cleared." in result.output
    assert result.exit_code == 0


def test_reset_db_command(runner):
    """
    GIVEN a cli command
    WHEN trying to use it
    THEN check if it properly works
    """
    result = runner.invoke(args=["reset-db"])
    assert "Database dropped and re-created." in result.output
    assert result.exit_code == 0