import json
import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture()
def create_order_event():
    """POST /orders HTTP API v2 이벤트"""
    return {
        "version": "2.0",
        "routeKey": "POST /orders",
        "rawPath": "/orders",
        "body": json.dumps({
            "menu": "비빔밥",
            "quantity": 2,
            "customer": {"name": "홍길동", "phone": "010-1234-5678"},
        }),
        "isBase64Encoded": False,
        "requestContext": {
            "http": {"method": "POST", "path": "/orders"},
            "requestId": "test-request-id",
        },
    }


@pytest.fixture()
def get_order_event():
    """GET /orders/{orderId} HTTP API v2 이벤트"""
    return {
        "version": "2.0",
        "routeKey": "GET /orders/{orderId}",
        "rawPath": "/orders/test-order-123",
        "pathParameters": {"orderId": "test-order-123"},
        "isBase64Encoded": False,
        "requestContext": {
            "http": {"method": "GET", "path": "/orders/test-order-123"},
            "requestId": "test-request-id",
        },
    }


@patch.dict(os.environ, {"TABLE_NAME": "FoodOrders", "POWERTOOLS_SERVICE_NAME": "test"})
@patch("boto3.resource")
def test_create_order(mock_boto3, create_order_event):
    mock_table = MagicMock()
    mock_boto3.return_value.Table.return_value = mock_table

    from src.order_handler import app

    ret = app.lambda_handler(create_order_event, MagicMock())

    assert ret["statusCode"] == 201
    body = json.loads(ret["body"])
    assert "orderId" in body
    assert body["status"] == "CREATED"
    mock_table.put_item.assert_called_once()


@patch.dict(os.environ, {"TABLE_NAME": "FoodOrders", "POWERTOOLS_SERVICE_NAME": "test"})
@patch("boto3.resource")
def test_get_order_not_found(mock_boto3, get_order_event):
    mock_table = MagicMock()
    mock_table.get_item.return_value = {}
    mock_boto3.return_value.Table.return_value = mock_table

    from src.order_handler import app

    ret = app.lambda_handler(get_order_event, MagicMock())

    assert ret["statusCode"] == 404
