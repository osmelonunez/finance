import pytest


pytestmark = [pytest.mark.routes, pytest.mark.integration]


@pytest.mark.parametrize(
    "role,path,allowed",
    [
        ("admin", "/management", True),
        ("editor", "/management", True),
        ("user", "/management", False),
        ("admin", "/management/users", True),
        ("editor", "/management/users", False),
        ("user", "/management/users", False),
        ("admin", "/management/backups", True),
        ("editor", "/management/backups", False),
        ("user", "/management/backups", False),
        ("admin", "/categories", True),
        ("editor", "/categories", True),
        ("user", "/categories", False),
        ("admin", "/payment-methods/kpi", True),
        ("editor", "/payment-methods/kpi", True),
        ("user", "/payment-methods/kpi", False),
        ("admin", "/payment-methods/relationships", True),
        ("editor", "/payment-methods/relationships", True),
        ("user", "/payment-methods/relationships", False),
        ("admin", "/payment-methods/banks/1", True),
        ("editor", "/payment-methods/banks/1", True),
        ("user", "/payment-methods/banks/1", False),
    ],
)
def test_role_access_matrix(client, login_as, role, path, allowed):
    login_as(client, role)
    response = client.get(path, follow_redirects=False)
    if allowed:
        assert response.status_code == 200
    else:
        assert response.status_code in {302, 303}
        assert response.headers["Location"].endswith("/")
