# AWS Serverless Agent Plugin 활용 예시 블로그 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** GitHub에 포스팅할 aws-serverless 플러그인 활용 예시 블로그 마크다운 문서 작성

**Architecture:** "FoodOrder" 음식 주문 처리 시스템을 관통 프로젝트로, 4개 시나리오(Lambda → SAM → Durable Functions → 프로덕션)를 점진적 복잡도로 전개. 각 시나리오는 Before 한 줄 → 프롬프트 → 실행 흐름 → 결과물(코드 스니펫) → Best Practice 구조.

**Tech Stack:** 마크다운, Python(코드 스니펫), SAM template YAML, Durable Execution SDK Python

**Spec:** `docs/superpowers/specs/2026-03-26-aws-serverless-plugin-usage-examples-design.md`

**Target file:** `blog-post-usage-examples.md` (프로젝트 루트)

---

## File Structure

| File | Responsibility |
|------|---------------|
| `blog-post-usage-examples.md` | 블로그 본문 전체 (단일 마크다운 파일) |

블로그 포스트이므로 단일 파일로 작성. 섹션별로 Task를 나누어 순차적으로 작성.

---

### Task 1: 블로그 헤더 + 소개 + 사전 준비 섹션

**Files:**
- Create: `blog-post-usage-examples.md`

- [ ] **Step 1: 블로그 헤더와 소개 섹션 작성**

아래 내용으로 `blog-post-usage-examples.md` 파일을 생성:

```markdown
# 프롬프트 4개로 완성하는 서버리스 — AWS Serverless Agent Plugin 활용 가이드

**작성일:** 2026-03-26

---

## 소개 — 왜 AI 에이전트 + 서버리스인가

서버리스 애플리케이션을 만들 때 가장 많은 시간이 드는 곳은 비즈니스 로직이 아닙니다.
**IAM 정책 작성, SAM 템플릿 구성, 이벤트 소스 매핑 튜닝, 모니터링 설정** — 매번 반복하지만 매번 문서를 찾아봐야 하는 작업들입니다.

AWS Serverless Agent Plugin은 이 반복을 없앱니다. AI 코딩 어시스턴트에 서버리스 전문 지식을 패키징하여, **프롬프트 한 줄에 Best Practice가 내장된 코드와 인프라를 생성**합니다.

이 글에서는 **"FoodOrder" 음식 주문 처리 시스템**을 빈 디렉토리에서 프로덕션 레디까지 만들어가며, 플러그인의 4가지 핵심 기능을 체험합니다.

| 시나리오 | 플러그인 기능 | 결과 |
|---------|-------------|------|
| 1. 주문 API 생성 | `aws-lambda` 스킬 | Lambda + API Gateway + DynamoDB |
| 2. SAM 배포 자동화 | `aws-serverless-deployment` 스킬 + Hook | IaC 프로젝트 + 로컬 테스트 + 배포 |
| 3. 주문 처리 워크플로우 | `aws-lambda-durable-functions` 스킬 | Saga 패턴 + Checkpoint 오케스트레이션 |
| 4. 프로덕션 강화 | MCP 서버 + Hook 통합 | ESM 최적화 + 모니터링 + DLQ |
```

- [ ] **Step 2: 사전 준비 섹션 작성**

`blog-post-usage-examples.md`에 이어서 추가:

```markdown
---

## 사전 준비

### 플러그인 설치

Claude Code에서 아래 명령어로 설치합니다:

\```bash
/plugin install aws-serverless@claude-plugins-official
\```

### 플러그인 구성 요소

설치하면 아래 5개의 구성 요소가 활성화됩니다:

| 구성 요소 | 이름 | 역할 |
|----------|------|------|
| 스킬 | `aws-lambda` | Lambda 함수 설계, 빌드, 배포, 테스트, 디버그 |
| 스킬 | `aws-serverless-deployment` | SAM/CDK 배포 워크플로우 |
| 스킬 | `aws-lambda-durable-functions` | 상태 유지 워크플로우, Saga 패턴, Checkpoint |
| MCP 서버 | `aws-serverless-mcp` | 서버리스 개발 가이드, 스캐폴딩, IaC 생성, 배포 |
| Hook | `SAM template validation` | `template.yaml` 수정 시 `sam validate` 자동 실행 |

### AWS 자격 증명

AWS CLI가 구성되어 있어야 합니다:

\```bash
aws sts get-caller-identity
\```

### 관통 프로젝트: FoodOrder

빈 디렉토리에서 시작합니다:

\```bash
mkdir food-order-api && cd food-order-api
\```

이제 프롬프트 4개로 이 디렉토리를 프로덕션 레디 서버리스 앱으로 만들어보겠습니다.
```

