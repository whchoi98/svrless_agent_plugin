# svrless_agent_plugin

AWS Serverless Agent Plugin 활용 예시 블로그 + 샘플 코드 프로젝트.

## Project Structure

```
svrless_agent_plugin/
├── README.md                    # 블로그 본문 (GitHub 포스팅용)
├── examples/
│   └── food-order-api/          # SAM 프로젝트 샘플 코드
│       ├── template.yaml        # SAM 템플릿 (Lambda + HttpApi + DynamoDB)
│       ├── src/order_handler/   # Lambda 핸들러 (Python, Powertools)
│       ├── events/              # sam local invoke 테스트 이벤트
│       └── tests/               # 유닛/통합 테스트
└── docs/superpowers/            # 설계 스펙 및 구현 플랜
```

## Tech Stack

- **Runtime:** Python 3.9 (Lambda)
- **IaC:** AWS SAM
- **Framework:** aws-lambda-powertools (Logger, Tracer, APIGatewayHttpResolver)
- **Database:** DynamoDB (PAY_PER_REQUEST, arm64)
- **API:** API Gateway HTTP API (v2)

## Key Commands

```bash
# SAM 프로젝트 빌드
cd examples/food-order-api
sam build

# 템플릿 검증
sam validate

# 로컬 테스트
sam local invoke OrderFunction -e events/create_order.json

# 배포
sam deploy --guided
```

## Conventions

- Lambda 핸들러: Powertools `APIGatewayHttpResolver` 기반 라우팅
- IAM: SAM 정책 템플릿 사용 (`DynamoDBCrudPolicy`), 와일드카드 금지
- DynamoDB: `DeletionPolicy: Retain` + `UpdateReplacePolicy: Retain`
- 환경 변수: 테이블명은 `TABLE_NAME` 환경 변수로 주입
