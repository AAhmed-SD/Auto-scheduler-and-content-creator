import psutil
import time
from typing import Dict, Any, Optional, List
from .logging import get_logger, get_audit_logger
import threading
from datetime import datetime
import json
from pathlib import Path
from collections import defaultdict

logger = get_logger(__name__)
audit_logger = get_audit_logger()

class PerformanceMonitor:
    """Monitor system and application performance"""
    
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self.error_metrics = defaultdict(list)
        
    def start(self):
        """Start the monitoring thread"""
        if self._monitor_thread is None:
            self._stop_event.clear()
            self._monitor_thread = threading.Thread(target=self._monitor_loop)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
            logger.info("Performance monitoring started")
            
    def stop(self):
        """Stop the monitoring thread"""
        if self._monitor_thread is not None:
            self._stop_event.set()
            self._monitor_thread.join()
            self._monitor_thread = None
            logger.info("Performance monitoring stopped")
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self._stop_event.is_set():
            try:
                metrics = self._collect_metrics()
                self._save_metrics(metrics)
                self._check_thresholds(metrics)
                self._analyze_error_metrics()
            except Exception as e:
                logger.exception("Error in monitoring loop")
            time.sleep(self.interval)
            
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect system and application metrics"""
        process = psutil.Process()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(),
                "count": psutil.cpu_count(),
                "process_percent": process.cpu_percent()
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "process_memory": process.memory_info().rss
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "network": {
                "connections": len(psutil.net_connections()),
                "io_counters": psutil.net_io_counters()._asdict()
            },
            "errors": {
                "total": sum(len(errors) for errors in self.error_metrics.values()),
                "by_type": {error_type: len(errors) for error_type, errors in self.error_metrics.items()}
            }
        }
        
    def _save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to file"""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        metrics_file = self.metrics_dir / f"metrics_{date_str}.json"
        
        try:
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    existing_metrics = json.load(f)
            else:
                existing_metrics = []
                
            existing_metrics.append(metrics)
            
            with open(metrics_file, 'w') as f:
                json.dump(existing_metrics, f, indent=2)
        except Exception as e:
            logger.exception("Error saving metrics")
            
    def _check_thresholds(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and alert if necessary"""
        thresholds = {
            "cpu_percent": 80,
            "memory_percent": 80,
            "disk_percent": 80,
            "error_rate": 100  # errors per hour
        }
        
        if metrics["cpu"]["percent"] > thresholds["cpu_percent"]:
            logger.warning(
                "High CPU usage",
                extra={
                    "current": metrics["cpu"]["percent"],
                    "threshold": thresholds["cpu_percent"]
                }
            )
            
        if metrics["memory"]["percent"] > thresholds["memory_percent"]:
            logger.warning(
                "High memory usage",
                extra={
                    "current": metrics["memory"]["percent"],
                    "threshold": thresholds["memory_percent"]
                }
            )
            
        if metrics["disk"]["percent"] > thresholds["disk_percent"]:
            logger.warning(
                "High disk usage",
                extra={
                    "current": metrics["disk"]["percent"],
                    "threshold": thresholds["disk_percent"]
                }
            )
            
        # Check error rates
        for error_type, errors in self.error_metrics.items():
            recent_errors = [
                error for error in errors
                if (datetime.utcnow() - error["timestamp"]).total_seconds() < 3600
            ]
            if len(recent_errors) > thresholds["error_rate"]:
                logger.warning(
                    f"High error rate for {error_type}",
                    extra={
                        "current": len(recent_errors),
                        "threshold": thresholds["error_rate"]
                    }
                )
                
    def _analyze_error_metrics(self):
        """Analyze error metrics for patterns and trends"""
        for error_type, errors in self.error_metrics.items():
            # Remove errors older than 24 hours
            self.error_metrics[error_type] = [
                error for error in errors
                if (datetime.utcnow() - error["timestamp"]).total_seconds() < 86400
            ]
            
            # Analyze error patterns
            if len(errors) > 0:
                error_paths = defaultdict(int)
                error_methods = defaultdict(int)
                error_users = defaultdict(int)
                
                for error in errors:
                    error_paths[error["path"]] += 1
                    error_methods[error["method"]] += 1
                    if error.get("user_id"):
                        error_users[error["user_id"]] += 1
                        
                # Log patterns if significant
                if max(error_paths.values()) > 10:
                    logger.warning(
                        f"Error pattern detected for {error_type}",
                        extra={
                            "most_common_path": max(error_paths.items(), key=lambda x: x[1]),
                            "most_common_method": max(error_methods.items(), key=lambda x: x[1]),
                            "affected_users": len(error_users)
                        }
                    )
                    
    def log_error(self, error_type: str, error_id: str, path: str, method: str):
        """Log an error occurrence for monitoring"""
        self.error_metrics[error_type].append({
            "error_id": error_id,
            "timestamp": datetime.utcnow(),
            "path": path,
            "method": method
        })

class DatabaseMonitor:
    """Monitor database performance"""
    
    def __init__(self):
        self.query_times: Dict[str, float] = {}
        self.slow_query_threshold = 1.0  # seconds
        self.error_queries: List[Dict[str, Any]] = []
        
    def log_query(self, query: str, duration: float):
        """Log database query performance"""
        self.query_times[query] = duration
        
        if duration > self.slow_query_threshold:
            logger.warning(
                "Slow database query",
                extra={
                    "query": query,
                    "duration": duration,
                    "threshold": self.slow_query_threshold
                }
            )
            
    def log_query_error(self, query: str, error: str, stack_trace: str):
        """Log database query errors"""
        self.error_queries.append({
            "timestamp": datetime.utcnow(),
            "query": query,
            "error": error,
            "stack_trace": stack_trace
        })
        
        # Keep only last 1000 errors
        if len(self.error_queries) > 1000:
            self.error_queries = self.error_queries[-1000:]
            
    def get_slow_queries(self) -> Dict[str, float]:
        """Get all queries that exceeded the threshold"""
        return {
            query: duration
            for query, duration in self.query_times.items()
            if duration > self.slow_query_threshold
        }
        
    def get_query_errors(self) -> List[Dict[str, Any]]:
        """Get recent query errors"""
        return self.error_queries

# Initialize monitors
performance_monitor = PerformanceMonitor()
database_monitor = DatabaseMonitor() 