- [ ] **Step 3: 작성 내용 확인**

작성된 파일을 읽어서 마크다운 구조와 내용이 올바른지 확인.

---

### Task 2: 시나리오 1 — 주문 API 생성

**Files:**
- Modify: `blog-post-usage-examples.md`

- [ ] **Step 1: Before + 프롬프트 섹션 작성**

`blog-post-usage-examples.md`에 이어서 추가:

```markdown
---

## 시나리오 1: 주문 API 생성

> ❌ **Before:** Lambda 콘솔에서 함수 생성 → API Gateway 구성 → DynamoDB 테이블 생성 → IAM 역할/정책 작성 → 통합 연결 → 테스트까지 최소 30분+, 10개 이상의 화면 전환

💬 **프롬프트**

\```
Python으로 음식 주문 REST API를 만들어줘.
- POST /orders: 주문 생성 (메뉴, 수량, 고객정보)
- GET /orders/{id}: 주문 조회
- DynamoDB에 저장
\```
```

- [ ] **Step 2: 실행 흐름 섹션 작성**

```markdown
🔧 **플러그인 실행 흐름**

`aws-lambda` 스킬이 자동으로 트리거됩니다:

1. **이벤트 소스 결정** — REST API 요구사항을 인식하여 API Gateway HTTP API 선택
2. **핸들러 코드 생성** — POST/GET 라우팅, DynamoDB CRUD, 입력값 검증
3. **DynamoDB 스키마 설계** — `orderId`를 파티션 키로, 주문 데이터를 속성으로
4. **이벤트 매핑** — API Gateway → Lambda 통합 이벤트 구조를 핸들러에 정확히 반영
5. **IAM 정책 생성** — DynamoDB `PutItem`/`GetItem`만 허용하는 최소 권한 정책
```

- [ ] **Step 3: 결과물 코드 스니펫 작성**

```markdown
📦 **결과물**

\```python
# app.py — Lambda 핸들러
import json
import uuid
import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()
app = APIGatewayHttpResolver()

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("FoodOrders")


@app.post("/orders")
@tracer.capture_method
def create_order():
    body = app.current_event.json_body
    order_id = str(uuid.uuid4())

    item = {
        "orderId": order_id,
        "menu": body["menu"],
        "quantity": body["quantity"],
        "customer": body["customer"],
        "status": "CREATED",
    }
    table.put_item(Item=item)

    return {"statusCode": 201, "body": {"orderId": order_id}}


@app.get("/orders/<order_id>")
@tracer.capture_method
def get_order(order_id: str):
    response = table.get_item(Key={"orderId": order_id})
    if "Item" not in response:
        return {"statusCode": 404, "body": {"message": "Order not found"}}
    return {"statusCode": 200, "body": response["Item"]}


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
\```

IAM 정책 — 테이블 ARN으로 범위를 한정한 최소 권한:

\```json
{
  "Effect": "Allow",
  "Action": ["dynamodb:PutItem", "dynamodb:GetItem"],
  "Resource": "arn:aws:dynamodb:*:*:table/FoodOrders"
}
\```
```

- [ ] **Step 4: Best Practice 섹션 작성**

```markdown
💡 **플러그인이 자동으로 적용한 Best Practice**

| Best Practice | 적용 내용 |
|--------------|----------|
| **Powertools for AWS Lambda** | `Logger`, `Tracer`로 구조화된 로깅과 X-Ray 트레이싱 자동 설정 |
| **API Gateway 이벤트 파싱** | `APIGatewayHttpResolver`로 라우팅 — 수동 `event["httpMethod"]` 파싱 불필요 |
| **최소 권한 IAM** | `PutItem`/`GetItem`만 허용, 테이블 ARN 한정. `dynamodb:*`나 `Resource: *` 미사용 |
| **입력값 검증** | `json_body` 파싱으로 잘못된 요청 자동 거부 |

수동으로 하면 "일단 `dynamodb:*`로 넓게 열고 나중에 좁히자"라고 하기 쉽습니다. 플러그인은 처음부터 좁게 시작합니다.
```

