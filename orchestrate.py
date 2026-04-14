"""
Complete MLOps Pipeline Orchestrator
Runs one or more Vertex AI training submissions and optional monitoring.
"""

import argparse
import os
import subprocess
import sys
import time

PROJECT_ID = "mlops-493014"
REGION = "us-central1"
FRAMEWORK_COMMANDS = {
    "scikit-learn": ("SCIKIT-LEARN", "src/vertex_train.py", "resource name:"),
    "tensorflow": ("TENSORFLOW", "src/vertex_train_tensorflow.py", "resource name:"),
    "pytorch": ("PYTORCH", "src/vertex_train_pytorch.py", "resource name:"),
}


class Colors:
    _ENABLED = sys.stdout.isatty() and os.environ.get("TERM")
    GREEN = '\033[92m' if _ENABLED else ''
    YELLOW = '\033[93m' if _ENABLED else ''
    RED = '\033[91m' if _ENABLED else ''
    BLUE = '\033[94m' if _ENABLED else ''
    END = '\033[0m' if _ENABLED else ''


def run_command(cmd, timeout=120, env=None):
    """Run a command and capture its output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except Exception as exc:
        return -1, "", str(exc)


def setup_environment(credentials_path=None):
    """Validate and configure the credential path used by the workflow."""
    print(f"\n{Colors.BLUE}=== ENVIRONMENT SETUP ==={Colors.END}")

    credential_candidate = (
        credentials_path
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or "./gcp-key.json"
    )

    if not os.path.exists(credential_candidate):
        print(f"{Colors.RED}ERROR: Missing credentials file: {credential_candidate}{Colors.END}")
        return False

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_candidate
    print(f"{Colors.GREEN}Credentials configured: {credential_candidate}{Colors.END}")
    print(f"{Colors.GREEN}Python executable: {sys.executable}{Colors.END}")
    return True


def submit_training_job(framework, timeout=300):
    """Submit a single framework training job to Vertex AI."""
    label, script_path, success_phrase = FRAMEWORK_COMMANDS[framework]
    print(f"\n{Colors.BLUE}=== {label} TRAINING ==={Colors.END}")
    print(f"Submitting {framework} training job...")

    cmd = [sys.executable, script_path]
    code, stdout, stderr = run_command(cmd, timeout=timeout, env=os.environ.copy())

    combined_output = f"{stdout}\n{stderr}".lower()
    succeeded = code == 0 and success_phrase in combined_output

    if succeeded:
        print(f"{Colors.GREEN}{framework} job submitted{Colors.END}")
    else:
        print(f"{Colors.RED}Failed to submit {framework} job{Colors.END}")
        failure_output = stderr.strip() or stdout.strip() or "No command output captured"
        print(failure_output[:1000])

    return succeeded


def list_training_jobs(limit=5):
    """List recent training jobs using the monitoring helper."""
    print(f"\n{Colors.BLUE}=== MONITORING JOBS ==={Colors.END}")
    print("Recent training jobs:\n")

    cmd = [sys.executable, "scripts/monitor_training.py", "--list", "--limit", str(limit)]
    code, stdout, stderr = run_command(cmd, timeout=120, env=os.environ.copy())

    if stdout.strip():
        print(stdout.strip())
    elif stderr.strip():
        print(stderr.strip())
    else:
        print("No training jobs were returned.")

    return code == 0


def show_summary(results):
    """Show a short summary of the supported workflows."""
    print(f"\n{Colors.BLUE}=== MLOPS PIPELINE SUMMARY ==={Colors.END}\n")

    print(
        f"""
{Colors.GREEN}AVAILABLE WORKFLOWS:{Colors.END}
    - Scikit-learn training
    - TensorFlow/Keras training
    - PyTorch training
    - Vertex AI job monitoring
    - Model deployment helpers
    - Vertex AI Pipelines orchestration

{Colors.YELLOW}GCP CONFIGURATION:{Colors.END}
    - Project: {PROJECT_ID}
    - Region: {REGION}
    - Bucket: gs://{PROJECT_ID}-bucket

{Colors.YELLOW}JENKINS ENTRYPOINT:{Colors.END}
    - python orchestrate.py --framework all
    - python orchestrate.py --framework scikit-learn --skip-monitor
    - python orchestrate.py --framework tensorflow --skip-monitor
    - python orchestrate.py --framework pytorch --skip-monitor
"""
    )

    print(f"{Colors.BLUE}=== TEST RESULTS ==={Colors.END}")
    for framework, status in results.items():
        status_text = f"{Colors.GREEN}PASS{Colors.END}" if status else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {framework.upper()}: {status_text}")

    passed = sum(1 for value in results.values() if value)
    total = len(results)
    print(f"\n{Colors.GREEN}Result: {passed}/{total} submissions passed{Colors.END}\n")


def main():
    parser = argparse.ArgumentParser(description="Run one or more Vertex AI training submissions")
    parser.add_argument(
        "--framework",
        choices=["all", *FRAMEWORK_COMMANDS.keys()],
        default="all",
        help="Framework to run (default: all)",
    )
    parser.add_argument(
        "--credentials-path",
        default=None,
        help="Optional path to the GCP service account JSON file",
    )
    parser.add_argument(
        "--skip-monitor",
        action="store_true",
        help="Skip listing recent jobs after submission",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of jobs to show when monitoring is enabled",
    )
    args = parser.parse_args()

    print(f"\n{Colors.BLUE}========================================{Colors.END}")
    print(f"{Colors.BLUE}MLOPS PIPELINE - COMPLETE EXECUTION{Colors.END}")
    print(f"{Colors.BLUE}========================================{Colors.END}")

    if not setup_environment(args.credentials_path):
        print(f"{Colors.RED}Environment setup failed{Colors.END}")
        sys.exit(1)

    selected_frameworks = (
        list(FRAMEWORK_COMMANDS.keys()) if args.framework == "all" else [args.framework]
    )

    results = {}
    for index, framework in enumerate(selected_frameworks):
        results[framework] = submit_training_job(framework)
        if index < len(selected_frameworks) - 1:
            time.sleep(2)

    if not args.skip_monitor:
        list_training_jobs(limit=args.limit)

    show_summary(results)

    if all(results.values()):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
