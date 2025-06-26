
def test_init_db_command(runner):
    """
    GIVEN a cli command
    WHEN trying to use it
    THEN check if it properly works
    """
    result = runner.invoke(args=["init-db"])
    assert "Database initialized via migration." in result.output
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