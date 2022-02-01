from typing import List, Optional
from pydantic import BaseModel

class ListenerOptions(BaseModel):
    queue_name: Optional[str]
    poll_interval: int = 1 # How often should we check the queue for messages.
    visibility_timeout: str = '30'
    queue_url: Optional[str]
    message_attribute_names: List[str] = ['']
    attribute_names: List[str] = ['All']
    force_delete: bool = False
    endpoint_name: Optional[str]
    wait_time: int = 0 # How long should we wait for a message to arrive.
    max_number_of_messages: int = 1
    region_name: str = 'us-west-2'
    ca_bundle: Optional[str]