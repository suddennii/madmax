pipeline {
    agent any
    
    environment {
        // VM 내의 JMeter 실행 경로
        JMETER_BIN = "jmeter" 
        TEST_DIR1 = "part1_api_automation"
        TEST_DIR2 = "part2_api_automation"
    }

    stages {
        stage('Clone Repository') {
            steps {
                // GitLab 주소 및 인증정보 설정
                git url: 'https://github.com/suddennii/madmax.git', 
                    branch: 'TC1', 
                    credentialsId: 'github-madmax'
            }
        }

        stage('Connection Check') {
            steps {
                // 파일이 잘 가져와졌는지 폴더 목록만 출력
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

        stage('Run Pytest (API Automation)') {
            steps {
                sh """
                    cd ${TEST_DIR1}
                    . venv/bin/activate
                    pytest tests/test_sub.py --html=reports/pytest_report.html --self-contained-html
                """
            }
        }
        /* 나중에 코드가 준비되면 아래 stage들의 주석을 해제하세요. 
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
    } // stages 끝

    post {
        always {
            // Part 1 폴더 안에 생성된 리포트를 젠킨스 대시보드에 저장
            archiveArtifacts artifacts: "${TEST_DIR1}/reports/*.html", allowEmptyArchive: true
            echo "✅ 모든 공정이 완료되었습니다."
        }
    }
} // pipeline 끝