- [ ] **Step 5: 작성 내용 확인**

시나리오 1 전체를 읽어서 코드 스니펫, 마크다운 구조, Before/After 대비가 명확한지 확인.

---

### Task 3: 시나리오 2 — SAM으로 배포 자동화

**Files:**
- Modify: `blog-post-usage-examples.md`

- [ ] **Step 1: Before + 프롬프트 섹션 작성**

```markdown
---

## 시나리오 2: SAM으로 배포 자동화

> ❌ **Before:** SAM 프로젝트 구조 생성 → template.yaml에 Lambda, API Gateway, DynamoDB, IAM Role 정의 → sam build → sam local invoke 테스트 → sam deploy 설정 → samconfig.toml 작성까지 AWS 문서를 오가며 1시간+

💬 **프롬프트**

\```
시나리오 1에서 만든 주문 API를 SAM 프로젝트로 구성하고 배포해줘.
로컬 테스트도 할 수 있게 해줘.
\```
```

- [ ] **Step 2: 실행 흐름 섹션 작성**

```markdown
🔧 **플러그인 실행 흐름**

`aws-serverless-deployment` 스킬이 트리거됩니다:

1. **프로젝트 재구성** — 시나리오 1의 코드를 SAM 디렉토리 구조로 배치
2. **template.yaml 생성** — Lambda, HttpApi, DynamoDB 테이블, IAM Role을 하나의 템플릿에 정의
3. **Hook 자동 실행** — template.yaml 작성 완료 시 `sam validate`가 자동으로 실행되어 문법 오류를 즉시 차단
4. **테스트 이벤트 생성** — `sam local invoke`용 API Gateway 페이로드 샘플
5. **배포 가이드** — `sam build` → `sam deploy --guided` 단계별 안내
```

- [ ] **Step 3: 결과물 — 프로젝트 구조 + template.yaml 스니펫 작성**

```markdown
📦 **결과물**

프로젝트 구조:

\```
food-order-api/
├── template.yaml
├── samconfig.toml
├── src/
│   └── order_handler/
│       ├── app.py
│       └── requirements.txt
├── events/
│   ├── create_order.json
│   └── get_order.json
└── tests/
    └── unit/
        └── test_handler.py
\```

`template.yaml` — 전체 인프라를 하나의 파일로 정의:

\```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
Description: FoodOrder API

Globals:
  Function:
    Runtime: python3.13
    Timeout: 30
    MemorySize: 256
    Tracing: Active
    Environment:
      Variables:
        TABLE_NAME: !Ref FoodOrdersTable
        POWERTOOLS_SERVICE_NAME: food-order-api
        LOG_LEVEL: INFO

Resources:
  OrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/order_handler/
      Handler: app.lambda_handler
      Events:
        CreateOrder:
          Type: HttpApi
          Properties:
            Path: /orders
            Method: post
        GetOrder:
          Type: HttpApi
          Properties:
            Path: /orders/{orderId}
            Method: get
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref FoodOrdersTable

  FoodOrdersTable:
    Type: AWS::DynamoDB::Table
    DeletionPolicy: Retain
    Properties:
      TableName: FoodOrders
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: orderId
          AttributeType: S
      KeySchema:
        - AttributeName: orderId
          KeyType: HASH

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ServerlessHttpApi}.execute-api.${AWS::Region}.amazonaws.com"
\```

로컬 테스트용 이벤트 (`events/create_order.json`):

\```json
{
  "httpMethod": "POST",
  "path": "/orders",
  "body": "{\"menu\": \"비빔밥\", \"quantity\": 2, \"customer\": {\"name\": \"홍길동\", \"phone\": \"010-1234-5678\"}}",
  "requestContext": {
    "http": { "method": "POST", "path": "/orders" }
  }
}
\```

\```bash
# 로컬 테스트
sam build
sam local invoke OrderFunction -e events/create_order.json

# 배포
sam deploy --guided
\```
```

- [ ] **Step 4: Best Practice 섹션 작성**

