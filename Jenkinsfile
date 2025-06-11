pipeline {
    agent any
    
    environment {
        VENV_PATH = 'venv'
        PYTHON_PATH = "${VENV_PATH}/bin/python"
        PIP_PATH = "${VENV_PATH}/bin/pip"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv ${VENV_PATH}
                    ${PIP_PATH} install --upgrade pip
                    ${PIP_PATH} install -r odonto_smile/backend/requirements.txt
                '''
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    ${PYTHON_PATH} -m pytest odonto_smile/backend/tests/
                '''
            }
        }
        
        stage('Build') {
            steps {
                sh '''
                    echo "Building the application..."
                    # Aquí puedes agregar comandos específicos para construir tu aplicación
                '''
            }
        }
        
        stage('Docker Build') {
            steps {
                sh '''
                    docker build -f odonto_smile/dockerfile -t odonto_smile_app .
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                sh '''
                    echo "Deploying the application..."
                    # Aquí puedes agregar comandos específicos para desplegar tu aplicación
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
    
}
