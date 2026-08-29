# ---- trusted_oracle/test_deploy_contract.py ----
"""Trusted checks on repeated starts."""

from app.deploy import Deployment


def test_a_repeated_start_does_not_run_the_deployment_again():
    deployment = Deployment()
    deployment.advance("start")
    deployment.advance("start")
    assert deployment.attempts() == 1


def test_a_burst_of_starts_counts_once():
    deployment = Deployment()
    for _ in range(5):
        deployment.advance("start")
    assert deployment.attempts() == 1


def test_the_move_table_holds_no_self_move_into_running():
    deployment = Deployment()
    deployment.advance("start")
    before = deployment.attempts()
    deployment.advance("start")
    assert deployment.attempts() == before
