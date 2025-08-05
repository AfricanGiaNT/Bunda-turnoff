"""
GPT prompt construction + response interpretation for the service station operations bot.

Handles parsing of natural language messages into structured data for Airtable storage.
"""

import json
import logging
from typing import Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel

import openai

logger = logging.getLogger(__name__)

class EntryType(Enum):
    """Types of entries that can be logged."""
    EXPENSE = "expense"
    FUEL = "fuel"
    TASK = "task"
    ISSUE = "issue"

class ParsedEntry(BaseModel):
    """Structured data extracted from user message."""
    type: EntryType
    date: Optional[str] = None  # YYYY-MM-DD format, will be set to today if missing
    amount: Optional[float] = None
    description: Optional[str] = None
    person: Optional[str] = None
    receipt_url: Optional[str] = None
    vehicle: Optional[str] = None
    driver: Optional[str] = None
    liters: Optional[float] = None
    odometer_start: Optional[int] = None
    odometer_end: Optional[int] = None
    purpose: Optional[str] = None
    task_title: Optional[str] = None
    details: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[str] = None
    assigned_to: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    reported_by: Optional[str] = None

class GPTParser:
    """Handles GPT-based message parsing."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=api_key)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for GPT."""
        return """You are a structured logger for a service station operations system. 

Given a user message, classify it into one of: expense, fuel, task, issue. Extract relevant fields depending on type.

Output JSON with a type field and the appropriate keys:

- expense: date (default today), amount, description, person (default "Nthambi"), receipt_url (if provided)
- fuel: date (default today), vehicle, driver, liters, odometer_start, odometer_end, purpose
- task: task_title, details, status (default "To Do"), deadline (if mentioned), assigned_to (default "Nthambi")
- issue: category, description, severity (default "Low" if unspecified), status (default "Open"), reported_by (default "Nthambi")

For vehicle selection in fuel logs, use: "Toyota Hilux", "Toyota Prado", or "Other"
For amounts, extract numeric values only (e.g., "15,000 MWK" becomes 15000)
For dates, use YYYY-MM-DD format (today is 2025-08-04)
For task status, use: "To Do", "In Progress", "Done"
For issue severity, use: "Low", "Medium", "High"
For issue category, use: "Equipment", "Supply", "Complaint", "Other"
For issue status, use: "Open", "Resolved" (NOT "To Do" - that's only for tasks)

IMPORTANT: 
- Always include the date field with today's date (2025-08-04) if not specified
- Convert relative dates like "Friday" to actual dates (e.g., "Friday" becomes "2025-08-08")
- Auto-detect severity from keywords: "urgent", "critical", "emergency" = "High"; "important", "priority" = "Medium"; default = "Low"
- For tasks, if no assignment mentioned, default to "Nthambi"
- For issues, if no reporter mentioned, default to "Nthambi"

Example output:
{
  "type": "task",
  "task_title": "Safety inspection",
  "details": "Inspect all safety equipment",
  "status": "To Do",
  "deadline": "2025-08-08",
  "assigned_to": "Nthambi"
}

Only include fields that are present or can be reasonably inferred."""
    
    def get_example_messages(self) -> list:
        """Get example messages for few-shot learning."""
        return [
            {
                "role": "user",
                "content": "Paid 15,000 MWK for filter replacement from petty cash."
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "type": "expense",
                    "date": "2025-08-04",
                    "amount": 15000,
                    "description": "Filter replacement",
                    "person": "Me"
                })
            },
            {
                "role": "user",
                "content": "Spent 25,000 on generator fuel, receipt attached"
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "type": "expense",
                    "date": "2025-08-04",
                    "amount": 25000,
                    "description": "Generator fuel",
                    "person": "Me",
                    "receipt_url": "attached"
                })
            },
            {
                "role": "user",
                "content": "Gave 40 liters diesel to Hilux, driver John, for Salima trip. Odometer start 12300 end 12420."
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "type": "fuel",
                    "date": "2025-08-04",
                    "vehicle": "Toyota Hilux",
                    "driver": "John",
                    "liters": 40,
                    "odometer_start": 12300,
                    "odometer_end": 12420,
                    "purpose": "Salima trip"
                })
            },
            {
                "role": "user",
                "content": "Prado refueled 35L, driver Sarah, odometer 15600 to 15800, maintenance visit"
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "type": "fuel",
                    "date": "2025-08-04",
                    "vehicle": "Toyota Prado",
                    "driver": "Sarah",
                    "liters": 35,
                    "odometer_start": 15600,
                    "odometer_end": 15800,
                    "purpose": "Maintenance visit"
                })
            },
            {
                "role": "user",
                "content": "Assign John to safety inspection by Friday"
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "type": "task",
                    "task_title": "Safety inspection",
                    "details": "Assign John to safety inspection",
                    "status": "To Do",
                    "deadline": "2025-08-08",
                    "assigned_to": "John"
                })
            },
            {
                "role": "user",
                "content": "Urgent: Air compressor malfunctioning"
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "type": "issue",
                    "category": "Equipment",
                    "description": "Air compressor malfunctioning",
                    "severity": "High",
                    "status": "Open",
                    "reported_by": "Nthambi"
                })
            },
            {
                "role": "user",
                "content": "Need to prepare client presentation by next week"
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "type": "task",
                    "task_title": "Prepare client presentation",
                    "details": "Prepare client presentation",
                    "status": "To Do",
                    "deadline": "2025-08-11",
                    "assigned_to": "Nthambi"
                })
            },
            {
                "role": "user",
                "content": "Fuel supply running low"
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "type": "issue",
                    "category": "Supply",
                    "description": "Fuel supply running low",
                    "severity": "Medium",
                    "status": "Open",
                    "reported_by": "Nthambi"
                })
            }
        ]
    
    async def parse_message(self, message: str) -> Optional[ParsedEntry]:
        """Parse a natural language message into structured data."""
        try:
            # Check if message contains multiple entries separated by semicolons
            if ';' in message:
                # This is a multi-entry message, but we'll handle it in the calling code
                # For now, just parse the first entry to maintain backward compatibility
                first_entry = message.split(';')[0].strip()
                return await self._parse_single_message(first_entry)
            else:
                return await self._parse_single_message(message)
            
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    async def parse_multiple_entries(self, message: str) -> list[ParsedEntry]:
        """Parse a message containing multiple entries separated by semicolons."""
        try:
            # Split message by semicolons and clean up whitespace
            entries = [entry.strip() for entry in message.split(';') if entry.strip()]
            
            if len(entries) == 1:
                # Single entry, use regular parsing
                single_entry = await self._parse_single_message(entries[0])
                return [single_entry] if single_entry else []
            
            # Parse each entry individually
            parsed_entries = []
            for i, entry_text in enumerate(entries):
                logger.info(f"Parsing entry {i+1}/{len(entries)}: {entry_text}")
                
                parsed_entry = await self._parse_single_message(entry_text)
                if parsed_entry:
                    parsed_entries.append(parsed_entry)
                else:
                    logger.warning(f"Failed to parse entry {i+1}: {entry_text}")
            
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing multiple entries: {e}")
            return []
    
    async def _parse_single_message(self, message: str) -> Optional[ParsedEntry]:
        """Parse a single natural language message into structured data."""
        try:
            # Use asyncio.to_thread for the synchronous OpenAI call
            import asyncio
            
            def make_openai_call():
                return self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.get_system_prompt()},
                        *self.get_example_messages(),
                        {"role": "user", "content": message}
                    ],
                    temperature=0.1
                )
            
            response = await asyncio.to_thread(make_openai_call)
            
            content = response.choices[0].message.content
            logger.info(f"GPT response: {content}")
            parsed_data = json.loads(content)
            logger.info(f"Parsed data: {parsed_data}")
            
            # Convert to ParsedEntry
            entry_type = EntryType(parsed_data["type"])
            # Remove 'type' from parsed_data to avoid conflict
            parsed_data_copy = parsed_data.copy()
            del parsed_data_copy["type"]
            logger.info(f"Data after removing type: {parsed_data_copy}")
            
            # Set default date if missing
            if "date" not in parsed_data_copy or not parsed_data_copy["date"]:
                from datetime import datetime
                parsed_data_copy["date"] = datetime.now().strftime("%Y-%m-%d")
            
            # Validate classification and fix if needed
            if entry_type == EntryType.FUEL:
                # Check if it should actually be an issue (e.g., "fuel supply running low")
                if self.is_issue_message(message) and not any(word in message.lower() for word in ["liters", "used", "gave", "refueled"]):
                    entry_type = EntryType.ISSUE
                    # Try to extract issue info
                    if "urgent" in message.lower() or "critical" in message.lower() or "emergency" in message.lower():
                        parsed_data_copy["severity"] = "High"
                    elif "important" in message.lower() or "priority" in message.lower():
                        parsed_data_copy["severity"] = "Medium"
                    else:
                        parsed_data_copy["severity"] = "Low"
                    
                    # Determine category
                    if any(word in message.lower() for word in ["equipment", "machine", "compressor", "generator"]):
                        parsed_data_copy["category"] = "Equipment"
                    elif any(word in message.lower() for word in ["fuel", "supply", "material"]):
                        parsed_data_copy["category"] = "Supply"
                    elif any(word in message.lower() for word in ["complaint", "customer", "service"]):
                        parsed_data_copy["category"] = "Complaint"
                    else:
                        parsed_data_copy["category"] = "Other"
            
            elif entry_type == EntryType.ISSUE:
                # Check if it should actually be fuel, expense, or task
                if self.is_fuel_message(message) and any(word in message.lower() for word in ["liters", "used", "gave", "refueled"]):
                    entry_type = EntryType.FUEL
                    # Try to extract fuel info
                    if "hilux" in message.lower():
                        parsed_data_copy["vehicle"] = "Toyota Hilux"
                    elif "prado" in message.lower():
                        parsed_data_copy["vehicle"] = "Toyota Prado"
                    else:
                        parsed_data_copy["vehicle"] = "Other"
                    
                    # Extract liters if present
                    import re
                    liters_match = re.search(r'(\d+)\s*liters?', message.lower())
                    if liters_match:
                        parsed_data_copy["liters"] = float(liters_match.group(1))
                
                elif self.is_expense_message(message):
                    entry_type = EntryType.EXPENSE
                
                elif self.is_task_message(message):
                    entry_type = EntryType.TASK
                    # Try to extract task info
                    if "assign" in message.lower():
                        # Extract assignment
                        import re
                        assign_match = re.search(r'assign\s+(\w+)', message.lower())
                        if assign_match:
                            parsed_data_copy["assigned_to"] = assign_match.group(1).title()
                        else:
                            parsed_data_copy["assigned_to"] = "Nthambi"
                    
                    # Extract deadline
                    if "friday" in message.lower():
                        parsed_data_copy["deadline"] = "2025-08-08"
                    elif "next week" in message.lower():
                        parsed_data_copy["deadline"] = "2025-08-11"
                    elif "monday" in message.lower():
                        parsed_data_copy["deadline"] = "2025-08-11"
                    elif "tuesday" in message.lower():
                        parsed_data_copy["deadline"] = "2025-08-12"
                    elif "wednesday" in message.lower():
                        parsed_data_copy["deadline"] = "2025-08-13"
                    elif "thursday" in message.lower():
                        parsed_data_copy["deadline"] = "2025-08-14"
                    elif "saturday" in message.lower():
                        parsed_data_copy["deadline"] = "2025-08-09"
                    elif "sunday" in message.lower():
                        parsed_data_copy["deadline"] = "2025-08-10"
                
                # If it's still an issue but missing description, try to extract from task_title or create one
                if entry_type == EntryType.ISSUE and not parsed_data_copy.get("description"):
                    if parsed_data_copy.get("task_title"):
                        parsed_data_copy["description"] = parsed_data_copy["task_title"]
                        del parsed_data_copy["task_title"]
                    else:
                        # Create a basic description from the message
                        parsed_data_copy["description"] = message.strip()
            
            elif entry_type == EntryType.TASK:
                # Check if it should actually be an issue
                if self.is_issue_message(message):
                    entry_type = EntryType.ISSUE
                    # Try to extract issue info
                    if "urgent" in message.lower() or "critical" in message.lower() or "emergency" in message.lower():
                        parsed_data_copy["severity"] = "High"
                    elif "important" in message.lower() or "priority" in message.lower():
                        parsed_data_copy["severity"] = "Medium"
                    else:
                        parsed_data_copy["severity"] = "Low"
                    
                    # Determine category
                    if any(word in message.lower() for word in ["equipment", "machine", "compressor", "generator"]):
                        parsed_data_copy["category"] = "Equipment"
                    elif any(word in message.lower() for word in ["fuel", "supply", "material"]):
                        parsed_data_copy["category"] = "Other"
                    elif any(word in message.lower() for word in ["complaint", "customer", "service"]):
                        parsed_data_copy["category"] = "Complaint"
                    else:
                        parsed_data_copy["category"] = "Other"
            
            entry = ParsedEntry(type=entry_type, **parsed_data_copy)
            
            logger.info(f"Successfully parsed message: {entry}")
            return entry
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    def validate_parsed_entry(self, entry: ParsedEntry) -> bool:
        """Validate that a parsed entry has required fields."""
        if entry.type == EntryType.EXPENSE:
            return entry.amount is not None and entry.description is not None
        elif entry.type == EntryType.FUEL:
            return entry.vehicle is not None and entry.liters is not None
        elif entry.type == EntryType.TASK:
            return entry.task_title is not None
        elif entry.type == EntryType.ISSUE:
            # For issues, we can use either description or task_title (if it was misclassified)
            return entry.description is not None or entry.task_title is not None
        return False
    
    def is_fuel_message(self, message: str) -> bool:
        """Check if a message is likely about fuel."""
        fuel_keywords = ['liters', 'fuel', 'diesel', 'petrol', 'gas', 'hilux', 'prado', 'vehicle', 'car']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in fuel_keywords)
    
    def is_expense_message(self, message: str) -> bool:
        """Check if a message is likely about expenses."""
        expense_keywords = ['spent', 'paid', 'cost', 'mwk', 'money', 'cash', 'expense']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in expense_keywords)
    
    def is_task_message(self, message: str) -> bool:
        """Check if a message is likely about tasks."""
        task_keywords = ['assign', 'task', 'todo', 'deadline', 'prepare', 'inspect', 'check', 'review', 'complete', 'finish']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in task_keywords)
    
    def is_issue_message(self, message: str) -> bool:
        """Check if a message is likely about issues."""
        issue_keywords = ['problem', 'issue', 'broken', 'malfunction', 'urgent', 'critical', 'emergency', 'complaint', 'fault']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in issue_keywords)
    
    def generate_confirmation_message(self, entry: ParsedEntry) -> str:
        """Generate a confirmation message for the user."""
        if entry.type == EntryType.EXPENSE:
            return f"Logged expense: {entry.amount:,.0f} MWK for {entry.description}."
        elif entry.type == EntryType.FUEL:
            return f"Logged fuel: {entry.liters}L for {entry.vehicle} ({entry.driver})."
        elif entry.type == EntryType.TASK:
            return f"Logged task: {entry.task_title} (Status: {entry.status or 'To Do'})."
        elif entry.type == EntryType.ISSUE:
            # Use description if available, otherwise use task_title (for misclassified entries)
            description = entry.description or entry.task_title or "No description"
            return f"Logged issue: {description} (Severity: {entry.severity or 'Low'})."
        return "Entry logged successfully."
    
    def generate_multiple_confirmation_message(self, entries: list[ParsedEntry], record_ids: list[str]) -> str:
        """Generate a confirmation message for multiple entries."""
        if not entries:
            return "❌ No entries were successfully processed."
        
        if len(entries) == 1:
            # Single entry, use regular confirmation
            return f"✅ {self.generate_confirmation_message(entries[0])} (Record ID: {record_ids[0]})"
        
        # Multiple entries
        confirmation_parts = [f"✅ Successfully logged {len(entries)} entries:"]
        
        for i, (entry, record_id) in enumerate(zip(entries, record_ids), 1):
            entry_type_emoji = {
                EntryType.EXPENSE: "💰",
                EntryType.FUEL: "⛽",
                EntryType.TASK: "📋",
                EntryType.ISSUE: "⚠️"
            }.get(entry.type, "📝")
            
            if entry.type == EntryType.EXPENSE:
                summary = f"{entry_type_emoji} {entry.amount:,.0f} MWK - {entry.description}"
            elif entry.type == EntryType.FUEL:
                summary = f"{entry_type_emoji} {entry.liters}L - {entry.vehicle}"
            elif entry.type == EntryType.TASK:
                summary = f"{entry_type_emoji} {entry.task_title}"
            elif entry.type == EntryType.ISSUE:
                description = entry.description or entry.task_title or "No description"
                summary = f"{entry_type_emoji} {description}"
            else:
                summary = f"{entry_type_emoji} {entry.type.value}"
            
            confirmation_parts.append(f"{i}. {summary} (ID: {record_id})")
        
        return "\n".join(confirmation_parts)

# Global parser instance (to be initialized with API key)
parser: Optional[GPTParser] = None 