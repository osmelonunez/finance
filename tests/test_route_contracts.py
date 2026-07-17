import pytest

from route_manifest import (
    CSRF_TOKEN,
    IGNORED_ENDPOINTS,
    POST_PAYLOADS,
    PUBLIC_ENDPOINTS,
    post_payload,
    route_cases,
)


pytestmark = [pytest.mark.routes, pytest.mark.integration]


def _case_id(case):
    endpoint, method, path = case
    return f"{method} {path} ({endpoint})"


def _registered_cases(application):
    return route_cases(application)


ALL_CASES = _registered_cases(pytest.importorskip("app").app)
POST_CASES = [case for case in ALL_CASES if case[1] == "POST"]
PRIVATE_CASES = [case for case in ALL_CASES if case[0] not in PUBLIC_ENDPOINTS]


def test_every_post_endpoint_has_an_explicit_payload(application):
    post_endpoints = {
        rule.endpoint
        for rule in application.url_map.iter_rules()
        if rule.endpoint not in IGNORED_ENDPOINTS and "POST" in rule.methods
    }
    assert post_endpoints == set(POST_PAYLOADS), (
        f"Missing payloads: {sorted(post_endpoints - set(POST_PAYLOADS))}; "
        f"obsolete payloads: {sorted(set(POST_PAYLOADS) - post_endpoints)}"
    )


def test_route_inventory_has_expected_size(application):
    cases = _registered_cases(application)
    rules = [rule for rule in application.url_map.iter_rules() if rule.endpoint not in IGNORED_ENDPOINTS]
    assert len(rules) == 86
    assert len(cases) == 92


@pytest.mark.parametrize(
    "endpoint,method,path",
    ALL_CASES,
    ids=[_case_id(case) for case in ALL_CASES],
)
def test_every_endpoint_method_responds_without_server_error(admin_client, endpoint, method, path):
    if method == "POST":
        response = admin_client.post(path, data=post_payload(endpoint), follow_redirects=False)
    else:
        response = admin_client.get(path, follow_redirects=False)
    assert response.status_code < 500, f"{method} {path} returned {response.status_code}"
    assert response.status_code in {200, 302, 303, 400, 404}


@pytest.mark.parametrize(
    "endpoint,method,path",
    POST_CASES,
    ids=[_case_id(case) for case in POST_CASES],
)
def test_every_mutating_endpoint_rejects_missing_csrf(admin_client, endpoint, method, path):
    response = admin_client.post(path, data=POST_PAYLOADS[endpoint], follow_redirects=False)
    assert response.status_code == 400
    assert b"Invalid CSRF token" in response.data


@pytest.mark.parametrize(
    "endpoint,method,path",
    PRIVATE_CASES,
    ids=[_case_id(case) for case in PRIVATE_CASES],
)
def test_every_private_endpoint_requires_authentication(client, endpoint, method, path):
    with client.session_transaction() as session:
        session["csrf_token"] = CSRF_TOKEN
    if method == "POST":
        response = client.post(path, data=post_payload(endpoint), follow_redirects=False)
    else:
        response = client.get(path, follow_redirects=False)
    assert response.status_code in {302, 303}
    assert response.headers["Location"].endswith("/login")
