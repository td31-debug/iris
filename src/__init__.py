"""
Iris ML Training Package

Modules:
- train: Training script with MLflow tracking
- job: Azure ML job submission
- connect_workspace: Azure ML workspace connection
- register_model: Model registration
- mlflow_config: MLflow configuration
"""

__version__ = "0.1.0"
__author__ = "ML Team"

# Import main modules
try:
    from . import train
    from . import job
    from . import connect_workspace
except ImportError:
    pass

__all__ = ["train", "job", "connect_workspace"]
