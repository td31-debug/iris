"""
Monitor Vertex AI Training Jobs
Displays job status, logs, and metrics
"""

from google.cloud import aiplatform
from google.auth import default as google_auth_default
import argparse
from datetime import datetime

PROJECT_ID = "mlops-493014"
REGION = "us-central1"

# Load credentials
credentials, project = google_auth_default()
aiplatform.init(project=PROJECT_ID, location=REGION, credentials=credentials)

def list_jobs(limit=10):
    """List recent training jobs"""
    print(f"\nRecent {limit} Training Jobs:\n")
    
    jobs = aiplatform.CustomJob.list(
        filter="state != JOB_STATE_CANCELLED",
        order_by="create_time desc"
    )
    
    if not jobs:
        print("No training jobs found in Vertex AI for this project/region.")
        return

    count = 0
    for job in jobs:
        if count >= limit:
            break
        
        status = "SUCCESS" if job.state.name == "JOB_STATE_SUCCEEDED" else \
             "FAILED" if job.state.name == "JOB_STATE_FAILED" else \
             "RUNNING" if job.state.name == "JOB_STATE_RUNNING" else "OTHER"
        
        created = job.create_time.strftime("%Y-%m-%d %H:%M:%S") if job.create_time else "N/A"
        print(f"{status} {job.display_name}")
        print(f"   ID: {job.name.split('/')[-1]}")
        print(f"   Status: {job.state.name}")
        print(f"   Created: {created}")
        print()
        count += 1

def get_job_details(job_id):
    """Get detailed status of a specific job"""
    print(f"\nJob Details: {job_id}\n")
    
    try:
        job = aiplatform.CustomJob(job_id)
        
        status = {
            "JOB_STATE_PENDING": "Pending",
            "JOB_STATE_RUNNING": "Running",
            "JOB_STATE_SUCCEEDED": "Succeeded",
            "JOB_STATE_FAILED": "Failed",
            "JOB_STATE_CANCELLED": "Cancelled"
        }
        
        print(f"Name: {job.display_name}")
        print(f"Status: {status.get(job.state.name, job.state.name)}")
        print(f"Created: {job.create_time}")
        print(f"Started: {job.start_time if job.start_time else 'Not started'}")
        print(f"Ended: {job.end_time if job.end_time else 'Still running'}")
        print(f"Machine Type: {job.machine_spec.machine_type if job.machine_spec else 'N/A'}")
        
        # Show error message if failed
        if job.state.name == "JOB_STATE_FAILED" and job.error:
            print(f"\nError: {job.error.message}")
        
        # Show output location
        if job.job_spec and job.job_spec.output_spec:
            print(f"Output Location: {job.job_spec.output_spec.gcs_output_directory}")
            
    except Exception as e:
        print(f"Error retrieving job: {e}")

def get_job_logs(job_id, limit=50):
    """Get logs for a training job"""
    print(f"\nJob Logs (last {limit} lines):\n")
    
    try:
        job = aiplatform.CustomJob(job_id)
        
        # Get logs from Cloud Logging
        try:
            from google.cloud import logging as cloud_logging
        except ImportError:
            print("google-cloud-logging is not installed. Install it with: pip install google-cloud-logging")
            return

        client = cloud_logging.Client(project=PROJECT_ID, credentials=credentials)
        
        # Construct log filter
        filter_str = f'resource.type="ml.googleapis.com/Job" AND resource.labels.job_id="{job_id}"'
        entries = list(client.list_entries(filter_=filter_str, max_results=limit))
        
        if not entries:
            print("No logs found. Job may still be initializing.")
            return
        
        for entry in reversed(entries[-limit:]):
            timestamp = entry.timestamp.strftime("%H:%M:%S") if entry.timestamp else "N/A"
            print(f"[{timestamp}] {entry.payload}")
            
    except Exception as e:
        print(f"Could not retrieve logs: {e}")
        print("   Jobs may have ended. Check GCS outputs or Vertex AI console.")

def main():
    parser = argparse.ArgumentParser(description="Monitor Vertex AI Training Jobs")
    parser.add_argument("--list", action="store_true", help="List recent jobs")
    parser.add_argument("--job-id", type=str, help="Get details for specific job ID")
    parser.add_argument("--logs", action="store_true", help="Get job logs (use with --job-id)")
    parser.add_argument("--limit", type=int, default=10, help="Number of jobs to list (default: 10)")
    
    args = parser.parse_args()
    
    if args.job_id:
        get_job_details(args.job_id)
        if args.logs:
            get_job_logs(args.job_id, limit=args.limit)
    else:
        list_jobs(limit=args.limit)

if __name__ == "__main__":
    main()
