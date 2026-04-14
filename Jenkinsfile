pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    parameters {
        choice(
            name: 'FRAMEWORK',
            choices: ['all', 'scikit-learn', 'tensorflow', 'pytorch'],
            description: 'Choose which training workflow to run'
        )
        booleanParam(
            name: 'MONITOR_JOBS',
            defaultValue: true,
            description: 'List recent Vertex AI jobs after submission'
        )
        booleanParam(
            name: 'DEPLOY_MODEL',
            defaultValue: false,
            description: 'Register a model artifact if MODEL_ARTIFACT_PATH is provided'
        )
        string(
            name: 'MODEL_ARTIFACT_PATH',
            defaultValue: '',
            description: 'Optional gs:// path to a trained model artifact'
        )
        string(
            name: 'MODEL_VERSION',
            defaultValue: 'v1',
            description: 'Version label used during model registration'
        )
    }

    environment {
        VENV_DIR = '.venv'
        PYTHON_BIN = 'python3'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                echo '🔄 Checking out code...'
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                echo '📦 Setting up Python environment...'
                sh '''
                    set -eu
                    "$PYTHON_BIN" -m venv "$VENV_DIR"
                    . "$VENV_DIR/bin/activate"
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Validate Credentials') {
            steps {
                echo '🔐 Validating GCP credentials...'
                withCredentials([file(credentialsId: 'gcp-vertex-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        set -eu
                        . "$VENV_DIR/bin/activate"
                        python - <<'PY'
from google.auth import default
creds, project = default()
email = getattr(creds, 'service_account_email', 'unknown')
print(f'✅ Authenticated as: {email}')
print(f'✅ Project: {project}')
PY
                    '''
                }
            }
        }

        stage('Submit Training Job') {
            steps {
                echo "🤖 Submitting ${params.FRAMEWORK} training workflow..."
                withCredentials([file(credentialsId: 'gcp-vertex-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        set -eu
                        . "$VENV_DIR/bin/activate"
                        python orchestrate.py --framework "$FRAMEWORK" --skip-monitor
                    '''
                }
            }
        }

        stage('Monitor Recent Jobs') {
            when {
                expression { return params.MONITOR_JOBS }
            }
            steps {
                echo '📋 Listing recent Vertex AI jobs...'
                withCredentials([file(credentialsId: 'gcp-vertex-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        set -eu
                        . "$VENV_DIR/bin/activate"
                        python scripts/monitor_training.py --list --limit 10
                    '''
                }
            }
        }

        stage('Optional Deploy') {
            when {
                expression { return params.DEPLOY_MODEL && params.FRAMEWORK != 'all' && params.MODEL_ARTIFACT_PATH?.trim() }
            }
            steps {
                echo '🚀 Registering the provided model artifact...'
                withCredentials([file(credentialsId: 'gcp-vertex-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        set -eu
                        . "$VENV_DIR/bin/activate"
                        python scripts/deploy_model.py upload \
                            --model-path "$MODEL_ARTIFACT_PATH" \
                            --framework "$FRAMEWORK" \
                            --version "$MODEL_VERSION"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ Jenkins training pipeline completed successfully'
        }
        failure {
            echo '❌ Jenkins training pipeline failed'
        }
        always {
            echo '🧹 Cleaning up workspace...'
            sh 'rm -rf "$VENV_DIR"'
        }
    }
}
