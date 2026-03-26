# Architecture

## System Overview

FoodOrder — 음식 주문 REST API 서버리스 애플리케이션. AWS Serverless Agent Plugin으로 생성한 데모 프로젝트.

## Components

| Component | Service | Role |
|-----------|---------|------|
| **Order API** | Lambda + API Gateway HTTP API | POST /orders, GET /orders/{id} |
| **Data Store** | DynamoDB (FoodOrders 테이블) | 주문 데이터 저장 (PK: orderId) |
| **Observability** | X-Ray + CloudWatch | Powertools Logger/Tracer 기반 |

## Data Flow

```
Client → API Gateway (HTTP API v2) → Lambda (OrderFunction)
                                         ├── POST /orders → DynamoDB PutItem
                                         └── GET /orders/{id} → DynamoDB GetItem
```

## Infrastructure

- **IaC:** AWS SAM (`template.yaml`)
- **Runtime:** Python 3.9, arm64
- **Billing:** DynamoDB PAY_PER_REQUEST
- **Protection:** DeletionPolicy + UpdateReplacePolicy: Retain
- **Deployment:** `sam build` → `sam deploy --guided`
