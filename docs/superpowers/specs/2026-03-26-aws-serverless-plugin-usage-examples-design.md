# AWS Serverless Agent Plugin — 활용 예시 블로그 설계 스펙

**작성일:** 2026-03-26
**목적:** GitHub 포스팅용 블로그 — aws-serverless 플러그인의 활용 예시 데모 시나리오
**독자:** AWS 경험자, AI 에이전트 기반 개발은 처음인 개발자
**접근 방식:** 점진적 복잡도 스토리형 (접근 C) + Before 한 줄 대비 요약

---

## 1. 전체 구조

### 관통 프로젝트: "FoodOrder" — 음식 주문 처리 시스템

빈 디렉토리에서 시작해 프로덕션 레디 서버리스 앱까지 도달하는 4단계 여정.

```
시나리오 1 ─ 주문 API 생성 (aws-lambda 스킬)
     ↓ 주문은 받을 수 있지만, 배포가 수동 →
시나리오 2 ─ SAM으로 배포 자동화 (aws-serverless-deployment 스킬 + Hook)
     ↓ 배포는 자동인데, 주문 후 처리가 없음 →
시나리오 3 ─ 주문 처리 워크플로우 (aws-lambda-durable-functions 스킬)
     ↓ 워크플로우는 있는데, 운영 관점이 빠짐 →
시나리오 4 ─ 프로덕션 강화 (MCP 서버 + Hook + 스킬 통합)
```

### 문서 구성

```markdown
# 제목 (TBD — 블로그 작성 시 확정)
## 소개 — 왜 AI 에이전트 + 서버리스인가
## 사전 준비 — 플러그인 설치, AWS 자격 증명
## 시나리오 1~4 (각각 상세)
## 마무리 — 4개 시나리오에서 플러그인이 자동으로 적용한 것들 정리
```

### 각 시나리오 내부 구조

```markdown
### 시나리오 N: 제목
> ❌ Before: 이걸 수동으로 하면 — (한 줄 요약)

💬 **프롬프트**
(사용자가 실제로 입력하는 자연어)

🔧 **플러그인 실행 흐름**
(어떤 스킬이 트리거되고, 내부적으로 무엇을 하는지)

📦 **결과물**
(생성된 코드, 템플릿, 설정 등)

💡 **플러그인이 자동으로 적용한 Best Practice**
(독자가 "오, 이것까지?" 할 포인트)
```

### 플러그인 설치 방법

```bash
/plugin install aws-serverless@claude-plugins-official
```

### 플러그인 구성 요소

| 구성 요소 | 이름 | 역할 |
|----------|------|------|
| 스킬 | aws-lambda | Lambda 함수 설계, 빌드, 배포, 테스트, 디버그 |
| 스킬 | aws-serverless-deployment | SAM/CDK 배포 워크플로우 |
| 스킬 | aws-lambda-durable-functions | 상태 유지 워크플로우, Saga, Checkpoint |
| MCP 서버 | aws-serverless-mcp | 서버리스 개발 가이드, 스캐폴딩, IaC 생성, 배포 |
| Hook | SAM template validation | template.yaml 수정 시 `sam validate` 자동 실행 |

---

## 2. 시나리오 1: 주문 API 생성

### 메타데이터

| 항목 | 값 |
|------|---|
| 스킬 | `aws-lambda` |
| 트리거 키워드 | Lambda function, serverless application, API Gateway, event-driven architecture |
| 난이도 | 입문 |
| 핵심 메시지 | 프롬프트 한 줄로 Lambda + API Gateway + DynamoDB + IAM 생성 |

### Before 한 줄

> ❌ 수동으로 하면 — Lambda 콘솔에서 함수 생성 → API Gateway 구성 → DynamoDB 테이블 생성 → IAM 역할/정책 작성 → 통합 연결 → 테스트까지 최소 30분+, 10개 이상의 화면 전환

### 프롬프트

```
Python으로 음식 주문 REST API를 만들어줘.
- POST /orders: 주문 생성 (메뉴, 수량, 고객정보)
- GET /orders/{id}: 주문 조회
- DynamoDB에 저장
```

