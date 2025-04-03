
from uuid import uuid4
from app.services.chat_service_v2 import ChatService

class ChatSessionManager:
    def __init__(self):
        self.sessions = {}  
    
    def create_session(self):
        session_id = str(uuid4())
        self.sessions[session_id] = ChatService(session_id)
        return session_id
    
    def get_session(self, session_id):
        return self.sessions.get(session_id)
    
    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

chat_session_manager = ChatSessionManager()