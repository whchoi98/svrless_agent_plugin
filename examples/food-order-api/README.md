# food-order-api

FoodOrder 음식 주문 REST API — AWS Serverless Agent Plugin 활용 예시 샘플 코드.

## 구조

```
food-order-api/
├── template.yaml                # SAM 템플릿 (Lambda + HttpApi + DynamoDB)
├── samconfig.toml               # SAM 배포 설정
├── src/
│   └── order_handler/
│       ├── app.py               # Lambda 핸들러 (Powertools + APIGatewayHttpResolver)
│       └── requirements.txt     # Python 의존성
├── events/
│   ├── create_order.json        # POST /orders 테스트 이벤트
│   └── get_order.json           # GET /orders/{orderId} 테스트 이벤트
└── tests/
    ├── unit/test_handler.py     # 유닛 테스트
    └── integration/test_api_gateway.py  # 통합 테스트
```

## 사전 준비

- AWS CLI 구성 (`aws sts get-caller-identity`)
- SAM CLI 설치 (`sam --version`)
- Python 3.9+

## 빌드 및 배포

```bash
# 빌드
sam build

# 템플릿 검증
sam validate

# 로컬 테스트
sam local invoke OrderFunction -e events/create_order.json

# 배포
sam deploy --guided
```

## API 엔드포인트

배포 후 출력되는 `ApiEndpoint` URL을 사용합니다:

```bash
# 주문 생성
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/orders \
  -H "Content-Type: application/json" \
  -d '{"menu": "비빔밥", "quantity": 2, "customer": {"name": "홍길동", "phone": "010-1234-5678"}}'

# 주문 조회
curl https://<api-id>.execute-api.<region>.amazonaws.com/orders/<orderId>
```

## 테스트

```bash
pip install -r tests/requirements.txt
python -m pytest tests/unit -v

# 통합 테스트 (배포 후)
AWS_SAM_STACK_NAME="food-order-api" python -m pytest tests/integration -v
```

## 로그 조회

```bash
sam logs -n OrderFunction --stack-name "food-order-api" --tail
```

## 정리

```bash
sam delete --stack-name "food-order-api"
```
