from typing import Any, Optional, List
from pydantic import BaseModel, Field

class MessageAttributes(BaseModel):
    DataType: str
    StringValue: Optional[str]
    BinaryValue: Optional[str]

class SnsMessage(BaseModel):
    TopicArn: Optional[str]
    TargetArn: Optional[str]
    PhoneNumber: Optional[str]
    Message: Any
    Subject: Optional[str]
    MessageStructure: str
    MessageAttributes: MessageAttributes
    MessageDeduplicationId: Optional[str]
    MessageGroupId: Optional[str]

class SnsMessageBody(BaseModel):
    default: Any


class SnsHttpResponse(BaseModel):
    MessageId: Optional[str]
    SequenceNumber: Optional[str]


class Topic(BaseModel):
    TopicArn: str


class HTTPHeaders(BaseModel):
    x_amzn_requestid: str = Field(..., alias='x-amzn-requestid')
    content_type: str = Field(..., alias='content-type')
    content_length: str = Field(..., alias='content-length')
    date: str


class ResponseMetadata(BaseModel):
    RequestId: str
    HTTPStatusCode: int
    HTTPHeaders: HTTPHeaders
    RetryAttempts: int


class TopicList(BaseModel):
    Topics: List[Topic]
    ResponseMetadata: ResponseMetadata