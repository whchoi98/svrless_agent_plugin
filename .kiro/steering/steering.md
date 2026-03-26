# Project Steering

## Overview

svrless_agent_plugin — AWS Serverless Agent Plugin 활용 예시 블로그 + 샘플 코드 프로젝트.

## Project Structure

```
svrless_agent_plugin/
├── README.md                    # 블로그 본문 (GitHub 포스팅용)
├── AGENT.md                     # Kiro 에이전트 지시사항
├── examples/
│   └── food-order-api/          # SAM 프로젝트 샘플 코드
│       ├── template.yaml        # SAM 템플릿 (Lambda + HttpApi + DynamoDB)
│       ├── samconfig.toml       # SAM 배포 설정
│       ├── src/order_handler/   # Lambda 핸들러 (Python, Powertools)
│       ├── events/              # sam local invoke 테스트 이벤트
│       └── tests/               # 유닛/통합 테스트
├── docs/
│   ├── architecture.md          # 시스템 아키텍처
│   ├── decisions/               # ADR (Architecture Decision Records)
│   └── runbooks/                # 운영 절차서
├── .kiro/                       # Kiro 설정
│   ├── steering/                # 프로젝트 컨텍스트 및 규칙
│   └── skills/                  # 커스텀 스킬
└── tools/                       # 스크립트, 프롬프트
```

## Conventions

- Lambda 핸들러: Powertools `APIGatewayHttpResolver` 기반 라우팅
- IAM: SAM 정책 템플릿 사용 (`DynamoDBCrudPolicy`), 와일드카드 금지
- DynamoDB: `DeletionPolicy: Retain` + `UpdateReplacePolicy: Retain`
- 환경 변수: 테이블명은 `TABLE_NAME` 환경 변수로 주입
- 테스트 이벤트: HTTP API v2 형식 (`version: "2.0"`, `routeKey`)

## Documentation Sync Rules

- `examples/` 코드 변경 → `README.md` 블로그 스니펫 동기화 확인
- SAM template 변경 → `docs/architecture.md` 업데이트
- 새 `examples/` 하위 디렉토리 → 해당 디렉토리에 문서 파일 생성
- 아키텍처 결정 → `docs/decisions/ADR-NNN-title.md` 생성

## ADR Numbering

`docs/decisions/ADR-*.md`에서 가장 높은 번호를 찾아 +1.
형식: `ADR-NNN-concise-title.md`
