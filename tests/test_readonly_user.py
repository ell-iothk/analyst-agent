import pytest

from analyst.data.readonly_user import check_safe, mariadb_statements, postgres_statements


def test_safe_name_and_password_pass():
    check_safe("analyst_ro", "change_me_readonly")


@pytest.mark.parametrize(
    ("user", "password"),
    [
        ("analyst_ro", "x'; DROP TABLE orders; --"),
        ("analyst_ro; DROP TABLE orders", "change_me_readonly"),
        ("analyst_ro", "short"),
        ("analyst_ro", "back\\slash123"),
    ],
)
def test_unsafe_values_are_rejected(user, password):
    with pytest.raises(ValueError):
        check_safe(user, password)


def test_postgres_account_only_gets_select_and_read_only_mode():
    sql = " ".join(postgres_statements("ro", "secret_pw", "olist"))
    assert "GRANT SELECT" in sql
    assert "default_transaction_read_only = on" in sql
    assert "INSERT" not in sql and "ALL PRIVILEGES" not in sql


def test_mariadb_account_only_gets_select():
    sql = " ".join(mariadb_statements("ro", "secret_pw", "olist"))
    assert "GRANT SELECT ON olist.*" in sql
    assert "ALL" not in sql
