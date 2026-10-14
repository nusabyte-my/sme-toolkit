"""Agent Communication Protocol - Standardized communication between agents"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages between agents"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    STATUS_UPDATE = "status_update"


class AgentMessage:
    """Standardized message structure for agent-to-agent communication"""
    
    def __init__(
        self,
        message_type: MessageType,
        sender: str,
        recipient: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.message_id = str(uuid.uuid4())
        self.message_type = message_type
        self.sender = sender
        self.recipient = recipient  # None means broadcast to all agents
        self.content = content or {}
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary"""
        return cls(
            message_type=MessageType(data["message_type"]),
            sender=data["sender"],
            recipient=data.get("recipient"),
            content=data.get("content", {}),
            correlation_id=data.get("correlation_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )


class SharedContext:
    """Shared context object that all agents can access"""
    
    def __init__(self, business_profile_id: str):
        self.business_profile_id = business_profile_id
        self.context_id = str(uuid.uuid4())
        self.data: Dict[str, Any] = {}
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.message_history: List[AgentMessage] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set(self, key: str, value: Any, agent_name: Optional[str] = None) -> None:
        """Set a value in the shared context"""
        self.data[key] = value
        self.updated_at = datetime.utcnow()
        logger.debug(f"Context updated by {agent_name or 'system'}: {key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the shared context"""
        return self.data.get(key, default)
    
    def update_agent_state(self, agent_name: str, state: Dict[str, Any]) -> None:
        """Update an agent's state in the context"""
        self.agent_states[agent_name] = {
            **self.agent_states.get(agent_name, {}),
            **state,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.updated_at = datetime.utcnow()
    
    def get_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """Get an agent's state from the context"""
        return self.agent_states.get(agent_name, {})
    
    def add_message(self, message: AgentMessage) -> None:
        """Add a message to the history"""
        self.message_history.append(message)
        self.updated_at = datetime.utcnow()
    
    def get_messages(
        self,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[AgentMessage]:
        """Get filtered messages from history"""
        messages = self.message_history
        
        if sender:
            messages = [m for m in messages if m.sender == sender]
        if recipient:
            messages = [m for m in messages if m.recipient == recipient or m.recipient is None]
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        return messages[-limit:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "context_id": self.context_id,
            "business_profile_id": self.business_profile_id,
            "data": self.data,
            "agent_states": self.agent_states,
            "message_count": len(self.message_history),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class MessageQueue:
    """Message queue for async operations"""
    
    def __init__(self):
        self.queue: List[AgentMessage] = []
        self.subscribers: Dict[str, List[str]] = {}  # agent_name -> list of message_types
    
    def subscribe(self, agent_name: str, message_types: List[MessageType]) -> None:
        """Subscribe an agent to specific message types"""
        self.subscribers[agent_name] = [mt.value for mt in message_types]
        logger.debug(f"Agent {agent_name} subscribed to {[mt.value for mt in message_types]}")
    
    def publish(self, message: AgentMessage) -> None:
        """Publish a message to the queue"""
        self.queue.append(message)
        logger.debug(f"Message published: {message.message_type.value} from {message.sender}")
    
    def get_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get messages for a specific agent"""
        subscribed_types = self.subscribers.get(agent_name, [])
        
        messages = [
            msg for msg in self.queue
            if msg.recipient == agent_name or msg.recipient is None
        ]
        
        if subscribed_types:
            messages = [msg for msg in messages if msg.message_type.value in subscribed_types]
        
        return messages
    
    def clear(self) -> None:
        """Clear the message queue"""
        self.queue.clear()
        logger.debug("Message queue cleared")


class DataTransformer:
    """Transform data between agents"""
    
    @staticmethod
    def transform_for_goal_advisor(context: SharedContext) -> Dict[str, Any]:
        """Transform context data for Goal Advisor"""
        return {
            "business_context": {
                "company_name": context.get("company_name"),
                "industry": context.get("industry"),
                "business_stage": context.get("business_stage"),
                "team_size": context.get("team_size"),
                "revenue": context.get("revenue")
            },
            "bmc_data": context.get("bmc_data", {}),
            "metrics": context.get("metrics", {}),
            "resources": context.get("resources", {}),
            "business_profile_id": context.business_profile_id
        }
    
    @staticmethod
    def transform_for_growth_advisor(context: SharedContext) -> Dict[str, Any]:
        """Transform context data for Growth Advisor"""
        return {
            "business_context": {
                "company_name": context.get("company_name"),
                "industry": context.get("industry"),
                "business_stage": context.get("business_stage")
            },
            "bmc_data": context.get("bmc_data", {}),
            "market_data": context.get("market_data", {}),
            "financial_projections": context.get("financial_projections", {}),
            "growth_metrics": context.get("growth_metrics", {}),
            "competitive_landscape": context.get("competitive_landscape", {}),
            "business_profile_id": context.business_profile_id
        }
    
    @staticmethod
    def transform_for_costing_advisor(context: SharedContext) -> Dict[str, Any]:
        """Transform context data for Costing Advisor"""
        return {
            "financial_data": context.get("financial_data", {}),
            "cost_breakdown": context.get("cost_breakdown", {}),
            "bmc_data": context.get("bmc_data", {}),
            "operational_metrics": context.get("operational_metrics", {}),
            "business_profile_id": context.business_profile_id
        }
    
    @staticmethod
    def transform_for_suggestion_advisor(context: SharedContext) -> Dict[str, Any]:
        """Transform context data for Suggestion Advisor"""
        return {
            "business_context": {
                "company_name": context.get("company_name"),
                "industry": context.get("industry"),
                "business_stage": context.get("business_stage")
            },
            "market_data": context.get("market_data", {}),
            "bmc_data": context.get("bmc_data", {}),
            "capabilities": context.get("capabilities", {}),
            "industry_analysis": context.get("industry_analysis", {}),
            "business_profile_id": context.business_profile_id
        }
    
    @staticmethod
    def merge_agent_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge results from multiple agents"""
        merged = {}
        
        for result in results:
            if isinstance(result, dict) and "success" in result:
                agent_name = result.get("agent_name", "unknown")
                merged[agent_name] = result
        
        return merged


class CommunicationProtocol:
    """Main communication protocol for agent coordination"""
    
    def __init__(self):
        self.message_queue = MessageQueue()
        self.contexts: Dict[str, SharedContext] = {}  # business_profile_id -> context
    
    def create_context(self, business_profile_id: str) -> SharedContext:
        """Create a new shared context"""
        context = SharedContext(business_profile_id)
        self.contexts[business_profile_id] = context
        logger.info(f"Created context for business profile {business_profile_id}")
        return context
    
    def get_context(self, business_profile_id: str) -> Optional[SharedContext]:
        """Get an existing context"""
        return self.contexts.get(business_profile_id)
    
    def send_message(
        self,
        sender: str,
        recipient: Optional[str],
        message_type: MessageType,
        content: Dict[str, Any],
        business_profile_id: str
    ) -> AgentMessage:
        """Send a message between agents"""
        context = self.get_context(business_profile_id)
        if not context:
            raise ValueError(f"No context found for business profile {business_profile_id}")
        
        message = AgentMessage(
            message_type=message_type,
            sender=sender,
            recipient=recipient,
            content=content
        )
        
        context.add_message(message)
        self.message_queue.publish(message)
        
        return message
    
    def broadcast_message(
        self,
        sender: str,
        message_type: MessageType,
        content: Dict[str, Any],
        business_profile_id: str
    ) -> AgentMessage:
        """Broadcast a message to all agents"""
        return self.send_message(
            sender=sender,
            recipient=None,
            message_type=message_type,
            content=content,
            business_profile_id=business_profile_id
        )
    
    def get_agent_messages(
        self,
        agent_name: str,
        business_profile_id: str
    ) -> List[AgentMessage]:
        """Get messages for a specific agent"""
        context = self.get_context(business_profile_id)
        if not context:
            return []
        
        return context.get_messages(recipient=agent_name)
    
    def cleanup_context(self, business_profile_id: str) -> None:
        """Clean up a context when no longer needed"""
        if business_profile_id in self.contexts:
            del self.contexts[business_profile_id]
            logger.info(f"Cleaned up context for business profile {business_profile_id}")


class AgentCommunicator:
    """Agent communicator for message passing and history tracking"""

    def __init__(self):
        self._messages: List[Dict[str, Any]] = []
        self._queues: Dict[str, List[Dict[str, Any]]] = {}

    def create_message(self, sender: str, receiver: str, message_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standardized message dictionary"""
        return {
            "id": str(uuid.uuid4()),
            "sender": sender,
            "receiver": receiver,
            "type": message_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }

    def send_message(self, message: Dict[str, Any]) -> bool:
        """Send a message to a receiver's queue"""
        self._messages.append(message)
        receiver = message.get("receiver")
        if receiver:
            if receiver not in self._queues:
                self._queues[receiver] = []
            self._queues[receiver].append(message)
        return True

    def receive_message(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Receive the next message for an agent"""
        queue = self._queues.get(agent_id, [])
        if queue:
            return queue.pop(0)
        return None

    def broadcast_message(self, message: Dict[str, Any], target_agents: List[str]) -> bool:
        """Broadcast a message to a list of target agents"""
        for agent in target_agents:
            copy_msg = dict(message)
            copy_msg["receiver"] = agent
            self.send_message(copy_msg)
        return True

    def get_message_history(self, sender: Optional[str] = None, receiver: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get message history filtered by sender and/or receiver"""
        history = self._messages
        if sender:
            history = [m for m in history if m.get("sender") == sender]
        if receiver:
            history = [m for m in history if m.get("receiver") == receiver]
        return history

