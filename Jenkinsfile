def candidateGcpCredentialPaths(scriptContext) {
    def candidates = []
    if (scriptContext.params.GCP_KEY_FILE?.trim()) {
        candidates << scriptContext.params.GCP_KEY_FILE.trim()
    }
    if (scriptContext.env.GOOGLE_APPLICATION_CREDENTIALS?.trim()) {
        candidates << scriptContext.env.GOOGLE_APPLICATION_CREDENTIALS.trim()
    }
    candidates << "${scriptContext.pwd()}/gcp-key.json"

    if (scriptContext.isUnix()) {
        def home = scriptContext.env.HOME ?: ''
        if (home) {
            candidates << "${home}/.config/gcloud/application_default_credentials.json"
        }
    } else {
        def appData = scriptContext.env.APPDATA ?: ''
        def userProfile = scriptContext.env.USERPROFILE ?: ''
        def systemRoot = scriptContext.env.SystemRoot ?: 'C:\\Windows'
        if (appData) {
            candidates << "${appData}\\gcloud\\application_default_credentials.json"
        }
        if (userProfile) {
            candidates << "${userProfile}\\AppData\\Roaming\\gcloud\\application_default_credentials.json"
        }
        candidates << "${systemRoot}\\System32\\config\\systemprofile\\AppData\\Roaming\\gcloud\\application_default_credentials.json"
    }

    return candidates.findAll { it?.trim() }.unique()
}

def resolveGcpCredentialFile(scriptContext) {
    for (String candidate : candidateGcpCredentialPaths(scriptContext)) {
        if (scriptContext.fileExists(candidate)) {
            return candidate
        }
    }
    return null
}

