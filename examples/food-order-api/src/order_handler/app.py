import json
import os
import uuid

import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()
app = APIGatewayHttpResolver()

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("TABLE_NAME", "FoodOrders"))


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
    logger.info("Order created", extra={"order_id": order_id})

    return {"statusCode": 201, "body": {"orderId": order_id, "status": "CREATED"}}


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
