stage('Build Docker Image') {
    steps {
        bat '"C:\\Users\\ATHARVA PATEL\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" --version'
        bat '"C:\\Users\\ATHARVA PATEL\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" info'
        bat '"C:\\Users\\ATHARVA PATEL\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t resumeiq:%BUILD_NUMBER% .'
    }
}