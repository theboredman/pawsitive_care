"""
Observer Pattern Implementation for Inventory Management

This module implements the Observer pattern to handle real-time notifications
for inventory changes, low stock alerts, and other inventory events.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class StockObserver(ABC):
    """Abstract base class for stock observers"""
    
    @abstractmethod
    def update(self, item_name: str, old_quantity: int, new_quantity: int, **kwargs):
        """Called when stock levels change"""
        pass


class LowStockObserver(StockObserver):
    """Observer for low stock notifications"""
    
    def __init__(self, threshold: int = 10):
        self.threshold = threshold
    
    def update(self, item_name: str, old_quantity: int, new_quantity: int, **kwargs):
        """Send notification if stock falls below threshold"""
        if new_quantity <= self.threshold and old_quantity > self.threshold:
            self._send_low_stock_alert(item_name, new_quantity)
        elif new_quantity > self.threshold and old_quantity <= self.threshold:
            self._send_stock_restored_alert(item_name, new_quantity)
    
    def _send_low_stock_alert(self, item_name: str, quantity: int):
        """Send low stock alert"""
        message = f"LOW STOCK ALERT: {item_name} has only {quantity} units remaining"
        logger.warning(message)
        # In a real implementation, this could send emails, SMS, etc.
    
    def _send_stock_restored_alert(self, item_name: str, quantity: int):
        """Send stock restored notification"""
        message = f"STOCK RESTORED: {item_name} now has {quantity} units available"
        logger.info(message)


class ExpiryObserver(StockObserver):
    """Observer for expiry date notifications"""
    
    def update(self, item_name: str, old_quantity: int, new_quantity: int, **kwargs):
        """Check for items nearing expiry"""
        expiry_date = kwargs.get('expiry_date')
        if expiry_date:
            self._check_expiry_alert(item_name, expiry_date)
    
    def _check_expiry_alert(self, item_name: str, expiry_date):
        """Check if item is nearing expiry"""
        from datetime import datetime, timedelta
        
        if expiry_date:
            days_until_expiry = (expiry_date - datetime.now().date()).days
            if 0 <= days_until_expiry <= 30:  # Alert if expiring within 30 days
                message = f"EXPIRY ALERT: {item_name} expires in {days_until_expiry} days"
                logger.warning(message)


class AuditObserver(StockObserver):
    """Observer for audit trail"""
    
    def update(self, item_name: str, old_quantity: int, new_quantity: int, **kwargs):
        """Log all stock changes for audit purposes"""
        user = kwargs.get('user', 'System')
        reason = kwargs.get('reason', 'Stock update')
        
        change = new_quantity - old_quantity
        action = "added" if change > 0 else "removed"
        
        message = (f"AUDIT: {user} {action} {abs(change)} units of {item_name}. "
                  f"Stock changed from {old_quantity} to {new_quantity}. Reason: {reason}")
        logger.info(message)


class InventoryNotificationCenter:
    """
    Notification center that manages observers and broadcasts inventory events.
    Implements the Observer pattern as the Subject.
    """
    
    def __init__(self):
        self._observers: List[StockObserver] = []
        self._notifications: List[Dict[str, Any]] = []
    
    def add_observer(self, observer: StockObserver):
        """Add an observer to the notification center"""
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"Added observer: {observer.__class__.__name__}")
    
    def remove_observer(self, observer: StockObserver):
        """Remove an observer from the notification center"""
        if observer in self._observers:
            self._observers.remove(observer)
            logger.info(f"Removed observer: {observer.__class__.__name__}")
    
    def notify_stock_change(self, item_name: str, old_quantity: int, new_quantity: int, **kwargs):
        """Notify all observers of a stock change"""
        for observer in self._observers:
            try:
                observer.update(item_name, old_quantity, new_quantity, **kwargs)
            except Exception as e:
                logger.error(f"Error notifying observer {observer.__class__.__name__}: {e}")
        
        # Store notification for history
        self._notifications.append({
            'item_name': item_name,
            'old_quantity': old_quantity,
            'new_quantity': new_quantity,
            'timestamp': kwargs.get('timestamp'),
            'user': kwargs.get('user'),
            'reason': kwargs.get('reason')
        })
    
    def get_recent_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent notifications"""
        return self._notifications[-limit:]
    
    def clear_notifications(self):
        """Clear notification history"""
        self._notifications.clear()


# Global notification center instance
notification_center = InventoryNotificationCenter()

# Add default observers
notification_center.add_observer(LowStockObserver(threshold=10))
notification_center.add_observer(ExpiryObserver())
notification_center.add_observer(AuditObserver())
