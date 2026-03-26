import json
import os

import boto3
import pytest
import requests

"""
AWS_SAM_STACK_NAME 환경 변수에 배포된 스택 이름을 설정하고 실행:
  AWS_SAM_STACK_NAME="food-order-api" python -m pytest tests/integration -v
"""


class TestApiGateway:

    @pytest.fixture()
    def api_gateway_url(self):
        """CloudFormation 스택 출력에서 API Gateway URL 조회"""
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")

        if stack_name is None:
            raise ValueError("AWS_SAM_STACK_NAME 환경 변수를 설정하세요")

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(f"스택 '{stack_name}'을 찾을 수 없습니다") from e

        stacks = response["Stacks"]
        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "ApiEndpoint"]

        if not api_outputs:
            raise KeyError(f"ApiEndpoint not found in stack {stack_name}")

        return api_outputs[0]["OutputValue"]

    def test_create_order(self, api_gateway_url):
        """POST /orders — 주문 생성"""
        response = requests.post(
            f"{api_gateway_url}/orders",
            json={"menu": "비빔밥", "quantity": 1, "customer": {"name": "테스트", "phone": "010-0000-0000"}},
        )

        assert response.status_code == 201
        body = response.json()
        assert "orderId" in body

    def test_get_order_not_found(self, api_gateway_url):
        """GET /orders/{id} — 존재하지 않는 주문 조회"""
        response = requests.get(f"{api_gateway_url}/orders/nonexistent-id")

        assert response.status_code == 404
