pipeline {
    agent any

    tools {
        allure 'allure'
    }
    
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
                    branch: 'main', 
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
                    pip install allure-pytest
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
                    pytest -s tests/ --alluredir=allure-results || true
                """
            }
        }

        stage('Run JMeter (Performance Test)') {
            steps {
                script{
                    // 테스트할 사용자 수 
                    def threadCnt = [1, 3]

                    for (threads in threadCnt){
                        echo "##### 현재 테스트 사용자 수 : ${threads}"

                        sh """
                            cd ${TEST_DIR2}/performance_tests

                            # 1. TOKEN 추출
                            ACCESS_TOKEN=\$(grep '^TOKEN=' .env | cut -d '=' -f2- | head -n 1 | tr -d '\\r' | tr -d '\\n')

                            # 2. 결과 폴더 초기화
                            REPORT_PATH="reports/threads_${threads}"
                            mkdir -p \$REPORT_PATH

                            # [추가] dstat 백그라운드 실행: 1초 간격으로 자원 수집 후 CSV 저장 (모니터링)
                            nohup dstat -tcmnd --output \$REPORT_PATH/system_resource_usage_raw.csv 1 > /dev/null 2>&1 &
                            MON_PID=\$!

                            # 3. JMeter 실행 (최신 버전용 옵션)
                            # -n: Non-GUI 모드
                            # -t: 테스트 계획 파일(.jmx)
                            # -l: 결과 파일(.jtl) 저장
                            # -e -o: 실행 직후 HTML 대시보드 생성
                            jmeter -n -t 3team_load_test_v4.jmx \\
                                "-Jtoken=\$ACCESS_TOKEN" \\
                                "-Jthreads=${threads}" \\
                                "-Jjmeter.save.saveservice.response_data=true" \\
                                "-Jjmeter.save.saveservice.samplerData=true" \\
                                "-Jjmeter.save.saveservice.responseCode=true" \\
                                -l \$REPORT_PATH/result.jtl \\
                                -j \$REPORT_PATH/jmeter.log \\
                                -e -o \$REPORT_PATH/dashboard

                            # 4. 테스트 종료 후 모니터링 프로세스 종료
                            sleep 2
                            kill \$MON_PID || true

                            # 5. [중요] dstat CSV 상단의 메타데이터(6줄)를 제거해야 Plot 플러그인이 읽을 수 있음.
                            tail -n +7 \$REPORT_PATH/system_resource_usage_raw.csv > \$REPORT_PATH/system_resource_usage.csv
                        """

                        echo "서버 안정화를 위해 5초간 대기"
                        sleep 5
                    }
                }
            }
        }
    } // stages 끝

    post {
        always {
            // Part 1 폴더 안에 생성된 리포트를 젠킨스 대시보드에 저장
            allure includeProperties: false, results: [[path: "${TEST_DIR1}/allure-results"]]
            archiveArtifacts artifacts: "${TEST_DIR2}/performance_tests/reports/**/*", allowEmptyArchive: true
            
            // 2. CSV 데이터 기반 젠킨스 대시보드 그래프 생성 (Plot Plugin)
            plot csvFileName: 'plot-resource.csv', 
                 group: 'Resource Usage', 
                 title: 'System Performance (100 Threads)', 
                 style: 'line', 
                 csvSeries: [[
                     file: "${TEST_DIR2}/performance_tests/reports/threads_1/system_resource_usage.csv", 
                     displayTableFlag: true
                 ]]
            
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'part2_api_automation/performance_tests/reports/threads_1/dashboard',
                reportFiles: 'index.html',
                reportName: 'JMeter Performance Report (Final)'
            ])

            echo "✅ 모든 공정이 완료되었습니다. 젠킨스 왼쪽 메뉴에서 리포트를 확인하세요!"
        }
    }
} // pipeline 끝