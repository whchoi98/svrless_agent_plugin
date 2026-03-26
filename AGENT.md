# AWS Serverless Agent Plugin — 블로그 + 샘플 코드 프로젝트

## 역할

이 프로젝트는 AWS Serverless Agent Plugin 활용 가이드 블로그(`README.md`)와 FoodOrder SAM 샘플 코드(`examples/food-order-api/`)로 구성됩니다.

## 핵심 규칙

- IAM 정책에 와일드카드(`*`) 사용 금지. SAM 정책 템플릿(`DynamoDBCrudPolicy`) 사용
- DynamoDB 테이블은 반드시 `DeletionPolicy: Retain` + `UpdateReplacePolicy: Retain`
- 테이블명은 `TABLE_NAME` 환경 변수로 주입 (하드코딩 금지)
- Lambda 핸들러는 Powertools(`Logger`, `Tracer`, `APIGatewayHttpResolver`) 기반
- `examples/` 코드 변경 시 `README.md` 블로그 스니펫 동기화 필수
- 새 `examples/` 하위 디렉토리 생성 시 해당 디렉토리에 문서 파일 필수

## 기술 스택

- Runtime: Python 3.9 (Lambda, arm64)
- IaC: AWS SAM
- Framework: aws-lambda-powertools
- Database: DynamoDB (PAY_PER_REQUEST)
- API: API Gateway HTTP API (v2)

## 주요 명령어

```bash
cd examples/food-order-api
sam build
sam validate
sam local invoke OrderFunction -e events/create_order.json
sam deploy --guided
```
