import time
from multiprocessing import Value
from multiprocessing.sharedctypes import Synchronized
from typing import Union

import boto3
from botocore.session import Session as s
from rx import Observable, create
from rx.core.typing import Observer

from reactive_sns_sqs.models import ListenerOptions
from reactive_sns_sqs.models.IAMUser import IAMUser


class SqsListener():
    
    _client: boto3.client = None
    _session: boto3.Session = None
    _iam: IAMUser = None
    _options: ListenerOptions = ListenerOptions()
    _running: Union[Value, bool]
    
    @property
    def running(self):
        return self._running
    
    @running.setter
    def running(self, state):
        self._running = state
    
    
    def __init__(self, queue_name: str = None, iam: IAMUser =  None, options: ListenerOptions = None) -> None:

        if(options): self._options = options
        if(queue_name): self._options.queue_name = queue_name
        if(iam): self._iam = iam
        
        self._validate_options()
        self._initialize_session()
        
    def listen(self) -> Observable:
        me = self
        return create(self._listen);
    
    def _listen(self, observer, rando=None):
        # Reset the client
        self._client = None
        self._get_client()
        # Now get the queue url
        self._get_queue_url()
        
        while True:
            if (not self._is_running()):
                observer.on_completed()
                break
            
            messages = None
            client = self._client or self._get_client()
            try:
                messages = client.receive_message(
                QueueUrl=self._options.queue_url,
                MessageAttributeNames=self._options.message_attribute_names,
                AttributeNames=self._options.attribute_names,
                WaitTimeSeconds=self._options.wait_time,
                MaxNumberOfMessages=self._options.max_number_of_messages
            )
            except Exception as ex:
                observer.on_error(ex)
                
            if 'Messages' in messages:
                for message in messages['Messages']:
                    receipt_handle = message['ReceiptHandle']
                    observer.on_next(
                        (message, lambda: client.delete_message(
                            QueueUrl=self._options.queue_url,
                                    ReceiptHandle=receipt_handle
                        )))
            else:
                time.sleep(self._options.poll_interval)
            
            
    def _is_running(self) -> bool:
        if(isinstance(self._running, Synchronized)):
            return bool(self._running.value)
        else:
            return self._running
        
    def _validate_options(self):
        # We can't do much if there isn't a queue to work with.
        if(not self._options.queue_name):
            raise ValueError('queue_name is required. Please set the queue name in the options or pass it in as a parameter.')
            

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
            
    def _get_client(self) -> boto3.client:
        ''' Create an SQS client '''
        if (self._client):
            # TODO: Check if client is valid and active.
            return self._client
        
        # Check if a ca_bundle is set by boto3
        a = s().get_config_variable('ca_bundle')
        # Check for an ca_bundle environment variable.
        ca_bundle = self._options.ca_bundle
        # If boto3 doesn't have a ca_bundle but there is an environment variable
        # set the ca_bundle path. If both == None just set verify to True
        verify = ((a == None and ca_bundle != None) and ca_bundle or True)
        
        client = self._session.client('sqs', 
            region_name=self._options.region_name,
            use_ssl=True,
            verify=verify
        )
        self._client = client
        if (not self._queue_exists()): 
            raise ValueError(f'The Queue {self._options.queue_name} does not exist')
        
        return client
    
    def _queue_exists(self):
        ''' Gets a list of available queues to verify the queue were looking at exists. '''
        queues = self._client.list_queues(QueueNamePrefix=self._options.queue_name)
        if 'QueueUrls' in queues:
            for q in queues['QueueUrls']:
                name = q.split('/')[-1]
                if name == self._options.queue_name:
                    return True
                
    def _get_queue_url(self): 
        ''' Uses the boto3 client to find and set the QueueUrl '''
        # Is the queue url already set?
        if (self._options.queue_url):
            return
            
        queue = None
        if (not self._options.queue_url): 
            queue = self._client.get_queue_url(
                QueueName=self._options.queue_name
            )
        
        if (not queue):
            raise Exception(f"The Queue: {self._options.queue_name} doesn't have a QueueUrl")
        
        self._options.queue_url = queue['QueueUrl']
        
    
    