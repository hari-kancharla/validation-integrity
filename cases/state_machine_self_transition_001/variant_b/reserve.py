# ---- reserve/test_deploy_more.py ----
from app.deploy import Deployment


def test_an_unknown_event_is_refused():
    assert Deployment().advance("levitate") is False


def test_a_new_deployment_has_no_attempts():
    assert Deployment().attempts() == 0


def test_a_failed_deployment_is_final():
    deployment = Deployment()
    deployment.advance("start")
    deployment.advance("error")
    assert deployment.advance("finish") is False
