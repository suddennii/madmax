#  LXP QA 자동화 & 부하 테스트 프로젝트
엘리스 LXP(Learning eXperience Platform)를 대상으로
**기능 테스트 자동화 + 부하 테스트(Spike Traffic)**를 수행하는 QA 프로젝트입니다.
본 프로젝트는 실제 서비스 품질 검증 프로세스를 경험하며,
API 분석 → 테스트 케이스 설계 → 자동화 → 부하 테스트까지
QA 실무 전 과정을 직접 수행하는 것을 목표로 합니다.


## 1. 프로젝트 소개
### 목적
- LXP 플랫폼의 일반 학습자(Learner) 관점에서 핵심 기능 검증
- API 기반 기능 테스트 자동화 구현
- 대규모 트래픽 상황에서의 성능 한계 및 병목 구간 분석
### 주요 구성
- Part 1: 기능 테스트 자동화 (pytest 기반)
- Part 2: 부하 테스트 (JMeter 기반)



## 2. 프로젝트 주요 단계
**1) 요구사항 분석 & API 명세 검토**
- 제공된 HTML API 스펙 분석
- 학습자(Learner) 권한에서 접근 가능한 API만 선별
- 관리자/교육자 API는 제외

**2) 테스트 범위 정의 (Scope 선정)**
LXP 플랫폼의 5개 핵심 메뉴 중심으로 테스트 범위 확정:
- 클래스 홈
- 학습 과목
- 수업 일정
- 게시판
- 대시보드

**3) 테스트 케이스 설계**
- Positive / Negative Test Case 작성
- 필수 파라미터, 권한, 응답 코드 기준 검증 포인트 정의
- YAML 기반 테스트 데이터 구성

**4) 기능 테스트 자동화 구현**
- pytest 기반 테스트 코드 작성
- API Client 모듈화
- 공통 로직(인증, 요청, 응답 검증) 구조화
- parametrize 기반 반복 테스트 적용

**5) 테스트 실행 & 리포트**
- pytest 실행
- 실패 케이스 분석
- API 응답 구조 및 데이터 유효성 검증

**6) 부하 테스트 설계 (Spike Traffic)**
- 시험 입장 → 응시 → 제출 → 재응시 사이클 정의
- Hidden API 직접 캡처(Network 탭 활용)
- JMeter Test Plan 구성

**7) 부하 테스트 실행**
- Thread 100 → 500 → 1,000 단계적 증가
- Ramp-up, Loop Count 설정
- 응답 시간 / 에러율 모니터링
- 병목 구간 및 임계 지점 분석

**8) 결과 분석 & 개선 제안**
- TPS, Latency, Error Rate 기반 성능 분석
- API 병목 지점 도출
- 개선 방향 제안

## 성공 기준
- Error Rate < 1%
- 평균 Latency 허용 범위 내 유지
- 1,000명 사이클 정상 반복
- TPS·Latency 변화 분석 및 병목 지점 도출

## 3. 기술 스펙
### Backend API 테스트 환경
- Python 3.13
- pytest
- requests
- PyYAML
- python-dotenv
### 부하 테스트 환경
- Apache JMeter 5.x
- HTTP Request Sampler
- Loop Controller
- Summary Report / Aggregate Report
### 개발 환경
- GitLab
- VS Code
- Git Flow 일부 적용
- Jenkins
- JMeter


## 4. 설치 방법
1) 저장소 클론
```
git clone https://kdt-gitlab.elice.io/qa_track/class_03/qa3_final_project/team_03/madmax.git
```
2) 가상환경 생성
```
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```
3) 패키지 설치
```
pip install -r requirements.txt
```
4) 환경 변수 설정
```
.env.example을 참고하여 .env 파일 생성:
BASE_URL=https://api.example.com
ACCESS_TOKEN=your_token_here
```

## 팀원 소개
박지우 (팀장), 조대건, 신윤아, 심다영, 김건후

## 프로젝트 기간
2026년 2월 2일(월) ~ 2026년 2월 23일(월)
