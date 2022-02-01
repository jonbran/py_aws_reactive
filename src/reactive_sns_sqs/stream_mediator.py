import copy
from typing import Callable, List
from xml.dom import ValidationErr

from reactive_sns_sqs.models.IAMUser import IAMUser

from .sns_publisher import SnsPublisher


class StreamMediator():

    _instance = None
    _sns_publishers: dict = {}
    _subscribers: dict = {}

    def __new__(cls):
        ''' Implemented as a singleton. '''
        if (cls._instance is None):
            cls._instance = super(StreamMediator, cls).__new__(cls)
        return cls._instance

    def register_topic(self, topic, iam:IAMUser=None, options: dict = None):
        """ Register an SNS publisher. Only the topic name is required and it needs match the AWS Topic.

        Args:
            topic (str): Name of the AWS topic you are registering.
            iam (IAMUser, optional): See IAMUser. Defaults to None.
            options (dict, optional): Listener options that you want to override. See listener_options for defaults. Defaults to None.
        """

        publisher = SnsPublisher(topic, iam=iam, options=options)
        self._sns_publishers[topic] = publisher
        self._subscribers[topic] = [publisher.publish]

    def publish(self, stream, message):
        """ Publish a messages to subscribers. 

        Args:
            stream (str): Stream name. e.g. topic
            message (Any): The message that will be published to the stream

        Raises:
            ValueError: Stream wasn't found
        """
        if (not stream in self._subscribers):
            raise ValueError(f"Stream {stream} doesn't exist")
        stream = self._subscribers[stream]

        subscribers = copy.copy(stream)
        for publish in subscribers:
            publish(message)

    def subscribe(self, stream_name, publisher):
        """ Subscribes the publisher to a stream

        Args:
            stream_name (str): name to identify the stream
            publisher (Callable|lambda): method that will handle published messages
        """
        if (stream_name in self._subscribers):
            self._subscribers[stream_name].append(publisher)
        else:
            self._subscribers[stream_name] = [publisher]

    def merge_topics(self, stream_name, topic_names: List):
        """ Merge multiple topics into a single stream. The topic stream must already exist.
        

        Args:
            stream_name (str): A name that will be used to publish to the new stream.
            topic_names (List): List of topic names. hint: the name you passed into register_topic

        Raises:
            ValidationErr: Topic hasn't been registered.
        """
        for name in topic_names:
            if (name in self._sns_publishers):
                publisher = self._sns_publishers[name]
                self.subscribe(stream_name, publisher.publish)
            else:
                raise ValidationErr(
                    f"The topic {name} hasn't been registered. Please register the stream first.")
