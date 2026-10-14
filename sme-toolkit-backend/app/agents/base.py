from abc import ABC, abstractmethod
from typing import Any, Dict, TypedDict, Optional


class BaseAgentState(TypedDict):
    """Base state for all agents"""
    error: Optional[str]


class BaseAgent(ABC):
    """Base class for all LangGraph agents"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name identifier"""
        pass

    @abstractmethod
    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with given input"""
        pass

    @abstractmethod
    def get_actions(self) -> list:
        """Return list of supported actions"""
        pass