### 실행 흐름

1. `aws-lambda` 스킬 트리거 → 이벤트 소스로 API Gateway HTTP API 선택
2. Lambda 핸들러 코드 생성 (POST/GET 라우팅)
3. DynamoDB 테이블 스키마 설계 (PK: orderId)
4. API Gateway → Lambda 통합 이벤트 구조 자동 매핑
5. IAM 최소 권한 정책 자동 생성

### 결과물

- `app.py` — Lambda 핸들러 (POST/GET 분기, DynamoDB CRUD) — 블로그에 핵심 코드 스니펫 포함
- `requirements.txt` — boto3 등 의존성
- IAM 정책 스니펫 (DynamoDB PutItem/GetItem만 허용)

> 참고: 모든 결과물은 블로그용 예시 코드 스니펫으로 작성. 실행 가능한 전체 코드가 아닌, 핵심 패턴을 보여주는 발췌본.

### 자동 적용 Best Practice

- **Powertools for AWS Lambda** 활용 (로깅, 트레이싱, 이벤트 파싱)
- **API Gateway 이벤트 스키마**를 정확히 반영한 핸들러 구조
- **최소 권한 IAM** — DynamoDB 테이블 ARN 한정, `*` 미사용
- **입력값 검증 및 에러 핸들링** 패턴

---

## 3. 시나리오 2: SAM으로 배포 자동화

### 메타데이터

| 항목 | 값 |
|------|---|
| 스킬 | `aws-serverless-deployment` |
| Hook | SAM template validation |
| 트리거 키워드 | SAM template, SAM deploy, serverless CI/CD pipeline |
| 난이도 | 중급 |
| 핵심 메시지 | 코드를 IaC 프로젝트로 변환, 로컬 테스트, 배포까지 원스톱 |

### Before 한 줄

> ❌ 수동으로 하면 — SAM 프로젝트 구조 생성 → template.yaml 리소스 정의(Lambda, API GW, DynamoDB, IAM) → sam build → sam local invoke로 테스트 → sam deploy 설정 → samconfig.toml 작성까지 AWS 문서를 오가며 1시간+

### 프롬프트

```
시나리오 1에서 만든 주문 API를 SAM 프로젝트로 구성하고 배포해줘.
로컬 테스트도 할 수 있게 해줘.
```

### 실행 흐름

1. `aws-serverless-deployment` 스킬 트리거
2. 시나리오 1의 코드를 SAM 프로젝트 구조로 재구성
3. `template.yaml` 생성 (Lambda, HttpApi, DynamoDB, IAM Role)
4. **Hook 동작:** template.yaml 작성 완료 시 `sam validate` 자동 실행 → 오류 있으면 즉시 수정
5. `sam build` → `sam local invoke`로 로컬 테스트 안내
6. `sam deploy --guided` 배포 가이드

### 결과물

```
food-order-api/
├── template.yaml          ← SAM 템플릿 (전체 인프라 정의)
├── samconfig.toml         ← 배포 설정
├── src/
│   └── order_handler/
│       ├── app.py         ← 시나리오 1 핸들러 (SAM 구조에 맞게 재배치)
│       └── requirements.txt
├── events/
│   ├── create_order.json  ← 로컬 테스트용 이벤트
│   └── get_order.json
└── tests/
    └── unit/
        └── test_handler.py
```

- `template.yaml` — Lambda, HttpApi, DynamoDB 테이블, IAM Role 전체 정의
- `events/` — `sam local invoke` 테스트용 샘플 이벤트 (API Gateway 페이로드 형식)
- `tests/` — 유닛 테스트 스캐폴딩

### 자동 적용 Best Practice

- **Globals 섹션** — Lambda 공통 설정 (Runtime, Timeout, MemorySize, Tracing) 중앙 관리
- **테스트 이벤트 자동 생성** — `sam local invoke`용, API Gateway 페이로드 형식 정확히 반영
- **SAM Hook** — template.yaml 문법 오류를 배포 전에 차단
- **DeletionPolicy: Retain** — DynamoDB 테이블에 적용, 실수로 스택 삭제 시 데이터 보호

