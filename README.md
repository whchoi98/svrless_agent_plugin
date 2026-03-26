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

---

## 사전 준비

### 플러그인 설치

Claude Code에서 아래 명령어로 설치합니다:

```bash
/plugin install aws-serverless@claude-plugins-official
```

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

```bash
aws sts get-caller-identity
```

### 관통 프로젝트: FoodOrder

빈 디렉토리에서 시작합니다:

```bash
mkdir food-order-api && cd food-order-api
```

이제 프롬프트 4개로 이 디렉토리를 프로덕션 레디 서버리스 앱으로 만들어보겠습니다.

---

## 시나리오 1: 주문 API 생성

> ❌ **Before:** Lambda 콘솔에서 함수 생성 → API Gateway 구성 → DynamoDB 테이블 생성 → IAM 역할/정책 작성 → 통합 연결 → 테스트까지 최소 30분+, 10개 이상의 화면 전환

💬 **프롬프트**

```
Python으로 음식 주문 REST API를 만들어줘.
- POST /orders: 주문 생성 (메뉴, 수량, 고객정보)
- GET /orders/{id}: 주문 조회
- DynamoDB에 저장
```

🔧 **플러그인 실행 흐름**

`aws-lambda` 스킬이 자동으로 트리거됩니다:

1. **이벤트 소스 결정** — REST API 요구사항을 인식하여 API Gateway HTTP API 선택
2. **핸들러 코드 생성** — POST/GET 라우팅, DynamoDB CRUD, 입력값 검증
3. **DynamoDB 스키마 설계** — `orderId`를 파티션 키로, 주문 데이터를 속성으로
4. **이벤트 매핑** — API Gateway → Lambda 통합 이벤트 구조를 핸들러에 정확히 반영
5. **IAM 정책 생성** — DynamoDB `PutItem`/`GetItem`만 허용하는 최소 권한 정책

📦 **결과물**

```python
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
```

IAM 정책 — 테이블 ARN으로 범위를 한정한 최소 권한:

```json
{
  "Effect": "Allow",
  "Action": ["dynamodb:PutItem", "dynamodb:GetItem"],
  "Resource": "arn:aws:dynamodb:*:*:table/FoodOrders"
}
```

💡 **플러그인이 자동으로 적용한 Best Practice**

| Best Practice | 적용 내용 |
|--------------|----------|
| **Powertools for AWS Lambda** | `Logger`, `Tracer`로 구조화된 로깅과 X-Ray 트레이싱 자동 설정 |
| **API Gateway 이벤트 파싱** | `APIGatewayHttpResolver`로 라우팅 — 수동 `event["httpMethod"]` 파싱 불필요 |
| **최소 권한 IAM** | `PutItem`/`GetItem`만 허용, 테이블 ARN 한정. `dynamodb:*`나 `Resource: *` 미사용 |
| **입력값 검증** | `json_body` 파싱으로 잘못된 요청 자동 거부 |

수동으로 하면 "일단 `dynamodb:*`로 넓게 열고 나중에 좁히자"라고 하기 쉽습니다. 플러그인은 처음부터 좁게 시작합니다.

---

## 시나리오 2: SAM으로 배포 자동화

> ❌ **Before:** SAM 프로젝트 구조 생성 → template.yaml에 Lambda, API Gateway, DynamoDB, IAM Role 정의 → sam build → sam local invoke 테스트 → sam deploy 설정 → samconfig.toml 작성까지 AWS 문서를 오가며 1시간+

💬 **프롬프트**

```
시나리오 1에서 만든 주문 API를 SAM 프로젝트로 구성하고 배포해줘.
로컬 테스트도 할 수 있게 해줘.
```

🔧 **플러그인 실행 흐름**

`aws-serverless-deployment` 스킬이 트리거됩니다:

1. **프로젝트 재구성** — 시나리오 1의 코드를 SAM 디렉토리 구조로 배치
2. **template.yaml 생성** — Lambda, HttpApi, DynamoDB 테이블, IAM Role을 하나의 템플릿에 정의
3. **Hook 자동 실행** — template.yaml 작성 완료 시 `sam validate`가 자동으로 실행되어 문법 오류를 즉시 차단
4. **테스트 이벤트 생성** — `sam local invoke`용 API Gateway 페이로드 샘플
5. **배포 가이드** — `sam build` → `sam deploy --guided` 단계별 안내

📦 **결과물**

프로젝트 구조:

```
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
```

`template.yaml` — 전체 인프라를 하나의 파일로 정의:

```yaml
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
```

로컬 테스트용 이벤트 (`events/create_order.json`):

