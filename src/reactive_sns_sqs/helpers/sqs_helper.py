from xmlrpc.client import Boolean
import boto3

class SqsHelper():
    
    def _queue_exists(self, client: boto3.client, queue_name:str) -> Boolean:
        ''' Gets a list of available queues to verify the queue were looking at exists. '''
        queues = client.list_queues(QueueNamePrefix=queue_name)
        if 'QueueUrls' in queues:
            for q in queues['QueueUrls']:
                name = q.split('/')[-1]
                if name == self._options.queue_name:
                    return True
                
    def _get_queue_url(self, client: boto3.client, queue_name: str) -> str: 
        ''' Uses the boto3 client to find and set the QueueUrl '''
        
        queue = None
        queue = client.get_queue_url(
                QueueName=queue_name
            )
        
        if (not queue):
            raise Exception(f"The Queue: {queue_name} doesn't have a QueueUrl")
        
        return queue['QueueUrl']