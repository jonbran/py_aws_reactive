import asyncio
from gettext import find
import json
from msilib.schema import Error
import uuid
from typing import Any

import boto3
import boto3.session
from botocore.session import Session as s
from pydantic import BaseModel

from .models import IAMUser
from .models import SnsHttpResponse, SnsMessage, SnsMessageBody


class SnsPublisher:

    # added to show class level variables
    _arn: str
    _client: boto3.client = None
    _iam: IAMUser
    _options: dict = { 'region_name': 'us-west-2' }
    _session: Any = None
    _topic: str
    

    def __init__(self, topic: str, iam: IAMUser=None, options=None) -> None:
        self._iam = iam
        self._topic = topic
        if (options != None):
            self._options.update(options)
        self._initialize_session()
        self._get_client()

    def publish(self, payload) -> SnsHttpResponse:
        message = None
        self._set_arn()
        try:
            #if (type(payload) is not dict):
            if (type(payload) is BaseModel):
                message = SnsMessageBody(default=payload.json())
            else:
                message = SnsMessageBody(default=json.dumps(payload))
        except Exception:
            print ('sns Message has invalid format. sns_publisher.publish')
            raise

        # Select the correct publishing method.
        if (self._arn[-4:] == 'fifo'):
            response = self._publish_fifo(message, self._arn)
        else:
            response = self._publish_standard(message, self._arn)
        return response

    def _publish_fifo(self, message: SnsMessage, arn: str) -> SnsHttpResponse:
        ''' Publish a message to a fifo Topic '''
        duplicationId = uuid.uuid4()
        messageGroupId = uuid.uuid4()
        try:
            snsResponse = self._client.publish(
                TopicArn=arn,
                MessageGroupId=str(messageGroupId),
                MessageDeduplicationId=str(duplicationId),
                Message=message.json(),
                MessageStructure='json'
            )
            response = SnsHttpResponse(
                MessageId=snsResponse['MessageId'], SequenceNumber=snsResponse['SequenceNumber'])
        except Exception as ex:
            print(ex)
        return response

    def _publish_standard(self, message: SnsMessage, arn: str) -> SnsHttpResponse:
        ''' Publish a message to a standard (not fifo) Topic '''
        response = None
        try:
            a = self._client.publish(
                TopicArn=arn,
                Message=message.json(),
                MessageStructure='json'
            )
            response = SnsHttpResponse(
                **a)
        except Exception as ex:
            print(ex)
        return response

    # Create the boto3 session. If and IAM was passed in
    # it will use those credentials.
    def _initialize_session(self):
        if (self._iam):
            # Set the session access_key and secert key
            self._session = boto3.Session(
                aws_access_key_id=self._iam.access_key,
                aws_secret_access_key=self._iam.secret_key
            )
        else:
            self._session = boto3.session()

    # Creates the boto3 client.
    def _get_client(self):
        
        if (hasattr(self, '_client')):
            if (self._client): return self._client

        region = self._options['region_name']
        a = s().get_config_variable('ca_bundle')
        ca_bundle = (
            'ca_bundle' in self._options) and self._options['ca_bundle'] or None
        verify = ((a == None and ca_bundle != None) and ca_bundle or True)
        self._client = self._session.client('sns',
                                            region_name=region,
                                            use_ssl=True,
                                            verify=verify
                                            )
    def _set_arn(self):
        if (hasattr(self, '_arn') and self._arn):
            return
        if('topic_arn' in self._options and self._options['topic_arn']):
            self._arn = self._options['topic_arn']
        else:
            self._arn = self._get_arn(self._topic)
        if (not self._arn):
            raise Error('Unable to find Topic arn')

    def _get_arn(self, name) -> str:
        self._get_client()
        topics = self._client.list_topics()
        topics = topics['Topics']
        arn = None
        x = len(name) * -1
        for topic_arn in topics:
            if(topic_arn['TopicArn'][x:] == name):
                arn = topic_arn['TopicArn']
                break;
    
        return arn
        