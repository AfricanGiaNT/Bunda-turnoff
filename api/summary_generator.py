"""
Daily summary logic for the service station operations bot.

Generates daily summaries of operations and sends them via Telegram.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from dataclasses import dataclass

# TODO: Import dependencies once created
# from .airtable_client import client
# from .telegram_handler import handler

logger = logging.getLogger(__name__)

@dataclass
class DailySummary:
    """Container for daily summary data."""
    date: str
    petty_cash_spent: float
    petty_cash_theoretical_balance: float
    petty_cash_actual_balance: Optional[float]
    petty_cash_diff: Optional[float]
    fuel_summary: List[Dict[str, Any]]
    total_fuel_liters: float
    pending_tasks: List[Dict[str, Any]]
    open_issues: List[Dict[str, Any]]
    new_issues_count: int
    high_severity_issues: int

class SummaryGenerator:
    """Handles daily summary generation and sending."""
    
    def __init__(self):
        pass
    
    async def generate_daily_summary(self, target_date: Optional[date] = None) -> Optional[DailySummary]:
        """Generate a daily summary for the specified date (defaults to today)."""
        try:
            if target_date is None:
                target_date = date.today()
            
            # TODO: Get data from Airtable client
            # expenses = await client.get_todays_expenses()
            # fuel_logs = await client.get_todays_fuel_logs()
            # pending_tasks = await client.get_pending_tasks()
            # open_issues = await client.get_open_issues()
            # petty_cash_balance = await client.get_petty_cash_balance()
            
            # Mock data for now
            expenses = []
            fuel_logs = []
            pending_tasks = []
            open_issues = []
            petty_cash_balance = 100000.0
            
            # Calculate summary data
            petty_cash_spent = sum(expense.get("Amount", 0) for expense in expenses)
            petty_cash_theoretical_balance = petty_cash_balance - petty_cash_spent
            petty_cash_actual_balance = None  # Would be set manually
            petty_cash_diff = None
            
            # Group fuel by vehicle
            fuel_summary = self._group_fuel_by_vehicle(fuel_logs)
            total_fuel_liters = sum(log.get("Liters", 0) for log in fuel_logs)
            
            # Count issues
            new_issues_count = len([issue for issue in open_issues if issue.get("Date") == target_date.isoformat()])
            high_severity_issues = len([issue for issue in open_issues if issue.get("Severity") == "High"])
            
            return DailySummary(
                date=target_date.isoformat(),
                petty_cash_spent=petty_cash_spent,
                petty_cash_theoretical_balance=petty_cash_theoretical_balance,
                petty_cash_actual_balance=petty_cash_actual_balance,
                petty_cash_diff=petty_cash_diff,
                fuel_summary=fuel_summary,
                total_fuel_liters=total_fuel_liters,
                pending_tasks=pending_tasks,
                open_issues=open_issues,
                new_issues_count=new_issues_count,
                high_severity_issues=high_severity_issues
            )
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return None
    
    def _group_fuel_by_vehicle(self, fuel_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group fuel logs by vehicle for summary."""
        vehicle_summary = {}
        
        for log in fuel_logs:
            vehicle = log.get("Vehicle", "Unknown")
            liters = log.get("Liters", 0)
            kms = log.get("KMs Travelled", 0)
            
            if vehicle not in vehicle_summary:
                vehicle_summary[vehicle] = {
                    "vehicle": vehicle,
                    "total_liters": 0,
                    "total_kms": 0,
                    "trips": 0
                }
            
            vehicle_summary[vehicle]["total_liters"] += liters
            vehicle_summary[vehicle]["total_kms"] += kms
            vehicle_summary[vehicle]["trips"] += 1
        
        return list(vehicle_summary.values())
    
    def format_summary_message(self, summary: DailySummary) -> str:
        """Format the daily summary as a Telegram message."""
        try:
            # Format date
            date_obj = datetime.fromisoformat(summary.date)
            formatted_date = date_obj.strftime("%b %d, %Y")
            
            # Build message
            message_lines = [f"Daily Summary – {formatted_date}"]
            
            # Petty Cash section
            petty_cash_line = f"• Petty Cash: Spent {summary.petty_cash_spent:,.0f} MWK today. "
            petty_cash_line += f"Theoretical balance: {summary.petty_cash_theoretical_balance:,.0f} MWK."
            
            if summary.petty_cash_actual_balance is not None:
                petty_cash_line += f" Actual float: {summary.petty_cash_actual_balance:,.0f} MWK. "
                if summary.petty_cash_diff is not None:
                    petty_cash_line += f"Diff: {summary.petty_cash_diff:+,.0f} MWK."
            
            message_lines.append(petty_cash_line)
            
            # Fuel section
            if summary.total_fuel_liters > 0:
                fuel_line = f"• Fuel: {summary.total_fuel_liters}L dispensed: "
                fuel_details = []
                for vehicle in summary.fuel_summary:
                    fuel_details.append(f"{vehicle['vehicle']} ({vehicle['total_liters']}L, {vehicle['total_kms']} km)")
                fuel_line += ", ".join(fuel_details) + "."
                message_lines.append(fuel_line)
            else:
                message_lines.append("• Fuel: No fuel dispensed today.")
            
            # Tasks section
            if summary.pending_tasks:
                task_titles = [task.get("Task", "Unknown") for task in summary.pending_tasks[:5]]  # Limit to 5
                task_line = f"• Tasks: {len(summary.pending_tasks)} pending"
                if task_titles:
                    task_line += f" ({', '.join(task_titles)})"
                task_line += "."
                message_lines.append(task_line)
            else:
                message_lines.append("• Tasks: No pending tasks.")
            
            # Issues section
            if summary.open_issues:
                issue_line = f"• Issues: {summary.new_issues_count} new"
                if summary.high_severity_issues > 0:
                    issue_line += f", {summary.high_severity_issues} high severity"
                issue_line += "."
                message_lines.append(issue_line)
            else:
                message_lines.append("• Issues: No open issues.")
            
            return "\n".join(message_lines)
            
        except Exception as e:
            logger.error(f"Error formatting summary message: {e}")
            return "Error generating daily summary."
    
    async def send_daily_summary(self, chat_id: int, target_date: Optional[date] = None) -> bool:
        """Generate and send daily summary to specified chat."""
        try:
            # Generate summary
            summary = await self.generate_daily_summary(target_date)
            if not summary:
                logger.error("Failed to generate daily summary")
                return False
            
            # Format message
            message = self.format_summary_message(summary)
            
            # TODO: Send via Telegram handler
            # await handler.send_message(chat_id, message)
            logger.info(f"Would send daily summary to chat {chat_id}: {message}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    async def send_summary_to_configured_chat(self, target_date: Optional[date] = None) -> bool:
        """Send daily summary to the configured chat (from environment)."""
        try:
            # TODO: Get chat ID from environment or config
            # chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))
            chat_id = 123456789  # Mock chat ID
            
            return await self.send_daily_summary(chat_id, target_date)
            
        except Exception as e:
            logger.error(f"Error sending summary to configured chat: {e}")
            return False

# Global generator instance
generator = SummaryGenerator() 