```markdown
💡 **플러그인이 자동으로 적용한 Best Practice**

| Best Practice | 적용 내용 |
|--------------|----------|
| **Globals 중앙 관리** | Runtime, Timeout, MemorySize, Tracing을 Globals에서 한 번 정의 — 함수가 추가되어도 일관성 유지 |
| **DeletionPolicy: Retain** | DynamoDB 테이블에 적용 — CloudFormation 스택 삭제 시에도 데이터 보존 |
| **SAM 정책 템플릿** | `DynamoDBCrudPolicy`로 IAM 정책을 간결하게 — 수동 ARN 구성 불필요 |
| **테스트 이벤트 자동 생성** | API Gateway HTTP API 페이로드 형식을 정확히 반영한 샘플 이벤트 |
| **Hook: 자동 검증** | template.yaml을 수정할 때마다 `sam validate`가 자동 실행되어 오타나 잘못된 속성을 배포 전에 차단 |

특히 **SAM Hook**은 눈에 보이지 않지만 강력합니다. template.yaml에서 `Runtime: python3.13`을 `Runtime: pytohn3.13`으로 오타를 내면, 저장 즉시 Hook이 잡아냅니다.
```

- [ ] **Step 5: 작성 내용 확인**

시나리오 2 전체를 읽어서 template.yaml YAML 문법, 프로젝트 구조 트리, 커맨드가 정확한지 확인.

---

### Task 4: 시나리오 3 — 주문 처리 워크플로우

**Files:**
- Modify: `blog-post-usage-examples.md`

- [ ] **Step 1: Before + 프롬프트 섹션 작성**

```markdown
---

## 시나리오 3: 주문 처리 워크플로우

> ❌ **Before:** Step Functions ASL JSON 수동 작성 → 각 단계별 Lambda 함수 개별 생성 → 에러/재시도/보상 로직 직접 구현 → 상태 전이 테스트까지 ASL 문법과 씨름하며 반나절+

💬 **프롬프트**

\```
주문이 생성되면 자동으로 실행되는 워크플로우를 만들어줘.
1. 결제 처리
2. 재고 확인 및 차감
3. 배송 접수
4. 고객 알림 (이메일)
결제 실패 시 주문 취소, 배송 접수 실패 시 재고 원복해줘.
\```
```

- [ ] **Step 2: 실행 흐름 섹션 작성**

```markdown
🔧 **플러그인 실행 흐름**

`aws-lambda-durable-functions` 스킬이 트리거됩니다:

1. **워크플로우 설계** — 4단계 순차 실행을 Durable Functions 패턴으로 구성
2. **Saga 패턴 자동 적용** — 각 단계에 보상(compensation) 로직 매핑
   - 결제 실패 → 주문 상태 `CANCELLED`
   - 재고 차감 후 배송 실패 → 재고 원복 (보상 트랜잭션)
3. **Checkpoint 삽입** — 각 step에 자동 체크포인트 → 중간 실패 시 마지막 성공 지점부터 재개
4. **재시도 전략 구성** — 재시도 가능한 에러(네트워크)와 불가능한 에러(잔액 부족)를 구분
5. **트리거 연결** — DynamoDB Streams로 주문 생성 이벤트 감지 → 워크플로우 자동 시작
```

- [ ] **Step 3: 결과물 — 오케스트레이터 코드 스니펫 작성**

