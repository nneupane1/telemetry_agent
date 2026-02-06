from pathlib import Path


def test_deployment_artifacts_exist_and_non_empty():
    files = [
        Path("deployments/docker-compose.yaml"),
        Path("deployments/k8s/api-deployment.yaml"),
        Path("deployments/terraform/main.tf"),
    ]
    for file in files:
        assert file.exists()
        assert file.stat().st_size > 0
