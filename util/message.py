import enum  
from typing import Any
from util.types import MessageType

class Message:
    message_id = 0
    
    def __init__(self, type:MessageType, content:Any=None):
        self.type = type
        self.content = content
        self.id = Message.message_id
        Message.message_id += 1
    
    def __lt__(self, other):
        """ To allow the message to be sorted in the priority queue"""
        return self.id < other.id
    
    def __str__(self):
        return f"Message {self.id}: {self.type} - {self.content}"