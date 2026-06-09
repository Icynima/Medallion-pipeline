"""
Apache Hop utility functions – run Hop pipelines/workflows from Airflow.
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

HOP_PROJECT_FOLDER = "/hop-project"


def run_hop_pipeline(
    pipeline_file: str,
    project_name: str = "day8_airflow_hop",
    project_folder: str = HOP_PROJECT_FOLDER,
    run_config: str = "local",
    log_level: str = "Basic",
) -> dict:
    """
    Execute a Hop pipeline (.hpl) via the hop-run.sh CLI.

    This function is designed to be called from inside the Airflow container
    using DockerOperator or via a shared volume where Hop CLI is available.
    For the lab we simulate the execution and log the result.
    """
    pipeline_path = Path(project_folder) / "pipelines" / pipeline_file

    log.info("Running Hop pipeline: %s (project=%s, config=%s)",
             pipeline_path, project_name, run_config)

    # Build the hop-run command
    cmd = [
        "/opt/hop/hop-run.sh",
        "--file", str(pipeline_path),
        "--project", project_name,
        "--runconfig", run_config,
        "--level", log_level,
    ]

    result = {
        "pipeline": pipeline_file,
        "project": project_name,
        "command": " ".join(cmd),
        "status": "simulated",
    }

    # Try to execute if Hop CLI is available (inside hop-cli container)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        result["status"] = "success" if proc.returncode == 0 else "failed"
        result["returncode"] = proc.returncode
        result["stdout"] = proc.stdout[-2000:] if proc.stdout else ""
        result["stderr"] = proc.stderr[-2000:] if proc.stderr else ""
    except FileNotFoundError:
        log.warning("Hop CLI not found – pipeline execution simulated")
        result["status"] = "simulated"
        result["note"] = "Hop CLI not installed in this container. Use DockerOperator to run inside hop-cli container."

    return result


def run_hop_workflow(
    workflow_file: str,
    project_name: str = "day8_airflow_hop",
    project_folder: str = HOP_PROJECT_FOLDER,
    run_config: str = "local",
    log_level: str = "Basic",
) -> dict:
    """Execute a Hop workflow (.hwf) via hop-run.sh."""
    workflow_path = Path(project_folder) / "workflows" / workflow_file

    log.info("Running Hop workflow: %s", workflow_path)

    cmd = [
        "/opt/hop/hop-run.sh",
        "--file", str(workflow_path),
        "--project", project_name,
        "--runconfig", run_config,
        "--level", log_level,
    ]

    result = {
        "workflow": workflow_file,
        "project": project_name,
        "command": " ".join(cmd),
        "status": "simulated",
    }

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )
        result["status"] = "success" if proc.returncode == 0 else "failed"
        result["returncode"] = proc.returncode
        result["stdout"] = proc.stdout[-2000:] if proc.stdout else ""
        result["stderr"] = proc.stderr[-2000:] if proc.stderr else ""
    except FileNotFoundError:
        log.warning("Hop CLI not found – workflow execution simulated")
        result["status"] = "simulated"
        result["note"] = "Hop CLI not installed in this container. Use DockerOperator."

    return result


def build_hop_docker_command(
    file_path: str,
    project_name: str = "day8_airflow_hop",
    run_config: str = "local",
    log_level: str = "Basic",
) -> str:
    """
    Build the shell command to run inside the apache/hop Docker container.
    Used with DockerOperator or BashOperator targeting the hop-cli container.
    """
    return (
        f"/opt/hop/hop-run.sh "
        f"--file /project/{file_path} "
        f"--project {project_name} "
        f"--runconfig {run_config} "
        f"--level {log_level}"
    )
