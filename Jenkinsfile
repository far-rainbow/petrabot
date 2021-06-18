pipeline {
  agent any
  stages {
    stage('BUILD') {
      steps {
        sh 'docker-compose build --pull'
      }
    }

    stage('PUSH') {
      steps {
        withCredentials([
                    usernamePassword(
                        credentialsId: '1382a34c-ae55-45ad-86a2-f2e8a8eda183',
                        usernameVariable: 'USER',
                        passwordVariable: 'PASSWORD'
                    )
         ]) {
              sh "docker login -u=$USER -p='$PASSWORD'"
         }
         sh "docker push kamenka/petrabot"
      }
    }
  }
}
