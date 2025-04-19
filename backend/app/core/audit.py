from datetime import datetime
from typing import Dict, Any, Optional, List
from .logging import get_audit_logger
from pydantic import BaseModel
import json
from pathlib import Path
from collections import defaultdict

audit_logger = get_audit_logger()

class AuditEvent(BaseModel):
    """Model for audit events"""
    timestamp: datetime
    event_type: str
    user_id: Optional[str]
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    status: str
    error_id: Optional[str] = None
    severity: str = "info"

class SecurityEvent(BaseModel):
    """Model for security events"""
    timestamp: datetime
    event_type: str
    user_id: Optional[str]
    ip_address: Optional[str]
    action: str
    details: Dict[str, Any]
    status: str
    error_id: Optional[str] = None
    severity: str
    mitigation: Optional[str] = None

class AuditTrail:
    """Track and manage audit events"""
    
    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.security_events: List[SecurityEvent] = []
        self.error_patterns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
    def log_event(self, event: AuditEvent):
        """Log an audit event"""
        # Log to file
        log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(f"{json.dumps(event.dict())}\n")
            
        # Log to audit logger
        audit_logger.info(
            f"Audit event: {event.event_type}",
            extra=event.dict()
        )
        
        # Track error patterns for security events
        if event.status == "error" and event.error_id:
            self.error_patterns[event.event_type][event.action] += 1
            
    def log_security_event(self, event: SecurityEvent):
        """Log a security event with enhanced tracking"""
        # Add to security events list
        self.security_events.append(event)
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
            
        # Log to file
        log_file = self.log_dir / f"security_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(f"{json.dumps(event.dict())}\n")
            
        # Log to audit logger with appropriate level
        if event.severity == "critical":
            audit_logger.critical(
                f"Security event: {event.event_type}",
                extra=event.dict()
            )
        elif event.severity == "error":
            audit_logger.error(
                f"Security event: {event.event_type}",
                extra=event.dict()
            )
        else:
            audit_logger.warning(
                f"Security event: {event.event_type}",
                extra=event.dict()
            )
            
        # Check for security patterns
        self._analyze_security_patterns()
        
    def _analyze_security_patterns(self):
        """Analyze security events for patterns"""
        # Group events by type and IP
        ip_events = defaultdict(list)
        user_events = defaultdict(list)
        
        for event in self.security_events:
            if event.ip_address:
                ip_events[event.ip_address].append(event)
            if event.user_id:
                user_events[event.user_id].append(event)
                
        # Check for suspicious patterns
        for ip, events in ip_events.items():
            if len(events) > 10:  # More than 10 security events from same IP
                audit_logger.warning(
                    "Suspicious IP activity detected",
                    extra={
                        "ip": ip,
                        "event_count": len(events),
                        "event_types": [e.event_type for e in events]
                    }
                )
                
        for user_id, events in user_events.items():
            if len(events) > 5:  # More than 5 security events for same user
                audit_logger.warning(
                    "Suspicious user activity detected",
                    extra={
                        "user_id": user_id,
                        "event_count": len(events),
                        "event_types": [e.event_type for e in events]
                    }
                )
                
    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[AuditEvent]:
        """Retrieve audit events with optional filtering"""
        events = []
        
        # Get all log files in the date range
        log_files = self.log_dir.glob("audit_*.log")
        for log_file in log_files:
            file_date = datetime.strptime(log_file.stem.split("_")[1], "%Y%m%d")
            if start_date and file_date < start_date:
                continue
            if end_date and file_date > end_date:
                continue
                
            with open(log_file, "r") as f:
                for line in f:
                    event_data = json.loads(line)
                    event = AuditEvent(**event_data)
                    
                    # Apply filters
                    if event_type and event.event_type != event_type:
                        continue
                    if user_id and event.user_id != user_id:
                        continue
                        
                    events.append(event)
                    
        return sorted(events, key=lambda x: x.timestamp)
        
    def get_security_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[SecurityEvent]:
        """Retrieve security events with optional filtering"""
        events = self.security_events
        
        # Apply filters
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if severity:
            events = [e for e in events if e.severity == severity]
            
        return sorted(events, key=lambda x: x.timestamp)
        
    def generate_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an audit report"""
        events = self.get_events(start_date, end_date, event_type, user_id)
        security_events = self.get_security_events(start_date, end_date)
        
        report = {
            "total_events": len(events),
            "total_security_events": len(security_events),
            "event_types": {},
            "security_event_types": {},
            "users": {},
            "status_counts": {},
            "security_severities": {},
            "timeline": [],
            "error_patterns": dict(self.error_patterns)
        }
        
        for event in events:
            # Count event types
            report["event_types"][event.event_type] = report["event_types"].get(event.event_type, 0) + 1
            
            # Count user actions
            if event.user_id:
                report["users"][event.user_id] = report["users"].get(event.user_id, 0) + 1
                
            # Count statuses
            report["status_counts"][event.status] = report["status_counts"].get(event.status, 0) + 1
            
            # Add to timeline
            report["timeline"].append({
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "user_id": event.user_id,
                "action": event.action,
                "status": event.status
            })
            
        for event in security_events:
            # Count security event types
            report["security_event_types"][event.event_type] = report["security_event_types"].get(event.event_type, 0) + 1
            
            # Count severities
            report["security_severities"][event.severity] = report["security_severities"].get(event.severity, 0) + 1
            
        return report

# Initialize audit trail
audit_trail = AuditTrail() 