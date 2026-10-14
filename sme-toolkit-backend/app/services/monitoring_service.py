"""
Monitoring and logging service
"""
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
from collections import defaultdict, deque


class MonitoringService:
    """
    Service for monitoring application performance and logging metrics
    """
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.logger = self._setup_logger()
        self.max_metrics_size = 1000  # Keep last 1000 metrics
    
    def _setup_logger(self) -> logging.Logger:
        """
        Setup structured logger
        """
        logger = logging.getLogger("sme_toolkit")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler("sme_toolkit.log")
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def log_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Log a metric value
        """
        timestamp = datetime.utcnow().isoformat()
        metric = {
            "name": name,
            "value": value,
            "timestamp": timestamp,
            "tags": tags or {}
        }
        
        self.metrics[name].append(metric)
        
        # Keep only recent metrics
        if len(self.metrics[name]) > self.max_metrics_size:
            self.metrics[name] = self.metrics[name][-self.max_metrics_size:]
        
        self.logger.info(f"Metric: {name}={value}", extra={"metric": metric})
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter
        """
        self.counters[name] += value
        self.logger.info(f"Counter: {name}+={value}", extra={"counter": name, "value": value, "tags": tags})
    
    def get_metric_stats(self, name: str) -> Dict[str, Any]:
        """
        Get statistics for a metric
        """
        if name not in self.metrics or not self.metrics[name]:
            return {}
        
        values = [m["value"] for m in self.metrics[name]]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None
        }
    
    def get_counter(self, name: str) -> int:
        """
        Get counter value
        """
        return self.counters[name]
    
    def reset_counter(self, name: str) -> None:
        """
        Reset a counter
        """
        self.counters[name] = 0
        self.logger.info(f"Counter reset: {name}")
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error with context
        """
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {}
        }
        
        self.logger.error(
            f"Error: {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra={"error": error_info}
        )
    
    def log_warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning with context
        """
        self.logger.warning(
            f"Warning: {message}",
            extra={"warning": {"message": message, "context": context or {}}}
        )
    
    def log_info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an info message with context
        """
        self.logger.info(
            f"Info: {message}",
            extra={"info": {"message": message, "context": context or {}}}
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall health status
        """
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_count": len(self.metrics),
            "counters_count": len(self.counters),
            "recent_errors": self._get_recent_errors()
        }
    
    def _get_recent_errors(self) -> list:
        """
        Get recent errors from logs
        """
        # In a real implementation, this would query log files
        # For now, return empty list
        return []


def monitor_performance(metric_name: str):
    """
    Decorator to monitor function performance
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            monitoring = get_monitoring_service()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                monitoring.log_metric(
                    f"{metric_name}.execution_time",
                    execution_time,
                    tags={"function": func.__name__}
                )
                monitoring.increment_counter(
                    f"{metric_name}.calls",
                    tags={"function": func.__name__}
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                monitoring.log_metric(
                    f"{metric_name}.execution_time",
                    execution_time,
                    tags={"function": func.__name__, "status": "error"}
                )
                monitoring.increment_counter(
                    f"{metric_name}.errors",
                    tags={"function": func.__name__}
                )
                monitoring.log_error(e, context={"function": func.__name__})
                raise
        
        return wrapper
    return decorator


# Global monitoring service instance
_monitoring_service = MonitoringService()


def get_monitoring_service() -> MonitoringService:
    """
    Get the global monitoring service instance
    """
    return _monitoring_service
