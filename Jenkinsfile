pipeline {
    agent any
    
    environment {
        // VM 내의 JMeter 실행 경로
        JMETER_BIN = "jmeter" 
        TEST_DIR1 = "part1_api_automation"
        TEST_DIR2 = "part2_api_automation"
    }

    stages {
        stage('Prepare') {
            steps {
                // 권한 에러 방지를 위해 기존 리포트 폴더 삭제 후 재생성
                sh "rm -rf part1_api_automation/reports part2_api_automation/performance_tests/reports"
                sh "mkdir -p part1_api_automation/reports part2_api_automation/performance_tests/reports/jmeter_dashboard"
            }
        }

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
                        # 1. .env 파일 복사 (권한 에러를 피하기 위해 chmod -R 777 제거)
                        cp ${ENV_FILE} ${TEST_DIR1}/.env
                        cp ${ENV_FILE} ${TEST_DIR2}/performance_tests/.env
                        
                        # 2. 줄바꿈 기호 제거 (Windows/Linux 호환성)
                        sed -i 's/\\r//g' ${TEST_DIR1}/.env
                        sed -i 's/\\r//g' ${TEST_DIR2}/performance_tests/.env
                        
                        # 3. 보안 권한 설정
                        chmod 600 ${TEST_DIR1}/.env ${TEST_DIR2}/performance_tests/.env
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
            archiveArtifacts artifacts: "${TEST_DIR1}/reports/*.html", allowEmptyArchive: true, fingerprint: true
            archiveArtifacts artifacts: "${TEST_DIR2}/performance_tests/reports/**/*", allowEmptyArchive: true
            echo "✅ 모든 공정이 완료되었습니다."

            // HTML 리포트를 젠킨스 메뉴에 고정
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'part1_api_automation/reports', // 리포트가 저장된 폴더 경로
                reportFiles: 'pytest_report.html',                // 생성된 파일명
                reportName: 'Pytest API Report'            // 젠킨스 메뉴에 표시될 이름
            ])
            
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'part2_api_automation/performance_tests/reports/jmeter_dashboard',
                reportFiles: 'index.html',
                reportName: 'JMeter Performance Report'
            ])

            echo "✅ 모든 공정이 완료되었습니다. 젠킨스 왼쪽 메뉴에서 리포트를 확인하세요!"
        }
    }
} // pipeline 끝