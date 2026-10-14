"""
Circuit breaker pattern for external service resilience
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any, Optional, Dict
import asyncio
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when circuit is open"""
    pass


class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3,
        success_threshold: int = 2,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        
        self._lock = asyncio.Lock()
    
    def _should_attempt_recovery(self) -> bool:
        if not self.last_failure_time:
            return True
        elapsed = datetime.utcnow() - self.last_failure_time
        return elapsed.total_seconds() >= self.recovery_timeout
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_recovery():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    self.success_count = 0
                    logger.info(f"Circuit {self.name} entering half-open state")
                else:
                    raise CircuitOpenError(
                        f"Circuit {self.name} is open. Retry after {self.recovery_timeout}s"
                    )
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        async with self._lock:
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                self.half_open_calls += 1
                
                if self.success_count >= self.success_threshold:
                    logger.info(f"Circuit {self.name} recovered, closing")
                    self.state = CircuitState.CLOSED
                    self.success_count = 0
            else:
                self.success_count += 1
    
    async def _on_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.success_count = 0
            self.last_failure_time = datetime.utcnow()
            
            if self.state == CircuitState.HALF_OPEN:
                logger.warning(f"Circuit {self.name} failed in half-open, reopening")
                self.state = CircuitState.OPEN
                self.half_open_calls = 0
                
            elif self.failure_count >= self.failure_threshold:
                logger.error(
                    f"Circuit {self.name} threshold reached ({self.failure_count}), opening"
                )
                self.state = CircuitState.OPEN
    
    def get_state(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }
    
    async def reset(self):
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.half_open_calls = 0
            logger.info(f"Circuit {self.name} manually reset")


class CircuitBreakerRegistry:
    """Global registry for circuit breakers"""
    
    _instance: Optional["CircuitBreakerRegistry"] = None
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
    
    @classmethod
    def get_instance(cls) -> "CircuitBreakerRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get(
        self, 
        name: str, 
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        **kwargs
    ) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                **kwargs
            )
        return self._breakers[name]
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        return {name: breaker.get_state() for name, breaker in self._breakers.items()}
    
    async def reset_all(self):
        for breaker in self._breakers.values():
            await breaker.reset()


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    return CircuitBreakerRegistry.get_instance().get(name, **kwargs)


PROVIDER_CIRCUIT_CONFIGS = {
    "gemini": {"failure_threshold": 3, "recovery_timeout": 30},
    "groq": {"failure_threshold": 5, "recovery_timeout": 60},
    "mistral": {"failure_threshold": 5, "recovery_timeout": 60},
    "deepseek": {"failure_threshold": 5, "recovery_timeout": 60},
    "flux": {"failure_threshold": 3, "recovery_timeout": 120},
    "stability": {"failure_threshold": 3, "recovery_timeout": 120},
    "veo": {"failure_threshold": 2, "recovery_timeout": 180},
    "kling": {"failure_threshold": 2, "recovery_timeout": 180},
}


def get_provider_circuit_breaker(provider_name: str) -> CircuitBreaker:
    config = PROVIDER_CIRCUIT_CONFIGS.get(provider_name, {})
    return get_circuit_breaker(f"provider_{provider_name}", **config)