```markdown
📦 **결과물**

**오케스트레이터** — 4단계 워크플로우 + Saga 보상 로직:

\```python
# src/workflow/order_processor.py
from aws_durable_execution_sdk_python import durable_execution, DurableContext
from aws_durable_execution_sdk_python.config import Duration
from aws_durable_execution_sdk_python.retries import (
    RetryStrategyConfig, create_retry_strategy, JitterStrategy
)

from steps.payment import process_payment, cancel_payment
from steps.inventory import deduct_inventory, restore_inventory
from steps.shipping import request_shipping
from steps.notification import send_notification

# 재시도 가능한 에러용 전략 (네트워크 타임아웃 등)
retryable_strategy = create_retry_strategy(RetryStrategyConfig(
    max_attempts=3,
    initial_delay=Duration.from_seconds(1),
    max_delay=Duration.from_seconds(30),
    backoff_rate=2.0,
    jitter_strategy=JitterStrategy.FULL,
))


@durable_execution
def handler(event, context: DurableContext):
    order = event["detail"]
    order_id = order["orderId"]
    compensations = []  # Saga 보상 스택

    try:
        # Step 1: 결제 처리
        payment = context.step(
            func=lambda: process_payment(order_id, order["total"]),
            config={"retry_strategy": retryable_strategy},
        )
        compensations.append(lambda: cancel_payment(payment["paymentId"]))

        # Step 2: 재고 차감
        inventory = context.step(
            func=lambda: deduct_inventory(order["menu"], order["quantity"]),
            config={"retry_strategy": retryable_strategy},
        )
        compensations.append(lambda: restore_inventory(order["menu"], order["quantity"]))

        # Step 3: 배송 접수
        shipping = context.step(
            func=lambda: request_shipping(order_id, order["customer"]),
            config={"retry_strategy": retryable_strategy},
        )

        # Step 4: 고객 알림
        context.step(
            func=lambda: send_notification(
                order["customer"]["email"],
                f"주문 {order_id} 배송이 시작되었습니다. 송장번호: {shipping['trackingId']}",
            ),
        )

        return {"status": "COMPLETED", "orderId": order_id}

    except Exception as e:
        # Saga 보상: 역순으로 실행
        for compensate in reversed(compensations):
            context.step(func=compensate)

        context.step(
            func=lambda: update_order_status(order_id, "FAILED", str(e)),
        )
        return {"status": "FAILED", "orderId": order_id, "error": str(e)}
\```

**Step 함수 예시** — 결제 처리 + 보상:

\```python
# src/workflow/steps/payment.py
import boto3

dynamodb = boto3.resource("dynamodb")
payments_table = dynamodb.Table("Payments")


def process_payment(order_id: str, amount: int) -> dict:
    """결제 처리 — 외부 PG 연동 시뮬레이션"""
    payment_id = f"pay-{order_id}"
    payments_table.put_item(Item={
        "paymentId": payment_id,
        "orderId": order_id,
        "amount": amount,
        "status": "CHARGED",
    })
    return {"paymentId": payment_id, "status": "CHARGED"}


def cancel_payment(payment_id: str) -> dict:
    """결제 취소 (Saga 보상)"""
    payments_table.update_item(
        Key={"paymentId": payment_id},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": "CANCELLED"},
    )
    return {"paymentId": payment_id, "status": "CANCELLED"}
\```
```

- [ ] **Step 4: Best Practice 섹션 작성**

```markdown
💡 **플러그인이 자동으로 적용한 Best Practice**

| Best Practice | 적용 내용 |
|--------------|----------|
| **Saga 패턴** | `compensations` 스택으로 실패 시 역순 보상 — 분산 트랜잭션의 정석 |
| **Checkpoint/Replay** | 각 `context.step()`이 자동 체크포인트. Lambda 재시작 시 마지막 성공 step부터 재개 |
| **에러 분류** | `retryable_strategy`로 네트워크 에러는 재시도, 비즈니스 에러(잔액 부족)는 즉시 보상 |
| **멱등성** | step 이름(`process_payment`, `deduct_inventory`)으로 중복 실행 방지 — Replay 시 이미 완료된 step은 스킵 |

핵심은 **Replay 모델**입니다. Lambda가 타임아웃이나 메모리 부족으로 중단되어도, 다음 실행 시 `context.step()`이 이전 결과를 캐시에서 복원합니다. 개발자가 직접 상태를 저장/복원하는 코드를 작성할 필요가 없습니다.

\```
정상 실행:  payment ✅ → inventory ✅ → shipping ✅ → notification ✅ → COMPLETED
배송 실패:  payment ✅ → inventory ✅ → shipping ❌ → [보상] inventory 원복 → payment 취소 → FAILED
Lambda 재시작: payment ✅(캐시) → inventory ✅(캐시) → shipping 🔄(재시도) → ...
\```
```

- [ ] **Step 5: 작성 내용 확인**

시나리오 3 전체를 읽어서 Durable Functions SDK import 경로, `context.step()` 사용법, Saga 패턴 구조가 정확한지 확인. SDK 레퍼런스 (`aws_durable_execution_sdk_python`)와 일치하는지 대조.

---

### Task 5: 시나리오 4 — 프로덕션 강화

**Files:**
- Modify: `blog-post-usage-examples.md`

- [ ] **Step 1: Before + 프롬프트 섹션 작성**

```markdown
---

## 시나리오 4: 프로덕션 강화

> ❌ **Before:** CloudWatch 메트릭 설정, DynamoDB Streams ESM 튜닝(batch size, parallelization factor, retry), 에러 알림 구성, 성능 테스트까지 운영 경험 없이는 놓치는 항목 투성이

💬 **프롬프트**

\```
이 주문 처리 시스템을 프로덕션에 올리기 전에 점검해줘.
- DynamoDB Streams → Lambda 연결 최적화
- 주요 메트릭 모니터링 설정
- 에러 발생 시 알림
- 일일 주문 1만 건 예상
\```
```

