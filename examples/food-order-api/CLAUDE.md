# food-order-api Module

## Role
FoodOrder 음식 주문 REST API SAM 프로젝트. 블로그 시나리오 1~4의 실제 구현체.

## Key Files
- `template.yaml` — SAM 템플릿 (Lambda, HttpApi, DynamoDB)
- `src/order_handler/app.py` — Lambda 핸들러 (Powertools + APIGatewayHttpResolver)
- `events/create_order.json` — POST /orders 테스트 이벤트 (HTTP API v2 형식)
- `events/get_order.json` — GET /orders/{orderId} 테스트 이벤트

## Rules
- 테이블명은 `TABLE_NAME` 환경 변수로 주입 (하드코딩 금지)
- IAM 정책은 SAM 정책 템플릿 사용 (`DynamoDBCrudPolicy`)
- DynamoDB 테이블은 `DeletionPolicy: Retain` + `UpdateReplacePolicy: Retain`
- 테스트 이벤트는 HTTP API v2 형식 (`version: "2.0"`, `routeKey`)
- 코드 변경 시 `../../README.md`의 블로그 스니펫도 동기화 필요