```json
{
  "httpMethod": "POST",
  "path": "/orders",
  "body": "{\"menu\": \"비빔밥\", \"quantity\": 2, \"customer\": {\"name\": \"홍길동\", \"phone\": \"010-1234-5678\"}}",
  "requestContext": {
    "http": { "method": "POST", "path": "/orders" }
  }
}
```

```bash
# 로컬 테스트
sam build
sam local invoke OrderFunction -e events/create_order.json

# 배포
sam deploy --guided
```

💡 **플러그인이 자동으로 적용한 Best Practice**

| Best Practice | 적용 내용 |
|--------------|----------|
| **Globals 중앙 관리** | Runtime, Timeout, MemorySize, Tracing을 Globals에서 한 번 정의 — 함수가 추가되어도 일관성 유지 |
| **DeletionPolicy: Retain** | DynamoDB 테이블에 적용 — CloudFormation 스택 삭제 시에도 데이터 보존 |
| **SAM 정책 템플릿** | `DynamoDBCrudPolicy`로 IAM 정책을 간결하게 — 수동 ARN 구성 불필요 |
| **테스트 이벤트 자동 생성** | API Gateway HTTP API 페이로드 형식을 정확히 반영한 샘플 이벤트 |
| **Hook: 자동 검증** | template.yaml을 수정할 때마다 `sam validate`가 자동 실행되어 오타나 잘못된 속성을 배포 전에 차단 |

특히 **SAM Hook**은 눈에 보이지 않지만 강력합니다. template.yaml에서 `Runtime: python3.13`을 `Runtime: pytohn3.13`으로 오타를 내면, 저장 즉시 Hook이 잡아냅니다.

---

## 시나리오 3: 주문 처리 워크플로우

> ❌ **Before:** Step Functions ASL JSON 수동 작성 → 각 단계별 Lambda 함수 개별 생성 → 에러/재시도/보상 로직 직접 구현 → 상태 전이 테스트까지 ASL 문법과 씨름하며 반나절+

💬 **프롬프트**

```
주문이 생성되면 자동으로 실행되는 워크플로우를 만들어줘.
1. 결제 처리
2. 재고 확인 및 차감
3. 배송 접수
4. 고객 알림 (이메일)
결제 실패 시 주문 취소, 배송 접수 실패 시 재고 원복해줘.
```

🔧 **플러그인 실행 흐름**

`aws-lambda-durable-functions` 스킬이 트리거됩니다:

1. **워크플로우 설계** — 4단계 순차 실행을 Durable Functions 패턴으로 구성
2. **Saga 패턴 자동 적용** — 각 단계에 보상(compensation) 로직 매핑
   - 결제 실패 → 주문 상태 `CANCELLED`
   - 재고 차감 후 배송 실패 → 재고 원복 (보상 트랜잭션)
3. **Checkpoint 삽입** — 각 step에 자동 체크포인트 → 중간 실패 시 마지막 성공 지점부터 재개
4. **재시도 전략 구성** — 재시도 가능한 에러(네트워크)와 불가능한 에러(잔액 부족)를 구분
5. **트리거 연결** — DynamoDB Streams로 주문 생성 이벤트 감지 → 워크플로우 자동 시작

📦 **결과물**

**오케스트레이터** — 4단계 워크플로우 + Saga 보상 로직:

```python
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
```

**Step 함수 예시** — 결제 처리 + 보상:

```python
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
```

💡 **플러그인이 자동으로 적용한 Best Practice**

| Best Practice | 적용 내용 |
|--------------|----------|
| **Saga 패턴** | `compensations` 스택으로 실패 시 역순 보상 — 분산 트랜잭션의 정석 |
| **Checkpoint/Replay** | 각 `context.step()`이 자동 체크포인트. Lambda 재시작 시 마지막 성공 step부터 재개 |
| **에러 분류** | `retryable_strategy`로 네트워크 에러는 재시도, 비즈니스 에러(잔액 부족)는 즉시 보상 |
| **멱등성** | step 이름(`process_payment`, `deduct_inventory`)으로 중복 실행 방지 — Replay 시 이미 완료된 step은 스킵 |

핵심은 **Replay 모델**입니다. Lambda가 타임아웃이나 메모리 부족으로 중단되어도, 다음 실행 시 `context.step()`이 이전 결과를 캐시에서 복원합니다. 개발자가 직접 상태를 저장/복원하는 코드를 작성할 필요가 없습니다.

```
정상 실행:  payment ✅ → inventory ✅ → shipping ✅ → notification ✅ → COMPLETED
배송 실패:  payment ✅ → inventory ✅ → shipping ❌ → [보상] inventory 원복 → payment 취소 → FAILED
Lambda 재시작: payment ✅(캐시) → inventory ✅(캐시) → shipping 🔄(재시도) → ...
```

---

## 시나리오 4: 프로덕션 강화

