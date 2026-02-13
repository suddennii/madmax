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
                    branch: 'dev', 
                    credentialsId: 'oauth2'
            }
        }
        
        stage('Inject env file') {
            steps {
                // 젠킨스에 등록된 Secret File ID: 'prod-env-file'
                withCredentials([file(credentialsId: 'prod-env-file', variable: 'ENV_FILE')]) {
                    sh '''
                        # 폴더가 없는 경우를 대비해 생성 및 권한 부여
                        mkdir -p ${TEST_DIR1}
                        mkdir -p ${TEST_DIR2}/performance_tests

                        # 현재 폴더 및 하위 폴더 권한을 777로 일시 변경 (복사 허용)
                        chmod -R 777 ${TEST_DIR2}/performance_tests

                        # Pytest용 .env 복사
                        cp $ENV_FILE ${TEST_DIR1}/.env
                        sed -i 's/\\r//g' ${TEST_DIR1}/.env
                        
                        # JMeter 폴더로도 .env 복사 
                        # JMeter용 .env 복사
                        cp \$ENV_FILE ${TEST_DIR2}/performance_tests/.env
                        sed -i 's/\\r//g' ${TEST_DIR2}/performance_tests/.env
                        
                        # 보안을 위해 권한 다시 제한
                        chmod 600 ${TEST_DIR1}/.env
                        chmod 600 ${TEST_DIR2}/performance_tests/.env
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

                    # 1. TOKEN 추출
                    ACCESS_TOKEN=\$(grep '^TOKEN=' .env | cut -d '=' -f2- | head -n 1 | tr -d '\\r' | tr -d '\\n')

                    # 2. 결과 폴더 초기화
                    rm -rf reports
                    mkdir -p reports/jmeter_dashboard

                    # 3. JMeter 실행 (최신 버전용 옵션)
                    # -n: Non-GUI 모드
                    # -t: 테스트 계획 파일(.jmx)
                    # -l: 결과 파일(.jtl) 저장
                    # -e -o: 실행 직후 HTML 대시보드 생성
                    jmeter -n -t 3team_load_test_v4.jmx \\
                        "-Jtoken=\$ACCESS_TOKEN" \\
                        -l reports/result.jtl \\
                        -e -o reports/jmeter_dashboard
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