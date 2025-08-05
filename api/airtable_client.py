"""
Airtable read/write abstractions for the service station operations bot.

Handles all interactions with Airtable base for storing and retrieving data.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import asyncio

from pyairtable import Api, Base, Table

logger = logging.getLogger(__name__)

class AirtableClient:
    """Handles Airtable operations."""
    
    def __init__(self, api_key: str, base_id: str):
        self.api_key = api_key
        self.base_id = base_id
        # Initialize Airtable client
        self.api = Api(api_key)
        self.base = self.api.base(base_id)
        
        # Table names and IDs (from actual Airtable base)
        self.petty_cash_table = "Petty Cash"
        self.petty_cash_table_id = "tblzh9vb96VrEvwZU"
        self.fuel_log_table = "Fuel Logs"
        self.fuel_log_table_id = "tblokwpw2cvNp5I8M"
        self.tasks_table = "Tasks"
        self.tasks_table_id = "tbl6XreR1ctmQsNJD"
        self.issues_table = "Issues"
        self.issues_table_id = "tblhmLkzbahZA5Afx"
        self.config_table = "Config"
        
        # Field mappings for Petty Cash table
        self.petty_cash_fields = {
            'person': 'Person',
            'amount': 'Amount',
            'description': 'Description',
            'date': 'Date',
            'receipt_photo': 'Receipt Photo',
            'theoretical_balance': 'Theoretical Balance',
            'actual_balance': 'Actual Balance',
            'reconciliation_diff': 'Reconciliation Diff'
        }
        
        # Field mappings for Fuel Logs table
        self.fuel_log_fields = {
            'driver': 'Driver',
            'vehicle': 'Vehicle',
            'date': 'Date',
            'liters': 'Liters',
            'odometer_start': 'Odometer Start',
            'odometer_end': 'Odometer End',
            'purpose': 'Purpose',
            'logged_by': 'Logged By',
            'kms_travelled': 'KMs Travelled',
            'fuel_efficiency': 'Fuel Efficiency'
        }
        
        # Field mappings for Tasks table
        self.tasks_fields = {
            'task_title': 'Task',
            'details': 'Details',
            'status': 'Status',
            'deadline': 'Deadline',
            'assigned_to': 'Assigned To',
            'created_at': 'Created At',
            'notes': 'Notes'
        }
        
        # Field mappings for Issues table
        self.issues_fields = {
            'reported_by': 'Reported By',
            'category': 'Category',
            'description': 'Description',
            'severity': 'Severity',
            'date': 'Date',
            'status': 'Status',
            'resolution_notes': 'Resolution Notes'
        }
        
        # Valid vehicle options
        self.valid_vehicles = ['Toyota Hilux', 'Toyota Prado', 'Other']
    
    async def create_expense(self, data: Dict[str, Any]) -> Optional[str]:
        """Create a new expense record in Petty Cash table."""
        try:
            table = self.base.table(self.petty_cash_table)
            
            # Map data to Airtable field names
            record_data = {
                self.petty_cash_fields['date']: data["date"],
                self.petty_cash_fields['amount']: data["amount"],
                self.petty_cash_fields['description']: data["description"],
                self.petty_cash_fields['person']: data.get("person", "Me")
            }
            
            # Add receipt photo if provided
            if data.get("receipt_url"):
                record_data[self.petty_cash_fields['receipt_photo']] = [{"url": data["receipt_url"]}]
            
            record = table.create(record_data)
            logger.info(f"Created expense record: {record['id']}")
            return record["id"]
            
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            return None
    
    async def create_fuel_log(self, data: Dict[str, Any]) -> Optional[str]:
        """Create a new fuel log record."""
        try:
            table = self.base.table(self.fuel_log_table)
            
            # Validate vehicle selection
            vehicle = data.get("vehicle", "")
            if vehicle not in self.valid_vehicles:
                logger.warning(f"Invalid vehicle: {vehicle}. Valid options: {self.valid_vehicles}")
                vehicle = "Other"  # Default to Other if invalid
            
            # Map data to Airtable field names
            record_data = {
                self.fuel_log_fields['date']: data["date"],
                self.fuel_log_fields['vehicle']: vehicle,
                self.fuel_log_fields['driver']: data["driver"],
                self.fuel_log_fields['liters']: data["liters"],
                self.fuel_log_fields['purpose']: data.get("purpose", ""),
                self.fuel_log_fields['logged_by']: data.get("logged_by", "Me")
            }
            
            # Add odometer readings if provided
            if data.get("odometer_start"):
                record_data[self.fuel_log_fields['odometer_start']] = data["odometer_start"]
            if data.get("odometer_end"):
                record_data[self.fuel_log_fields['odometer_end']] = data["odometer_end"]
            
            record = table.create(record_data)
            logger.info(f"Created fuel log record: {record['id']}")
            return record["id"]
            
        except Exception as e:
            logger.error(f"Error creating fuel log: {e}")
            return None
    
    async def create_task(self, data: Dict[str, Any]) -> Optional[str]:
        """Create a new task record."""
        try:
            table = self.base.table(self.tasks_table)
            
            # Map data to Airtable field names
            record_data = {
                self.tasks_fields['task_title']: data["task_title"],
                self.tasks_fields['status']: data.get("status", "To Do"),
                self.tasks_fields['assigned_to']: data.get("assigned_to", "Nthambi"),
                self.tasks_fields['created_at']: data.get("date", datetime.now().strftime("%Y-%m-%d"))
            }
            
            # Add optional fields if provided
            if data.get("details"):
                record_data[self.tasks_fields['details']] = data["details"]
            
            if data.get("deadline"):
                record_data[self.tasks_fields['deadline']] = data["deadline"]
            
            if data.get("notes"):
                record_data[self.tasks_fields['notes']] = data["notes"]
            
            record = table.create(record_data)
            logger.info(f"Created task record: {record['id']}")
            return record["id"]
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    async def create_issue(self, data: Dict[str, Any]) -> Optional[str]:
        """Create a new issue record."""
        try:
            table = self.base.table(self.issues_table)
            
            # Map data to Airtable field names
            record_data = {
                self.issues_fields['description']: data["description"],
                self.issues_fields['severity']: data.get("severity", "Low"),
                self.issues_fields['status']: data.get("status", "Open"),
                self.issues_fields['date']: data.get("date", datetime.now().strftime("%Y-%m-%d")),
                self.issues_fields['reported_by']: data.get("reported_by", "Nthambi")
            }
            
            # Add optional fields if provided
            if data.get("category"):
                record_data[self.issues_fields['category']] = data["category"]
            
            if data.get("resolution_notes"):
                record_data[self.issues_fields['resolution_notes']] = data["resolution_notes"]
            
            record = table.create(record_data)
            logger.info(f"Created issue record: {record['id']}")
            return record["id"]
            
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            return None
    
    async def get_todays_expenses(self) -> List[Dict[str, Any]]:
        """Get all expenses for today."""
        try:
            # TODO: Implement Airtable query
            # table = self.base.table(self.petty_cash_table)
            # today = date.today().isoformat()
            # records = table.all(formula=f"{{Date}} = '{today}'")
            # return [record["fields"] for record in records]
            
            logger.info("Would get today's expenses")
            return []
            
        except Exception as e:
            logger.error(f"Error getting today's expenses: {e}")
            return []
    
    async def get_todays_fuel_logs(self) -> List[Dict[str, Any]]:
        """Get all fuel logs for today."""
        try:
            # TODO: Implement Airtable query
            # table = self.base.table(self.fuel_log_table)
            # today = date.today().isoformat()
            # records = table.all(formula=f"{{Date}} = '{today}'")
            # return [record["fields"] for record in records]
            
            logger.info("Would get today's fuel logs")
            return []
            
        except Exception as e:
            logger.error(f"Error getting today's fuel logs: {e}")
            return []
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all pending tasks."""
        try:
            # TODO: Implement Airtable query
            # table = self.base.table(self.tasks_table)
            # records = table.all(formula="OR({Status} = 'To Do', {Status} = 'In Progress')")
            # return [record["fields"] for record in records]
            
            logger.info("Would get pending tasks")
            return []
            
        except Exception as e:
            logger.error(f"Error getting pending tasks: {e}")
            return []
    
    async def get_open_issues(self) -> List[Dict[str, Any]]:
        """Get all open issues."""
        try:
            # TODO: Implement Airtable query
            # table = self.base.table(self.issues_table)
            # records = table.all(formula="{Status} = 'Open'")
            # return [record["fields"] for record in records]
            
            logger.info("Would get open issues")
            return []
            
        except Exception as e:
            logger.error(f"Error getting open issues: {e}")
            return []
    
    async def get_petty_cash_balance(self) -> Optional[float]:
        """Get current petty cash theoretical balance."""
        try:
            # TODO: Implement balance calculation
            # This would need to query the config table for starting balance
            # and calculate based on all expenses
            logger.info("Would get petty cash balance")
            return 100000.0  # Mock value
            
        except Exception as e:
            logger.error(f"Error getting petty cash balance: {e}")
            return None
    
    async def update_actual_balance(self, actual_balance: float) -> bool:
        """Update the actual petty cash balance for reconciliation."""
        try:
            # TODO: Implement balance update
            # This would update a config record or create a reconciliation entry
            logger.info(f"Would update actual balance to: {actual_balance}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating actual balance: {e}")
            return False
    
    async def get_all_data_for_export(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all data for export functionality."""
        try:
            # TODO: Implement comprehensive data retrieval
            # This would get all records from all tables for the export period
            logger.info("Would get all data for export")
            return {
                "petty_cash": [],
                "fuel_logs": [],
                "tasks": [],
                "issues": []
            }
            
        except Exception as e:
            logger.error(f"Error getting data for export: {e}")
            return {}

# Global client instance (to be initialized with API key and base ID)
client: Optional[AirtableClient] = None 