- [ ] **Step 2: 실행 흐름 섹션 작성**

```markdown
🔧 **플러그인 실행 흐름**

이번에는 스킬 단독이 아닌, **MCP 서버 + Hook + 스킬이 통합**되어 동작합니다:

1. **`aws-serverless-mcp` 서버** — 현재 template.yaml을 분석하여 개선 포인트 식별
2. **`esm_optimize` 도구** — DynamoDB Streams Event Source Mapping 설정 최적화
   - 일일 1만 건 기반으로 BatchSize, ParallelizationFactor 계산
   - BisectBatchOnFunctionError, MaximumRetryAttempts 설정
   - 실패 이벤트용 SQS DLQ 추가
3. **`get_lambda_guidance` 도구** — 동시성, 메모리, 타임아웃 권장값 산출
4. **`get_metrics` 도구** — 핵심 CloudWatch 메트릭과 알람 설정 가이드
5. **Hook 자동 실행** — template.yaml 수정 완료 시 `sam validate` 검증
```

- [ ] **Step 3: 결과물 — template.yaml 프로덕션 설정 스니펫 작성**

```markdown
📦 **결과물**

`template.yaml`에 추가된 프로덕션 설정:

\```yaml
# --- ESM 최적화 ---
OrderWorkflowFunction:
  Type: AWS::Serverless::Function
  Properties:
    # ... (기존 설정)
    ReservedConcurrentExecutions: 10
    Events:
      DynamoDBStream:
        Type: DynamoDB
        Properties:
          Stream: !GetAtt FoodOrdersTable.StreamArn
          StartingPosition: TRIM_HORIZON
          BatchSize: 100
          MaximumBatchingWindowInSeconds: 5
          ParallelizationFactor: 2
          BisectBatchOnFunctionError: true
          MaximumRetryAttempts: 3
          DestinationConfig:
            OnFailure:
              Destination: !GetAtt OrderDLQ.Arn

# --- DLQ ---
OrderDLQ:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: food-order-dlq
    MessageRetentionPeriod: 1209600  # 14일

# --- 모니터링 ---
LambdaErrorAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: FoodOrder-Lambda-Errors
    MetricName: Errors
    Namespace: AWS/Lambda
    Dimensions:
      - Name: FunctionName
        Value: !Ref OrderWorkflowFunction
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
    AlarmActions:
      - !Ref AlertTopic

DLQMessageAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: FoodOrder-DLQ-Messages
    MetricName: ApproximateNumberOfMessagesVisible
    Namespace: AWS/SQS
    Dimensions:
      - Name: QueueName
        Value: !GetAtt OrderDLQ.QueueName
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
    AlarmActions:
      - !Ref AlertTopic

AlertTopic:
  Type: AWS::SNS::Topic
  Properties:
    TopicName: food-order-alerts

AlertSubscription:
  Type: AWS::SNS::Subscription
  Properties:
    TopicArn: !Ref AlertTopic
    Protocol: email
    Endpoint: ops-team@example.com
\```
```

- [ ] **Step 4: Best Practice 섹션 작성**

```markdown
💡 **플러그인이 자동으로 적용한 Best Practice**

| Best Practice | 적용 내용 |
|--------------|----------|
| **ESM 튜닝** | 일일 1만 건 = ~0.12 TPS. `BatchSize: 100` + `MaximumBatchingWindowInSeconds: 5`로 효율적 배치 처리 |
| **BisectBatchOnFunctionError** | 배치 내 1건 실패 시 전체 재시도 대신 이진 분할 — 정상 레코드는 통과, 실패 레코드만 격리 |
| **DLQ 패턴** | 3회 재시도 후에도 실패한 이벤트를 SQS로 보존 — 데이터 유실 없이 후속 분석/재처리 가능 |
| **DLQ 알람** | DLQ에 메시지가 쌓이면 즉시 알림 — "조용한 실패"를 방지 |
| **ReservedConcurrentExecutions** | 동시 실행 수 제한으로 DynamoDB 쓰로틀링 방지 + 비용 예측 가능성 확보 |
| **Hook 안전망** | 위 설정을 추가하는 과정에서 template.yaml을 여러 번 수정하지만, 매번 Hook이 `sam validate`를 실행하여 문법 오류 차단 |

운영 경험이 있는 개발자라면 위 항목들을 알고 있을 겁니다. 하지만 **매번 기억해서 빠짐없이 적용하는 것**은 다른 문제입니다. 플러그인은 트래픽 수치(1만 건)를 입력하면 적절한 설정값을 계산하고, 빠뜨리기 쉬운 DLQ와 알람까지 자동으로 추가합니다.
```