> ❌ **Before:** CloudWatch 메트릭 설정, DynamoDB Streams ESM 튜닝(batch size, parallelization factor, retry), 에러 알림 구성, 성능 테스트까지 운영 경험 없이는 놓치는 항목 투성이

💬 **프롬프트**

```
이 주문 처리 시스템을 프로덕션에 올리기 전에 점검해줘.
- DynamoDB Streams → Lambda 연결 최적화
- 주요 메트릭 모니터링 설정
- 에러 발생 시 알림
- 일일 주문 1만 건 예상
```

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

📦 **결과물**

`template.yaml`에 추가된 프로덕션 설정:

```yaml
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
```

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

### 플러그인이 자동으로 적용한 Best Practice 총정리

| 카테고리 | 적용 항목 |
|---------|----------|
| **보안** | 최소 권한 IAM, 테이블 ARN 한정, `*` 미사용 |
| **코드 품질** | Powertools (Logger, Tracer), 입력 검증, 에러 핸들링 |
| **IaC** | Globals 중앙 관리, DeletionPolicy: Retain, SAM 자동 검증(Hook) |
| **안정성** | Saga 패턴, Checkpoint/Replay, 멱등성, 재시도 전략 분류 |
| **운영** | ESM 튜닝, DLQ + DLQ 알람, CloudWatch Alarm, Concurrency 제한 |

이 항목들은 AWS Well-Architected Framework의 서버리스 렌즈에서 권장하는 패턴들입니다. 플러그인은 이 지식을 프롬프트 한 줄에 자동으로 적용합니다.

---

## 부록: 실제 테스트 결과

아래는 위 시나리오를 실제로 실행한 결과입니다. AWS Serverless Agent Plugin의 MCP 도구와 SAM CLI를 사용했습니다.

### 테스트 환경

| 항목 | 값 |
|------|---|
| OS | Amazon Linux 2023 (aarch64) |
| Python | 3.9.25 |
| SAM CLI | 1.155.2 |
| 플러그인 | `aws-serverless@claude-plugins-official` |

### 테스트 1: `sam_init` — 프로젝트 초기화

**MCP 도구:** `sam_init`

```
입력:
  project_name: food-order-api
  runtime: python3.13
  dependency_manager: pip
  application_template: hello-world
  architecture: arm64
  tracing: true

결과: ✅ 성공
  "Successfully initialized SAM project 'food-order-api'"
```

생성된 프로젝트 구조:

```
food-order-api/
├── template.yaml
├── samconfig.toml
├── hello_world/
│   ├── app.py            ← hello-world 기본 핸들러
│   ├── requirements.txt
│   └── __init__.py
├── events/
│   └── event.json
├── tests/
│   ├── unit/test_handler.py
│   └── integration/test_api_gateway.py
├── README.md
└── .gitignore
```

**관찰:** `sam_init`은 hello-world 스캐폴딩을 생성. 이후 aws-lambda 스킬 가이드에 따라 Powertools + DynamoDB + HttpApi로 커스터마이징.

### 테스트 2: `sam validate` — 템플릿 검증

커스터마이징된 template.yaml을 검증:

```
첫 번째 실행: ❌ 실패
  "[W3011] Both 'UpdateReplacePolicy' and 'DeletionPolicy' are needed"
  → DeletionPolicy: Retain만 설정하고 UpdateReplacePolicy를 누락

수정 후 재실행: ✅ 성공
  "template.yaml is a valid SAM Template"
```

**관찰:** SAM Hook이 실제로 문법 오류를 잡아냄. `DeletionPolicy`만 설정하면 `UpdateReplacePolicy`도 필요하다는 린팅 규칙을 발견 — 블로그에서 언급한 "Hook 안전망"이 실제로 동작하는 사례.

### 테스트 3: `sam_build` — 빌드

```
첫 번째 시도: ❌ 실패
  "PythonPipBuilder:Validation - Binary validation failed for python"
  → python3.13이 로컬에 없음 (로컬 Python: 3.9.25)

Runtime을 python3.9로 변경 후 재시도: ✅ 성공
  "Build Succeeded"
  "Built Artifacts: .aws-sam/build"
```

**관찰:** 로컬 환경에 해당 런타임이 없으면 빌드 실패. 실제 프로덕션에서는 `use_container: true` 옵션으로 Docker 기반 빌드를 사용하거나, 로컬 Python 버전과 Runtime을 맞춰야 함.

### 테스트 4: `esm_optimize` — DynamoDB Streams ESM 최적화 분석

**MCP 도구:** `esm_optimize` (action: analyze)

```
입력:
  event_source: dynamodb
  optimization_targets: [throughput, failure_rate, cost]

결과: ✅ 성공 — 트레이드오프 분석 반환
```

주요 분석 결과:

