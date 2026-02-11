pipeline {
    agent any
     
    environment {
        JMETER_BIN = "jmeter"
        TEST_DIR1 = "part1_api_automation"
        TEST_DIR2 = "part2_api_automation"

        ACCOUNT_ID = credentials('account-id')
        ACCOUNT_ID2 = credentials('account-id2')
        USER_TOKEN = credentials('user-token-1')
    }

    stages {

        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/suddennii/madmax.git',
                    branch: 'TC1',
                    credentialsId: 'github-token'
            }
        }

        stage('Connection Check') {
            steps {
                sh "ls -R"
                echo "✅ 깃랩 연결 및 파일 체크아웃 성공!"
            }
        }

        stage('Environment Setup') {
            steps {
                sh """
                    cd ${TEST_DIR1}
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Load ENV File') {
            steps {
                withCredentials([file(credentialsId: 'madmax-env-file', variable: 'ENV_FILE')]) {
                    sh """
                        cp "$ENV_FILE" "$WORKSPACE/${TEST_DIR1}/.env"
                    """
                }
            }
        }

        stage('Run Pytest (API Automation)') {
            steps {
                sh """
                    cd ${TEST_DIR1}
                    . venv/bin/activate
                    pytest tests/test_dash.py --html=reports/pytest_report.html --self-contained-html
                """
            }
        }

        /*
        stage('Run JMeter (Performance Test)') {
            steps {
                sh """
                    cd ${TEST_DIR2}/performance_tests
                    rm -rf reports
                    mkdir -p reports/jmeter_dashboard
                    ${JMETER_BIN} -n -t load_test2.jmx -l reports/result.jtl -e -o reports/jmeter_dashboard || true
                """
            }
        }
        */
    }

    post {
        always {
            archiveArtifacts artifacts: "${TEST_DIR1}/reports/*.html", allowEmptyArchive: true
            echo "✅ 모든 공정이 완료되었습니다."
        }
    }
}