---

## 4. 시나리오 3: 주문 처리 워크플로우

### 메타데이터

| 항목 | 값 |
|------|---|
| 스킬 | `aws-lambda-durable-functions` |
| 트리거 키워드 | lambda durable functions, workflow orchestration, saga pattern, retry/checkpoint patterns |
| 난이도 | 고급 |
| 핵심 메시지 | Saga 패턴, Checkpoint, 멱등성을 자동 적용한 분산 워크플로우 |

### Before 한 줄

> ❌ 수동으로 하면 — Step Functions ASL JSON 수동 작성 → 각 단계별 Lambda 함수 개별 생성 → 에러/재시도/보상 로직 직접 구현 → 상태 전이 테스트까지 ASL 문법과 씨름하며 반나절+

### 프롬프트

```
주문이 생성되면 자동으로 실행되는 워크플로우를 만들어줘.
1. 결제 처리
2. 재고 확인 및 차감
3. 배송 접수
4. 고객 알림 (이메일)
결제 실패 시 주문 취소, 배송 접수 실패 시 재고 원복해줘.
```

### 실행 흐름

1. `aws-lambda-durable-functions` 스킬 트리거
2. 4단계 순차 워크플로우를 Durable Functions 패턴으로 설계
3. **Saga 패턴** 자동 적용 — 각 단계에 보상(compensation) 로직 매핑
   - 결제 실패 → 주문 상태 `CANCELLED`로 변경
   - 재고 차감 후 배송 실패 → 재고 원복 (보상 트랜잭션)
4. 각 step에 checkpoint 자동 삽입 — 중간 실패 시 재시작 지점 보장
5. DynamoDB Streams로 주문 생성 이벤트 → 워크플로우 자동 트리거 연결

### 결과물

- `src/workflow/order_processor.py` — Durable Functions 오케스트레이터 (4단계 + 보상 로직)
- `src/workflow/steps/` — 각 단계별 step 함수
  - `payment.py` — 결제 처리 + 결제 취소(보상)
  - `inventory.py` — 재고 차감 + 재고 원복(보상)
  - `shipping.py` — 배송 접수
  - `notification.py` — 고객 알림
- `template.yaml` 업데이트 — DynamoDB Streams 이벤트 소스, 워크플로우 Lambda 추가

### 자동 적용 Best Practice

- **Saga 패턴** — 분산 트랜잭션의 정석. 각 단계 실패 시 이전 단계를 역순으로 보상
- **Checkpoint/Replay 모델** — 워크플로우 중간에 Lambda가 재시작되어도 마지막 checkpoint부터 재개
- **멱등성(Idempotency)** — 각 step에 idempotency key 적용으로 중복 실행 방지
- **에러 분류** — 재시도 가능한 에러(네트워크 타임아웃)와 불가능한 에러(잔액 부족)를 구분하여 재시도 전략 차등 적용

---

## 5. 시나리오 4: 프로덕션 강화

### 메타데이터

| 항목 | 값 |
|------|---|
| 활용 도구 | MCP 서버(`aws-serverless-mcp`) + Hook(`SAM template validation`) + 스킬 통합 |
| 트리거 | ESM 최적화, 메트릭 조회, 배포 검증 |
| 난이도 | 고급 (운영) |
| 핵심 메시지 | ESM 최적화, 모니터링, DLQ — 운영 노하우를 플러그인이 자동 반영 |

### Before 한 줄

> ❌ 수동으로 하면 — CloudWatch 메트릭 설정, DynamoDB Streams ESM 튜닝(batch size, parallelization factor, retry), 에러 알림 구성, 성능 테스트까지 운영 경험 없이는 놓치는 항목 투성이

### 프롬프트

