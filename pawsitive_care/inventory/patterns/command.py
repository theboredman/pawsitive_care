"""
Command Pattern Implementation for Inventory Management

This module implements the Command pattern to encapsulate stock operations
as objects, enabling undo/redo functionality and operation queuing.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StockCommand(ABC):
    """Abstract base class for stock commands"""
    
    def __init__(self, item_id: int, quantity: int, reason: str = "", user: str = "System"):
        """
        Initialize command with basic parameters.
        
        Args:
            item_id: ID of the inventory item
            quantity: Quantity to operate on
            reason: Reason for the operation
            user: User performing the operation
        """
        self.item_id = item_id
        self.quantity = quantity
        self.reason = reason
        self.user = user
        self.timestamp = datetime.now()
        self.executed = False
        self.previous_quantity = None
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command"""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of the command"""
        pass
    
    def can_undo(self) -> bool:
        """Check if this command can be undone"""
        return self.executed and self.previous_quantity is not None


class AddStockCommand(StockCommand):
    """Command to add stock to an inventory item"""
    
    def execute(self) -> bool:
        """Add stock to the item"""
        try:
            # Import here to avoid circular imports
            from ..models import InventoryItem
            
            item = InventoryItem.objects.get(id=self.item_id)
            self.previous_quantity = item.quantity_in_stock
            
            # Add stock
            item.quantity_in_stock += self.quantity
            item.save()
            
            # Create stock movement record
            self._create_stock_movement(item, 'IN')
            
            self.executed = True
            logger.info(f"Added {self.quantity} units to {item.name}. New quantity: {item.quantity_in_stock}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute AddStockCommand: {e}")
            return False
    
    def undo(self) -> bool:
        """Remove the added stock"""
        if not self.can_undo():
            return False
        
        try:
            from ..models import InventoryItem
            
            item = InventoryItem.objects.get(id=self.item_id)
            
            # Restore previous quantity
            item.quantity_in_stock = self.previous_quantity
            item.save()
            
            # Create reversal stock movement record
            self._create_stock_movement(item, 'OUT', is_reversal=True)
            
            self.executed = False
            logger.info(f"Undid add operation for {item.name}. Restored quantity: {item.quantity_in_stock}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to undo AddStockCommand: {e}")
            return False
    
    def get_description(self) -> str:
        return f"Add {self.quantity} units (Reason: {self.reason})"
    
    def _create_stock_movement(self, item, movement_type: str, is_reversal: bool = False):
        """Create a stock movement record"""
        try:
            from ..models import StockMovement
            
            # Calculate old and new quantities based on operation
            if movement_type == 'IN':
                old_qty = item.quantity_in_stock - self.quantity
                new_qty = item.quantity_in_stock
            elif movement_type == 'OUT':
                old_qty = item.quantity_in_stock + self.quantity
                new_qty = item.quantity_in_stock
            else:  # ADJUSTMENT
                old_qty = self.previous_quantity
                new_qty = item.quantity_in_stock
            
            StockMovement.objects.create(
                item=item,
                movement_type=movement_type,
                quantity=self.quantity,
                reason=f"{'UNDO: ' if is_reversal else ''}{self.reason}",
                old_quantity=old_qty,
                new_quantity=new_qty,
                created_by=self.user if hasattr(self.user, 'id') else None,
                notes=f"Command executed at {self.timestamp}"
            )
        except Exception as e:
            logger.error(f"Failed to create stock movement: {e}")


class RemoveStockCommand(StockCommand):
    """Command to remove stock from an inventory item"""
    
    def execute(self) -> bool:
        """Remove stock from the item"""
        try:
            from ..models import InventoryItem
            
            item = InventoryItem.objects.get(id=self.item_id)
            self.previous_quantity = item.quantity_in_stock
            
            # Check if sufficient stock available
            if item.quantity_in_stock < self.quantity:
                logger.warning(f"Insufficient stock for {item.name}. Available: {item.quantity_in_stock}, Requested: {self.quantity}")
                return False
            
            # Remove stock
            item.quantity_in_stock -= self.quantity
            item.save()
            
            # Create stock movement record
            self._create_stock_movement(item, 'OUT')
            
            self.executed = True
            logger.info(f"Removed {self.quantity} units from {item.name}. New quantity: {item.quantity_in_stock}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute RemoveStockCommand: {e}")
            return False
    
    def undo(self) -> bool:
        """Restore the removed stock"""
        if not self.can_undo():
            return False
        
        try:
            from ..models import InventoryItem
            
            item = InventoryItem.objects.get(id=self.item_id)
            
            # Restore previous quantity
            item.quantity_in_stock = self.previous_quantity
            item.save()
            
            # Create reversal stock movement record
            self._create_stock_movement(item, 'IN', is_reversal=True)
            
            self.executed = False
            logger.info(f"Undid remove operation for {item.name}. Restored quantity: {item.quantity_in_stock}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to undo RemoveStockCommand: {e}")
            return False
    
    def get_description(self) -> str:
        return f"Remove {self.quantity} units (Reason: {self.reason})"
    
    def _create_stock_movement(self, item, movement_type: str, is_reversal: bool = False):
        """Create a stock movement record"""
        try:
            from ..models import StockMovement
            
            # Calculate old and new quantities based on operation
            if movement_type == 'IN':
                old_qty = item.quantity_in_stock - self.quantity
                new_qty = item.quantity_in_stock
            elif movement_type == 'OUT':
                old_qty = item.quantity_in_stock + self.quantity
                new_qty = item.quantity_in_stock
            else:  # ADJUSTMENT
                old_qty = self.previous_quantity
                new_qty = item.quantity_in_stock
            
            StockMovement.objects.create(
                item=item,
                movement_type=movement_type,
                quantity=self.quantity,
                reason=f"{'UNDO: ' if is_reversal else ''}{self.reason}",
                old_quantity=old_qty,
                new_quantity=new_qty,
                created_by=self.user if hasattr(self.user, 'id') else None,
                notes=f"Command executed at {self.timestamp}"
            )
        except Exception as e:
            logger.error(f"Failed to create stock movement: {e}")


class AdjustStockCommand(StockCommand):
    """Command to adjust stock to a specific quantity"""
    
    def __init__(self, item_id: int, new_quantity: int, reason: str = "", user: str = "System"):
        """
        Initialize stock adjustment command.
        
        Args:
            item_id: ID of the inventory item
            new_quantity: New quantity to set
            reason: Reason for the adjustment
            user: User performing the operation
        """
        super().__init__(item_id, new_quantity, reason, user)
        self.new_quantity = new_quantity
    
    def execute(self) -> bool:
        """Adjust stock to the new quantity"""
        try:
            from ..models import InventoryItem
            
            item = InventoryItem.objects.get(id=self.item_id)
            self.previous_quantity = item.quantity_in_stock
            
            # Calculate adjustment
            adjustment = self.new_quantity - item.quantity_in_stock
            
            # Set new quantity
            item.quantity_in_stock = self.new_quantity
            item.save()
            
            # Create stock movement record
            movement_type = 'IN' if adjustment > 0 else 'OUT'
            self._create_stock_movement(item, movement_type, abs(adjustment))
            
            self.executed = True
            logger.info(f"Adjusted {item.name} stock to {self.new_quantity}. Previous: {self.previous_quantity}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute AdjustStockCommand: {e}")
            return False
    
    def undo(self) -> bool:
        """Restore the previous quantity"""
        if not self.can_undo():
            return False
        
        try:
            from ..models import InventoryItem
            
            item = InventoryItem.objects.get(id=self.item_id)
            
            # Calculate reversal adjustment
            adjustment = self.previous_quantity - item.quantity_in_stock
            
            # Restore previous quantity
            item.quantity_in_stock = self.previous_quantity
            item.save()
            
            # Create reversal stock movement record
            movement_type = 'IN' if adjustment > 0 else 'OUT'
            self._create_stock_movement(item, movement_type, abs(adjustment), is_reversal=True)
            
            self.executed = False
            logger.info(f"Undid adjustment for {item.name}. Restored quantity: {item.quantity_in_stock}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to undo AdjustStockCommand: {e}")
            return False
    
    def get_description(self) -> str:
        return f"Adjust to {self.new_quantity} units (Reason: {self.reason})"
    
    def _create_stock_movement(self, item, movement_type: str, quantity: int, is_reversal: bool = False):
        """Create a stock movement record"""
        try:
            from ..models import StockMovement
            
            # Calculate old and new quantities based on operation
            if movement_type == 'IN':
                old_qty = item.quantity_in_stock - quantity
                new_qty = item.quantity_in_stock
            elif movement_type == 'OUT':
                old_qty = item.quantity_in_stock + quantity
                new_qty = item.quantity_in_stock
            else:  # ADJUSTMENT
                old_qty = self.previous_quantity
                new_qty = item.quantity_in_stock
            
            StockMovement.objects.create(
                item=item,
                movement_type=movement_type,
                quantity=quantity,
                reason=f"{'UNDO: ' if is_reversal else ''}{self.reason}",
                old_quantity=old_qty,
                new_quantity=new_qty,
                created_by=self.user if hasattr(self.user, 'id') else None,
                notes=f"Command executed at {self.timestamp}"
            )
        except Exception as e:
            logger.error(f"Failed to create stock movement: {e}")


class StockCommandInvoker:
    """
    Invoker class that manages command execution and provides undo/redo functionality.
    Maintains command history and allows batch operations.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize command invoker.
        
        Args:
            max_history: Maximum number of commands to keep in history
        """
        self.command_history: List[StockCommand] = []
        self.max_history = max_history
        self.current_position = -1
    
    def execute_command(self, command: StockCommand) -> bool:
        """
        Execute a command and add it to history.
        
        Args:
            command: Command to execute
            
        Returns:
            True if execution was successful
        """
        if command.execute():
            # Remove any commands after current position (for redo functionality)
            if self.current_position < len(self.command_history) - 1:
                self.command_history = self.command_history[:self.current_position + 1]
            
            # Add command to history
            self.command_history.append(command)
            self.current_position += 1
            
            # Maintain history size limit
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)
                self.current_position -= 1
            
            logger.info(f"Executed command: {command.get_description()}")
            return True
        
        return False
    
    def undo_last_command(self) -> bool:
        """
        Undo the last executed command.
        
        Returns:
            True if undo was successful
        """
        if self.current_position >= 0:
            command = self.command_history[self.current_position]
            if command.undo():
                self.current_position -= 1
                logger.info(f"Undid command: {command.get_description()}")
                return True
        
        return False
    
    def redo_command(self) -> bool:
        """
        Redo the next command in history.
        
        Returns:
            True if redo was successful
        """
        if self.current_position < len(self.command_history) - 1:
            self.current_position += 1
            command = self.command_history[self.current_position]
            if command.execute():
                logger.info(f"Redid command: {command.get_description()}")
                return True
            else:
                self.current_position -= 1
        
        return False
    
    def execute_batch(self, commands: List[StockCommand]) -> Dict[str, Any]:
        """
        Execute multiple commands as a batch.
        
        Args:
            commands: List of commands to execute
            
        Returns:
            Dictionary with execution results
        """
        results = {
            'total_commands': len(commands),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for command in commands:
            if self.execute_command(command):
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to execute: {command.get_description()}")
        
        return results
    
    def get_command_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get command history.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of command information
        """
        history = self.command_history[-limit:] if limit else self.command_history
        
        return [
            {
                'description': cmd.get_description(),
                'timestamp': cmd.timestamp,
                'user': cmd.user,
                'executed': cmd.executed,
                'can_undo': cmd.can_undo()
            }
            for cmd in history
        ]
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        self.current_position = -1
        logger.info("Cleared command history")
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return self.current_position >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible"""
        return self.current_position < len(self.command_history) - 1


# Helper function to get command invoker instance (to avoid circular imports)
def get_stock_command_invoker():
    """Get stock command invoker instance"""
    return StockCommandInvoker()
