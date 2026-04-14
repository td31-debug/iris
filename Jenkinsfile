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
            name: 'LOCAL_ONLY',
            defaultValue: true,
            description: 'Run only local setup, tests, and training on this machine without cloud authentication or cloud jobs'
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
        string(
            name: 'VERTEX_PIPELINE_RUN',
            defaultValue: '',
            description: 'Optional Vertex pipeline console URL, resource name, or run id to inspect instead of submitting a new training job'
        )
        string(
            name: 'PYTHON_CMD',
            defaultValue: '',
            description: 'Optional Python command for Jenkins agents, for example py -3.10, python, or a full path to python.exe'
        )
    }

    environment {
        VENV_DIR = '.venv'
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
                script {
                    if (isUnix()) {
                        sh '''
                            set -eu
                            python3 -m venv "$VENV_DIR"
                            . "$VENV_DIR/bin/activate"
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                            @echo off
                            setlocal EnableDelayedExpansion
                            set "PYTHON_TO_USE=%PYTHON_CMD%"
                            if defined PYTHON_TO_USE (
                                call !PYTHON_TO_USE! --version >nul 2>nul || set "PYTHON_TO_USE="
                            )
                            if not defined PYTHON_TO_USE (
                                where py >nul 2>nul && set "PYTHON_TO_USE=py -3.10"
                            )
                            if not defined PYTHON_TO_USE (
                                where python >nul 2>nul && set "PYTHON_TO_USE=python"
                            )
                            if not defined PYTHON_TO_USE if exist "%LOCALAPPDATA%\\Programs\\Python\\Python310\\python.exe" set "PYTHON_TO_USE=%LOCALAPPDATA%\\Programs\\Python\\Python310\\python.exe"
                            if not defined PYTHON_TO_USE if exist "%LOCALAPPDATA%\\Programs\\Python\\Python311\\python.exe" set "PYTHON_TO_USE=%LOCALAPPDATA%\\Programs\\Python\\Python311\\python.exe"
                            if not defined PYTHON_TO_USE if exist "C:\\Python310\\python.exe" set "PYTHON_TO_USE=C:\\Python310\\python.exe"
                            if not defined PYTHON_TO_USE if exist "C:\\Python311\\python.exe" set "PYTHON_TO_USE=C:\\Python311\\python.exe"
                            if not defined PYTHON_TO_USE if exist "%ProgramFiles%\\Python310\\python.exe" set "PYTHON_TO_USE=%ProgramFiles%\\Python310\\python.exe"
                            if not defined PYTHON_TO_USE if exist "%ProgramFiles%\\Python311\\python.exe" set "PYTHON_TO_USE=%ProgramFiles%\\Python311\\python.exe"
                            if not defined PYTHON_TO_USE (
                                set "BOOTSTRAP_DIR=%CD%\\jenkins-miniconda3"
                                set "BOOTSTRAP_EXE=!BOOTSTRAP_DIR!\\python.exe"
                                set "INSTALLER=%CD%\\miniconda-installer.exe"
                                if not exist "!BOOTSTRAP_EXE!" (
                                    echo Bootstrapping Miniconda into !BOOTSTRAP_DIR!
                                    if exist "!INSTALLER!" del /f /q "!INSTALLER!"
                                    where curl.exe >nul 2>nul && curl.exe -L "https://repo.anaconda.com/miniconda/Miniconda3-py310_24.11.1-0-Windows-x86_64.exe" -o "!INSTALLER!"
                                    if not exist "!INSTALLER!" powershell -NoProfile -ExecutionPolicy Bypass -Command "(New-Object System.Net.WebClient).DownloadFile('https://repo.anaconda.com/miniconda/Miniconda3-py310_24.11.1-0-Windows-x86_64.exe', '!INSTALLER!')"
                                    if not exist "!INSTALLER!" bitsadmin /transfer miniconda /download /priority foreground "https://repo.anaconda.com/miniconda/Miniconda3-py310_24.11.1-0-Windows-x86_64.exe" "!INSTALLER!"
                                    if exist "!INSTALLER!" start /wait "" "!INSTALLER!" /InstallationType=JustMe /RegisterPython=0 /S /D=!BOOTSTRAP_DIR!
                                )
                                if exist "!BOOTSTRAP_EXE!" set "PYTHON_TO_USE=!BOOTSTRAP_EXE!"
                            )
                            if not defined PYTHON_TO_USE (
                                echo ERROR: Python was not found and Miniconda bootstrap did not succeed.
                                echo Set the PYTHON_CMD build parameter to py -3.10, python, or the full path to python.exe.
                                echo Example: C:\\Users\\YOURNAME\\AppData\\Local\\Programs\\Python\\Python310\\python.exe
                                exit /b 1
                            )
                            echo Using Python command: !PYTHON_TO_USE!
                            if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
                            call !PYTHON_TO_USE! -m venv "%VENV_DIR%"
                            call "%VENV_DIR%\\Scripts\\activate.bat"
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Validate Credentials') {
            when {
                expression { return !params.LOCAL_ONLY }
            }
            steps {
                echo '🔐 Validating GCP credentials...'
                withCredentials([file(credentialsId: 'gcp-vertex-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set -eu
                                . "$VENV_DIR/bin/activate"
                                python - <<'PY'
from google.auth import default
creds, project = default()
email = getattr(creds, 'service_account_email', 'unknown')
print(f'Authenticated as: {email}')
print(f'Project: {project}')
PY
                            '''
                        } else {
                            bat '''
                                @echo off
                                call "%VENV_DIR%\\Scripts\\activate.bat"
                                python -c "from google.auth import default; creds, project = default(); print(f'Authenticated as: {getattr(creds, ''service_account_email'', ''unknown'')}'); print(f'Project: {project}')"
                            '''
                        }
                    }
                }
            }
        }

        stage('Run Local Tests') {
            steps {
                echo '🧪 Running local tests...'
                script {
                    if (isUnix()) {
                        sh '''
                            set -eu
                            . "$VENV_DIR/bin/activate"
                            python -m pytest tests/ -v
                        '''
                    } else {
                        bat '''
                            @echo off
                                call "%VENV_DIR%\\Scripts\\activate.bat"
                                python -m pytest tests\\ -v
                        '''
                    }
                }
            }
        }

        stage('Run Local Training') {
            steps {
                echo '🏃 Running local training...'
                script {
                    if (isUnix()) {
                        sh '''
                            set -eu
                            . "$VENV_DIR/bin/activate"
                            MLFLOW_TRACKING_URI=./mlruns python src/train.py
                            test -f models/model.pkl
                        '''
                    } else {
                        bat '''
                            @echo off
                                call "%VENV_DIR%\\Scripts\\activate.bat"
                                set MLFLOW_TRACKING_URI=.\\mlruns
                                python src\\train.py
                                if not exist models\\model.pkl exit /b 1
                        '''
                    }
                }
            }
        }

        stage('Submit Training Job') {
            when {
                expression { return !params.LOCAL_ONLY && !params.VERTEX_PIPELINE_RUN?.trim() }
            }
            steps {
                echo "🤖 Submitting ${params.FRAMEWORK} training workflow..."
                withCredentials([file(credentialsId: 'gcp-vertex-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set -eu
                                . "$VENV_DIR/bin/activate"
                                python orchestrate.py --framework "$FRAMEWORK" --skip-monitor
                            '''
                        } else {
                            bat '''
                                @echo off
                                call "%VENV_DIR%\\Scripts\\activate.bat"
                                python orchestrate.py --framework "%FRAMEWORK%" --skip-monitor
                            '''
                        }
                    }
                }
            }
        }

        stage('Inspect Vertex Pipeline Run') {
            when {
                expression { return !params.LOCAL_ONLY && params.VERTEX_PIPELINE_RUN?.trim() }
            }
            steps {
                echo '🔎 Inspecting existing Vertex pipeline run...'
                withCredentials([file(credentialsId: 'gcp-vertex-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set -eu
                                . "$VENV_DIR/bin/activate"
                                python scripts/monitor_vertex_pipeline_run.py --run "$VERTEX_PIPELINE_RUN"
                            '''
                        } else {
                            bat '''
                                @echo off
                                call "%VENV_DIR%\\Scripts\\activate.bat"
                                python scripts\\monitor_vertex_pipeline_run.py --run "%VERTEX_PIPELINE_RUN%"
                            '''
                        }
                    }
                }
            }
        }

        stage('Monitor Recent Jobs') {
            when {
                expression { return !params.LOCAL_ONLY && params.MONITOR_JOBS }
            }
            steps {
                echo '📋 Listing recent Vertex AI jobs...'
                withCredentials([file(credentialsId: 'gcp-vertex-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set -eu
                                . "$VENV_DIR/bin/activate"
                                python scripts/monitor_training.py --list --limit 10
                            '''
                        } else {
                            bat '''
                                @echo off
                                call "%VENV_DIR%\\Scripts\\activate.bat"
                                python scripts\\monitor_training.py --list --limit 10
                            '''
                        }
                    }
                }
            }
        }

        stage('Optional Deploy') {
            when {
                expression { return !params.LOCAL_ONLY && params.DEPLOY_MODEL && params.FRAMEWORK != 'all' && params.MODEL_ARTIFACT_PATH?.trim() }
            }
            steps {
                echo '🚀 Registering the provided model artifact...'
                withCredentials([file(credentialsId: 'gcp-vertex-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set -eu
                                . "$VENV_DIR/bin/activate"
                                python scripts/deploy_model.py upload \
                                    --model-path "$MODEL_ARTIFACT_PATH" \
                                    --framework "$FRAMEWORK" \
                                    --version "$MODEL_VERSION"
                            '''
                        } else {
                            bat '''
                                @echo off
                                call "%VENV_DIR%\\Scripts\\activate.bat"
                                python scripts\\deploy_model.py upload --model-path "%MODEL_ARTIFACT_PATH%" --framework "%FRAMEWORK%" --version "%MODEL_VERSION%"
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Jenkins training pipeline completed successfully'
        }
        failure {
            echo 'Jenkins training pipeline failed'
        }
        always {
            echo 'Cleaning up workspace...'
            script {
                if (isUnix()) {
                    sh 'rm -rf "$VENV_DIR"'
                } else {
                    bat '''
                        @echo off
                        if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
                    '''
                }
            }
        }
    }
}
