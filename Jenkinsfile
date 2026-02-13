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
                git url: 'https://kdt-gitlab.elice.io/qa_track/class_03/qa3_final_project/team_03/madmax.git', 
                    branch: 'TC2', 
                    credentialsId: 'oauth2'
            }
        }
        
        stage('Inject env file') {
            steps {
                // 젠킨스에 등록된 Secret File ID: 'prod-env-file'
                withCredentials([file(credentialsId: 'prod-env-file', variable: 'ENV_FILE')]) {
                    sh '''
                        # Pytest용 .env 복사
                        cp $ENV_FILE ${TEST_DIR1}/.env
                        sed -i 's/\\r//g' ${TEST_DIR1}/.env
                        chmod 600 ${TEST_DIR1}/.env
                        if command -v dos2unix >/dev/null 2>&1; then
                            dos2unix ${TEST_DIR1}/.env
                        fi
                        # JMeter 폴더로도 .env 복사 (토큰 추출 용도)
                        cp \$ENV_FILE ${TEST_DIR2}/performance_tests/.env
                    '''
                }
            }
        }

        stage('Connection Check') {
            steps {
                // 파일이 잘 가져와졌는지 폴더 목록만 출력
                sh "ls -R"
                echo "✅ 깃랩 연결 및 파일 체크아웃 성공!"
            }
        }

        
        stage('Environment Setup (Pytest)') {
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
                    set +x
                    export \$(grep -v '^#' .env | xargs)
                    pytest -s tests/ --html=reports/pytest_report.html --self-contained-html || true
                """
            }
        }
        stage('Run JMeter (Performance Test)') {
            steps {
                sh """
                    cd ${TEST_DIR2}/performance_tests

                    # 1. .env 파일에서 토큰 값 추출 (변수명이 TOKEN이라고 가정)
                    # 실제 .env 내 변수명에 맞게 'TOKEN' 부분을 수정하세요.
                    ACCESS_TOKEN=\$(grep 'TOKEN' .env | cut -d '=' -f2 | tr -d '\\r')

                    # 2. 리포트 폴더 초기화
                    rm -rf reports
                    mkdir -p reports/jmeter_dashboard

                    # 3. JMeter 실행
                    ${JMETER_BIN} -n -t 3team_load_test_v4.jmx \
                    -Jtoken=\$ACCESS_TOKEN \
                    -l reports/result.jtl
                    
                    # 4. 실행 후 별도로 대시보드 생성 시도
                    ${JMETER_BIN} -g reports/result.jtl -o reports/jmeter_dashboard || echo "Dashboard generation failed"
                    """
            }
        }
    } // stages 끝

    post {
        always {
            // Part 1 폴더 안에 생성된 리포트를 젠킨스 대시보드에 저장
            archiveArtifacts artifacts: "${TEST_DIR1}/reports/*.html", allowEmptyArchive: true
            archiveArtifacts artifacts: "${TEST_DIR2}/performance_tests/reports/**/*", allowEmptyArchive: true
            echo "✅ 모든 공정이 완료되었습니다."
        }
    }
} // pipeline 끝