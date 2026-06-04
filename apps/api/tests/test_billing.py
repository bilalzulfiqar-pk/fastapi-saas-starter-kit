from __future__ import annotations


def test_billing_plans_exist(client):
    response = client.get("/api/v1/billing/plans")
    assert response.status_code == 200
    assert [plan["slug"] for plan in response.json()["data"]["plans"]] == ["free", "pro", "business"]