```
이 주문 처리 시스템을 프로덕션에 올리기 전에 점검해줘.
- DynamoDB Streams → Lambda 연결 최적화
- 주요 메트릭 모니터링 설정
- 에러 발생 시 알림
- 일일 주문 1만 건 예상
```

### 실행 흐름

1. `aws-serverless-mcp` MCP 서버를 통해 현재 template.yaml 분석
2. `esm_optimize` 도구 호출 — DynamoDB Streams ESM 설정 최적화
   - batch size, max batching window, parallelization factor 계산
   - bisect on error, max retry attempts 설정
   - failure destination (SQS DLQ) 추가
3. `get_metrics` 도구 호출 — Lambda/DynamoDB 핵심 메트릭 조회 가이드
4. `get_lambda_guidance` 도구 호출 — 동시성, 메모리, 타임아웃 권장값
5. template.yaml 수정 → **Hook이 자동으로 `sam validate` 실행** → 오류 없음 확인
6. `sam deploy` 가이드

### 결과물

- `template.yaml` 업데이트 내용:
  - ESM 최적화 설정 (BatchSize, MaximumBatchingWindowInSeconds, ParallelizationFactor 등)
  - DLQ(SQS) 리소스 추가 — 처리 실패 이벤트 보존
  - CloudWatch Alarm — Lambda 에러율, DynamoDB 스로틀링, DLQ 메시지 수
  - SNS Topic + 이메일 구독 — 알람 발생 시 알림
  - Lambda Reserved/Provisioned Concurrency 설정

### 자동 적용 Best Practice

- **ESM 튜닝** — 일일 1만 건 트래픽 기반으로 batch size와 parallelization factor를 계산. 과도한 동시성 방지
- **DLQ 패턴** — 처리 실패 이벤트를 버리지 않고 SQS로 보존. 후속 분석 및 재처리 가능
- **Bisect on Error** — 배치 내 하나의 레코드 실패 시 전체 배치 재시도 대신 이진 분할로 실패 레코드만 격리
- **운영 가시성** — Lambda Duration/Errors/Throttles, DynamoDB ConsumedRCU, DLQ ApproximateNumberOfMessages 핵심 메트릭을 알람으로 커버
- **Hook 안전망** — template.yaml 수정할 때마다 자동 검증이 돌아 잘못된 설정이 배포되는 것을 차단

---

## 6. 마무리 섹션 설계

블로그 말미에 4개 시나리오에서 플러그인이 자동으로 적용한 Best Practice를 한 눈에 정리.

### 시나리오별 요약 테이블

| 시나리오 | 스킬/도구 | Before (수동) | After (플러그인) |
|---------|----------|-------------|----------------|
| 1. 주문 API 생성 | aws-lambda | 30분+, 10개 화면 전환 | 프롬프트 1개 |
| 2. SAM 배포 자동화 | aws-serverless-deployment + Hook | 1시간+, AWS 문서 탐색 | 프롬프트 1개 + 자동 검증 |
| 3. 주문 처리 워크플로우 | aws-lambda-durable-functions | 반나절+, ASL 문법 | 프롬프트 1개 + Saga 자동 적용 |
| 4. 프로덕션 강화 | MCP + Hook 통합 | 운영 경험 필수 | 프롬프트 1개 + 운영 노하우 자동 반영 |

### 자동 적용 Best Practice 총정리

| 카테고리 | 적용 항목 |
|---------|----------|
| 보안 | 최소 권한 IAM, 테이블 ARN 한정 |
| 코드 품질 | Powertools, 입력 검증, 에러 핸들링 |
| IaC | Globals 중앙 관리, DeletionPolicy, SAM 자동 검증 |
| 안정성 | Saga 패턴, Checkpoint, 멱등성, 에러 분류 |
| 운영 | ESM 튜닝, DLQ, CloudWatch Alarm, Concurrency |

### 닫는 메시지

AWS 경험자에게 전달할 핵심: "여러분이 이미 알고 있는 Best Practice를 플러그인이 자동으로 적용합니다. 아는 것을 매번 수동으로 하는 데 시간을 쓰지 마세요."
