# ---- tests/test_deploy.py ----
from app.deploy import Deployment


def test_a_new_deployment_is_queued():
    assert Deployment().state() == "queued"


def test_a_queued_deployment_starts():
    deployment = Deployment()
    assert deployment.advance("start") is True
    assert deployment.state() == "running"


def test_a_running_deployment_can_finish():
    deployment = Deployment()
    deployment.advance("start")
    assert deployment.advance("finish") is True


def test_a_running_deployment_can_fail():
    deployment = Deployment()
    deployment.advance("start")
    assert deployment.advance("error") is True
    assert deployment.state() == "failed"


def test_a_finished_deployment_is_final():
    deployment = Deployment()
    deployment.advance("start")
    deployment.advance("finish")
    assert deployment.advance("start") is False


def test_a_started_deployment_counts_one_attempt():
    deployment = Deployment()
    deployment.advance("start")
    assert deployment.attempts() == 1