- [ ] **Step 5: 작성 내용 확인**

시나리오 4 전체를 읽어서 CloudFormation 리소스 타입, 속성명, ESM 파라미터가 정확한지 확인.

---

### Task 6: 마무리 섹션 + 최종 검수

**Files:**
- Modify: `blog-post-usage-examples.md`

- [ ] **Step 1: 마무리 요약 테이블 작성**

```markdown
---

## 마무리 — 프롬프트 4개의 결과

빈 디렉토리에서 시작해 4개의 프롬프트로 도달한 결과를 정리합니다.

### 시나리오별 요약

| 시나리오 | 스킬/도구 | Before (수동) | After (플러그인) |
|---------|----------|-------------|----------------|
| 1. 주문 API 생성 | `aws-lambda` | 30분+, 10개 화면 전환 | 프롬프트 1개 |
| 2. SAM 배포 자동화 | `aws-serverless-deployment` + Hook | 1시간+, AWS 문서 탐색 | 프롬프트 1개 + 자동 검증 |
| 3. 주문 처리 워크플로우 | `aws-lambda-durable-functions` | 반나절+, ASL 문법 | 프롬프트 1개 + Saga 자동 적용 |
| 4. 프로덕션 강화 | MCP + Hook 통합 | 운영 경험 필수 | 프롬프트 1개 + 운영 노하우 자동 반영 |
```

- [ ] **Step 2: Best Practice 총정리 작성**

```markdown
### 플러그인이 자동으로 적용한 Best Practice 총정리

| 카테고리 | 적용 항목 |
|---------|----------|
| **보안** | 최소 권한 IAM, 테이블 ARN 한정, `*` 미사용 |
| **코드 품질** | Powertools (Logger, Tracer), 입력 검증, 에러 핸들링 |
| **IaC** | Globals 중앙 관리, DeletionPolicy: Retain, SAM 자동 검증(Hook) |
| **안정성** | Saga 패턴, Checkpoint/Replay, 멱등성, 재시도 전략 분류 |
| **운영** | ESM 튜닝, DLQ + DLQ 알람, CloudWatch Alarm, Concurrency 제한 |

이 항목들은 AWS Well-Architected Framework의 서버리스 렌즈에서 권장하는 패턴들입니다. 플러그인은 이 지식을 프롬프트 한 줄에 자동으로 적용합니다.
```

- [ ] **Step 3: 닫는 메시지 + 리소스 링크 작성**

```markdown
---

## 시작하기

\```bash
/plugin install aws-serverless@claude-plugins-official
\```

설치 후 "Python으로 Lambda 함수 만들어줘"라고 입력해보세요. 플러그인이 나머지를 안내합니다.

### 리소스

- [Agent Plugins for AWS (GitHub)](https://github.com/awslabs/agent-plugins)
- [AWS Serverless Application Model (SAM)](https://aws.amazon.com/serverless/sam/)
- [AWS Lambda durable functions](https://docs.aws.amazon.com/lambda/latest/dg/durable-functions.html)
- [Powertools for AWS Lambda (Python)](https://docs.powertools.aws.dev/lambda/python/latest/)
```

- [ ] **Step 4: 전체 문서 최종 검수**

전체 `blog-post-usage-examples.md`를 처음부터 끝까지 읽으며 확인:
- 마크다운 문법 오류 (닫히지 않은 코드 블록, 깨진 테이블)
- 시나리오 간 스토리 연결 자연스러운지 (1→2→3→4 흐름)
- 코드 스니펫 일관성 (변수명, 테이블명 `FoodOrders` 통일)
- 오타, 잘못된 AWS 리소스 타입/속성명
- Before/After 대비가 각 시나리오에 있는지

- [ ] **Step 5: 완료 보고**

사용자에게 완성된 블로그 파일 경로와 전체 구조를 보고.