def runGoogleAuthProbe(scriptContext) {
    if (scriptContext.isUnix()) {
        return scriptContext.sh(
            returnStatus: true,
            script: '''
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
        )
    }

    return scriptContext.bat(
        returnStatus: true,
        script: '''
            @echo off
            call "%VENV_DIR%\\Scripts\\activate.bat"
            python -c "from google.auth import default; creds, project = default(); email = getattr(creds, 'service_account_email', 'unknown'); print('Authenticated as: {}'.format(email)); print('Project: {}'.format(project))"
        '''
    )
}

def withDetectedGcpAuth(scriptContext, Closure body) {
    def credentialFile = resolveGcpCredentialFile(scriptContext)
    if (credentialFile) {
        scriptContext.echo("Using GCP credential file at ${credentialFile}")
        scriptContext.withEnv(["GOOGLE_APPLICATION_CREDENTIALS=${credentialFile}"]) {
            body()
        }
        return
    }
    if (runGoogleAuthProbe(scriptContext) == 0) {
        scriptContext.echo('Using ambient Google Application Default Credentials from the Jenkins agent.')
        body()
        return
    }
    if (scriptContext.params.GCP_CREDENTIALS_ID?.trim()) {
        try {
            scriptContext.withCredentials([file(credentialsId: scriptContext.params.GCP_CREDENTIALS_ID, variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                body()
            }
            return
        } catch (Exception ex) {
            scriptContext.error("No usable GCP credentials were found. Checked GCP_KEY_FILE, GOOGLE_APPLICATION_CREDENTIALS, workspace gcp-key.json, common gcloud ADC locations, and Jenkins credential ID '${scriptContext.params.GCP_CREDENTIALS_ID}'. Either set GCP_KEY_FILE to a real JSON path on the Jenkins agent, configure that Jenkins file credential, or configure ADC for the Jenkins service account. Original error: ${ex.message}")
        }
    }
    scriptContext.error('No usable GCP credentials were found. Set GCP_KEY_FILE to a real JSON path on the Jenkins agent, configure GOOGLE_APPLICATION_CREDENTIALS, configure gcloud ADC for the Jenkins service account, or provide a Jenkins file credential ID.')
}

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    parameters {
        choice(
            name: 'FRAMEWORK',
            choices: ['scikit-learn', 'tensorflow', 'pytorch', 'all'],
            description: 'Framework to submit to Vertex AI. Use scikit-learn for the end-to-end default path or all to submit every training workflow.'
        )
        booleanParam(
            name: 'MONITOR_JOBS',
            defaultValue: true,
            description: 'List recent Vertex AI jobs after submission'
        )
        booleanParam(
            name: 'LOCAL_ONLY',
            defaultValue: false,
            description: 'When true, stop after local setup, tests, and training. Leave false for the full Jenkins to Vertex AI workflow.'
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
        string(
            name: 'GCP_CREDENTIALS_ID',
            defaultValue: 'gcp-vertex-sa-key',
            description: 'Optional Jenkins file credential ID for the GCP service account JSON used by the Vertex pipeline stages'
        )
        string(
            name: 'GCP_KEY_FILE',
            defaultValue: '',
            description: 'Optional local path on the Jenkins agent to a GCP service account JSON file. If set, this is used instead of Jenkins credentials.'
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

        stage('Pipeline Parameters') {
            steps {
                echo "FRAMEWORK=${params.FRAMEWORK}"
                echo "LOCAL_ONLY=${params.LOCAL_ONLY}"
                echo "MONITOR_JOBS=${params.MONITOR_JOBS}"
                echo "DEPLOY_MODEL=${params.DEPLOY_MODEL}"
                echo "VERTEX_PIPELINE_RUN=${params.VERTEX_PIPELINE_RUN ?: '(empty)'}"
                echo "MODEL_ARTIFACT_PATH=${params.MODEL_ARTIFACT_PATH ?: '(empty)'}"
                echo "GCP_CREDENTIALS_ID=${params.GCP_CREDENTIALS_ID ?: '(empty)'}"
                echo "GCP_KEY_FILE=${params.GCP_KEY_FILE ?: '(empty)'}"
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
            steps {
                script {
                    if (params.LOCAL_ONLY) {
                        echo 'LOCAL_ONLY=true, so cloud credential validation is intentionally bypassed.'
                    } else {
                        echo '🔐 Validating GCP credentials...'
                        withDetectedGcpAuth(this) {
                            if (isUnix()) {
                                sh '''
                                    set -eu
                                    if [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]; then
                                        test -f "$GOOGLE_APPLICATION_CREDENTIALS"
                                    fi
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
                                    if defined GOOGLE_APPLICATION_CREDENTIALS if not exist "%GOOGLE_APPLICATION_CREDENTIALS%" exit /b 1
                                    call "%VENV_DIR%\Scripts\activate.bat"
                                    python -c "from google.auth import default; creds, project = default(); email = getattr(creds, 'service_account_email', 'unknown'); print('Authenticated as: {}'.format(email)); print('Project: {}'.format(project))"
                                '''
                            }
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
            steps {
                script {
                    if (params.LOCAL_ONLY) {
                        echo 'LOCAL_ONLY=true, so no Vertex training job will be submitted.'
                    } else if (params.VERTEX_PIPELINE_RUN?.trim()) {
                        echo 'Existing VERTEX_PIPELINE_RUN provided, so new training submission is skipped by design.'
                    } else {
                        echo "🤖 Submitting ${params.FRAMEWORK} training workflow..."
                        withDetectedGcpAuth(this) {
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
        }

        stage('Inspect Vertex Pipeline Run') {
            steps {
                script {
                    if (params.LOCAL_ONLY) {
                        echo 'LOCAL_ONLY=true, so existing Vertex pipeline inspection is bypassed.'
                    } else if (params.VERTEX_PIPELINE_RUN?.trim()) {
                        echo '🔎 Inspecting existing Vertex pipeline run...'
                        withDetectedGcpAuth(this) {
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
                    } else {
                        echo 'No VERTEX_PIPELINE_RUN value was provided, so this stage has nothing to inspect.'
                    }
                }
            }
        }

        stage('Monitor Recent Jobs') {
            steps {
                script {
                    if (params.LOCAL_ONLY) {
                        echo 'LOCAL_ONLY=true, so cloud job monitoring is bypassed.'
                    } else if (!params.MONITOR_JOBS) {
                        echo 'MONITOR_JOBS=false, so recent Vertex AI jobs will not be listed.'
                    } else {
                        echo '📋 Listing recent Vertex AI jobs...'
                        withDetectedGcpAuth(this) {
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
        }

        stage('Optional Deploy') {
            steps {
                script {
                    if (params.LOCAL_ONLY) {
                        echo 'LOCAL_ONLY=true, so deployment is bypassed.'
                    } else if (!params.DEPLOY_MODEL) {
                        echo 'DEPLOY_MODEL=false, so model registry upload is intentionally skipped.'
                    } else if (params.FRAMEWORK == 'all') {
                        echo 'DEPLOY_MODEL=true but FRAMEWORK=all. Choose a single framework to deploy a specific model artifact.'
                    } else if (!params.MODEL_ARTIFACT_PATH?.trim()) {
                        echo 'DEPLOY_MODEL=true but MODEL_ARTIFACT_PATH is empty. Provide a gs:// model artifact path to enable deployment.'
                    } else {
                        echo '🚀 Registering the provided model artifact...'
                        withDetectedGcpAuth(this) {
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