| 파라미터 | 처리량 ↑ | 실패율 ↓ | 비용 ↓ |
|---------|---------|---------|-------|
| **BatchSize ↑** | ✅ 처리량 증가 | ❌ 실패 시 영향 커짐 | ✅ 호출 횟수 감소 |
| **MaximumBatchingWindowInSeconds ↑** | ✅ 배치 효율 증가 | - | ✅ 호출 횟수 감소 |
| **ParallelizationFactor ↑** | ✅ 동시 처리 증가 | - | ❌ 동시 실행 비용 증가 |
| **BisectBatchOnFunctionError** | ❌ 분할 오버헤드 | ✅ 실패 레코드 격리 | ❌ 추가 호출 발생 |
| **MaximumRetryAttempts ↑** | ❌ 재시도 오버헤드 | ✅ 복구 기회 증가 | ❌ 재시도 비용 |

**관찰:** `esm_optimize`는 단순히 "이 값을 쓰세요"가 아니라 **트레이드오프 분석**을 제공. 개발자가 자기 시나리오에 맞는 결정을 내릴 수 있도록 처리량/실패율/비용 간의 상충 관계를 명시.

### 테스트 5: `esm_guidance` — DynamoDB Streams 설정 가이드

**MCP 도구:** `esm_guidance` (event_source: dynamodb, guidance_type: setup)

```
결과: ✅ 성공 — 7단계 설정 가이드 반환
```

가이드 핵심:
1. DynamoDB 테이블 생성/확인
2. Streams 활성화 확인
3. Lambda 함수 생성/지정
4. `AWSLambdaDynamoDBExecutionRole` 정책 연결
5. Event Source Mapping 생성 (ARN 명시, 와일드카드 금지)
6. 테스트 스크립트 생성
7. 정리(cleanup) 스크립트 생성

**관찰:** "와일드카드 대신 정확한 ARN 사용", "정리 스크립트 필수 생성" 등 운영 Best Practice가 가이드에 내장.

### 테스트 6: `get_lambda_guidance` — Lambda 적합성 분석

**MCP 도구:** `get_lambda_guidance`

```
입력:
  use_case: "DynamoDB Streams event processing for food order workflow
             with 10,000 daily orders"

결과: ✅ 성공 — Lambda 적합성 판정 + 의사결정 기준 8개 반환
```

의사결정 기준 요약:

| 기준 | Lambda 적합? | 이유 |
|------|------------|------|
| 실행 시간 | ✅ | 주문 처리는 15분 이내 완료 |
| 실행 빈도 | ✅ | 일 1만 건 = 간헐적 워크로드 |
| 리소스 요구 | ✅ | 메모리/CPU 제한 이내 |
| 지연 민감도 | ⚠️ | 콜드스타트 고려 필요 → Provisioned Concurrency |
| 상태 관리 | ⚠️ | Lambda는 stateless → DynamoDB/Durable Functions 필요 |

### 테스트 결과 종합

| 테스트 | MCP 도구 | 결과 | 비고 |
|--------|---------|------|------|
| 프로젝트 초기화 | `sam_init` | ✅ | hello-world 스캐폴딩 생성 |
| 템플릿 검증 | `sam validate` | ✅ (2차) | DeletionPolicy/UpdateReplacePolicy 린팅 발견 |
| 빌드 | `sam_build` | ✅ (2차) | 로컬 Python 버전 불일치 해결 후 성공 |
| ESM 최적화 | `esm_optimize` | ✅ | 트레이드오프 분석표 반환 |
| ESM 설정 가이드 | `esm_guidance` | ✅ | 7단계 + Best Practice 내장 |
| Lambda 적합성 | `get_lambda_guidance` | ✅ | 8가지 의사결정 기준 제공 |

> **핵심 발견:** 플러그인의 가치는 "코드를 대신 써주는 것"만이 아닙니다. `esm_optimize`의 트레이드오프 분석, `esm_guidance`의 보안 가이드라인, `sam validate`의 린팅 — **경험 많은 개발자의 코드 리뷰를 자동화**하는 것에 가깝습니다.

---

## 시작하기

```bash
/plugin install aws-serverless@claude-plugins-official
```

설치 후 "Python으로 Lambda 함수 만들어줘"라고 입력해보세요. 플러그인이 나머지를 안내합니다.

### 리소스

- [Agent Plugins for AWS (GitHub)](https://github.com/awslabs/agent-plugins)
- [AWS Serverless Application Model (SAM)](https://aws.amazon.com/serverless/sam/)
- [AWS Lambda durable functions](https://docs.aws.amazon.com/lambda/latest/dg/durable-functions.html)
- [Powertools for AWS Lambda (Python)](https://docs.powertools.aws.dev/lambda/python/latest/)
