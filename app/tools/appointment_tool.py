"""Appointment management tool for scheduling, booking, and managing appointments."""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from langchain_core.tools import Tool, BaseTool
import spacy
from pydantic import PrivateAttr

from app.tools.database_client import DatabaseClient
from app.tools.tool_config import (
    APPOINTMENT_SERVICE_TYPES,
    CANCELLATION_KEYWORDS,
    SPACY_MODEL_NAME,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES
)

logger = logging.getLogger(__name__)

NAME: str = "appointment_management" 
DESCRIPTION: str = "Manage appointments: search availability, book new, reschedule, cancel, and view appointments"

class AppointmentTool(BaseTool):
    """Tool for managing appointments with full CRUD operations."""
    
    name: str = "appointment_management"
    description: str = "Manage appointments: search availability, book new, reschedule, cancel, and view appointments"
  
    def __init__(self, **kwargs):
        """Initialize the appointment management tool."""
        # Initialize database client & SpaCy NER model
        db_client = DatabaseClient()
        try:
            ner = spacy.load(SPACY_MODEL_NAME)
        except OSError:
            logger.warning(f"Could not load SpaCy model '{SPACY_MODEL_NAME}'. Name extraction will be disabled.")
            ner = None
    
        def appointment_tool(query: str, user_name: str = "", user_email: str = "") -> str:
            """
            Execute appointment management based on query.
            
            Args:
                query: Natural language query about appointments
                user_name: User's full name (required for booking/modifying)
                user_email: User's email (required for booking/modifying)
                
            Returns:
                Formatted string with appointment results or status
            """
            try:
                # Detect the type of appointment operation
                operation = _detect_operation(query)
                
                if operation == "search_availability":
                    return _handle_availability_search(query, db_client, ner)
                elif operation == "book": # create new appointment
                    return _handle_new_booking(query, user_name, user_email, db_client, ner)
                elif operation == "view": # read appointments
                    return _handle_view_appointments(query, user_email, db_client)
                elif operation == "cancel": # delete appointment
                    return _handle_cancellation(query, user_email, db_client)
                elif operation == "reschedule": # update existing appointment
                    return _handle_reschedule(query, user_email, db_client)
                else:
                    # Default to availability search
                    return _handle_availability_search(query, db_client, ner)
                    
            except Exception as e:
                logger.error(f"Error during appointment management: {e}")
                return f"Error managing appointments: {str(e)}"
        
        super().__init__(
            name=NAME,
            description=DESCRIPTION,
            func=appointment_tool,
            **kwargs
        )

def _detect_operation(query: str) -> str:
    """Detect what type of appointment operation is requested."""
    query_lower = query.lower()
    
    # New booking keywords
    if any(word in query_lower for word in ["book", "schedule", "make appointment", "create appointment", "reserve", "set up", "new appointment", "create new"]):
        return "book"
    
    # Cancellation keywords
    elif any(word in query_lower for word in ["cancel", "delete", "remove appointment", "terminate", "end appointment"]):
        return "cancel"
    
    # Rescheduling keywords
    elif any(word in query_lower for word in ["reschedule", "change", "move appointment", "update"]):
        return "reschedule"
    
    # View appointments keywords
    elif any(word in query_lower for word in ["my appointments", "view appointments", "show appointments", "list appointments"]):
        return "view"
    
    # Default to availability search
    else:
        return "search_availability"

def _handle_availability_search(query: str, db_client: DatabaseClient, ner) -> str:
    """Handle availability search requests."""
    try:
        # Extract date range from query
        date_range = _extract_date_range(query)
        
        # Extract service type and provider filters
        service_filter = _extract_service_filter(query)
        provider_filter = _extract_provider_filter(query, ner)
        
        # Build filters
        filters = {"status": "available"}
        if service_filter:
            filters["service_type"] = {"$regex": service_filter, "$options": "i"}
        if provider_filter:
            filters["provider"] = {"$regex": provider_filter, "$options": "i"}
        
        # Search available appointments
        results = db_client.search_appointments(
            date_range=date_range,
            filters=filters,
            limit=10
        )
        
        if not results:
            date_desc = "the requested time period" if date_range else "in the near future"
            return f"No available appointments found for {date_desc}."
        
        return _format_availability_results(results)
        
    except Exception as e:
        logger.error(f"Error searching availability: {e}")
        return f"Error searching availability: {str(e)}"

def _handle_new_booking(query: str, user_name: str, user_email: str, db_client: DatabaseClient, ner) -> str:
    """Handle appointment booking requests."""
    if not user_name or not user_email:
        return ERROR_MESSAGES["missing_user_info"]
    
    try:
        # Extract appointment details from query
        date, time = _extract_date_time(query)
        service_type = _extract_service_filter(query) or "consultation"
        provider = _extract_provider_filter(query, ner)
        notes = _extract_notes(query)
        
        if not date or not time:
            return "Please specify the date and time for your appointment (e.g., 'tomorrow at 2pm' or 'January 15th at 10:30am')."
        
        # Check availability first
        is_available = db_client.check_availability(
            date=date,
            time=time,
            provider=provider
        )
        
        if not is_available:
            return f"Unfortunately, {date} at {time} is not available. Please check available slots and choose a different time."
        
        # Create the appointment
        appointment_id = db_client.create_appointment(
            user_name=user_name,
            user_email=user_email,
            date=date,
            time=time,
            service_type=service_type,
            provider=provider,
            notes=notes
        )
        
        if appointment_id:
            provider_info = f" with {provider}" if provider else ""
            return f"✅ Appointment booked successfully!\n\nDetails:\n- Date: {date}\n- Time: {time}\n- Service: {service_type}{provider_info}\n- Confirmation ID: {appointment_id[:8]}"
        else:
            return "Failed to book the appointment. Please try again or contact support."
            
    except Exception as e:
        logger.error(f"Error booking appointment: {e}")
        return f"Error booking appointment: {str(e)}"

def _handle_view_appointments(query: str, user_email: str, db_client: DatabaseClient) -> str:
    """Handle viewing user's appointments."""
    if not user_email:
        return "To view your appointments, I need your email address."
    
    try:
        # Extract status filter if specified
        status_filter = None
        if "upcoming" in query.lower() or "booked" in query.lower():
            status_filter = "booked"
        elif "cancelled" in query.lower():
            status_filter = "cancelled"
        
        appointments = db_client.get_user_appointments(
            user_email=user_email,
            status_filter=status_filter,
            limit=10
        )
        
        if not appointments:
            status_desc = f" {status_filter}" if status_filter else ""
            return f"No{status_desc} appointments found for your account."
        
        return _format_user_appointments(appointments)
        
    except Exception as e:
        logger.error(f"Error viewing appointments: {e}")
        return f"Error viewing appointments: {str(e)}"

def _handle_cancellation(query: str, user_email: str, db_client: DatabaseClient) -> str:
    """Handle appointment cancellation requests."""
    if not user_email:
        return "To cancel an appointment, I need your email address."
    
    try:
        # Extract appointment ID or date/time
        appointment_id = _extract_appointment_id(query)
        reason = _extract_cancellation_reason(query)
        
        if appointment_id:
            success = db_client.cancel_appointment(
                appointment_id=appointment_id,
                user_email=user_email,
                reason=reason
            )
            
            if success:
                return f"✅ Appointment {appointment_id[:8]} has been cancelled successfully."
            else:
                return f"Could not cancel appointment {appointment_id[:8]}. Please check the ID and try again."
        else:
            return "Please provide the appointment ID to cancel (e.g., 'cancel appointment ABC12345')."
            
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return f"Error cancelling appointment: {str(e)}"

def _handle_reschedule(query: str, user_email: str, db_client: DatabaseClient) -> str:
    """Handle appointment rescheduling requests."""
    if not user_email:
        return "To reschedule an appointment, I need your email address."
    
    try:
        # Extract appointment ID and new date/time
        appointment_id = _extract_appointment_id(query)
        new_date, new_time = _extract_date_time(query)
        
        if not appointment_id:
            return "Please provide the appointment ID to reschedule (e.g., 'reschedule appointment ABC12345 to tomorrow at 3pm')."
        
        if not new_date or not new_time:
            return "Please specify the new date and time for your appointment."
        
        # Check availability for new slot
        is_available = db_client.check_availability(
            date=new_date,
            time=new_time
        )
        
        if not is_available:
            return f"Unfortunately, {new_date} at {new_time} is not available. Please choose a different time."
        
        # Update the appointment
        success = db_client.update_appointment(
            appointment_id=appointment_id,
            user_email=user_email,
            updates={
                "date": new_date,
                "time": new_time
            }
        )
        
        if success:
            return f"✅ Appointment {appointment_id[:8]} has been rescheduled to {new_date} at {new_time}."
        else:
            return f"Could not reschedule appointment {appointment_id[:8]}. Please check the ID and try again."
            
    except Exception as e:
        logger.error(f"Error rescheduling appointment: {e}")
        return f"Error rescheduling appointment: {str(e)}"

def _extract_date_range(query: str) -> Optional[Dict[str, str]]:
    """Extract date range from natural language query."""
    today = datetime.now()
    query_lower = query.lower()
    
    if "today" in query_lower:
        date_str = today.strftime("%Y-%m-%d")
        return {"start": date_str, "end": date_str}
    elif "tomorrow" in query_lower:
        tomorrow = today + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")
        return {"start": date_str, "end": date_str}
    elif "next week" in query_lower:
        start_date = today + timedelta(days=1)
        end_date = start_date + timedelta(days=7)
        return {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        }
    elif "this week" in query_lower:
        days_until_sunday = 6 - today.weekday()
        end_date = today + timedelta(days=days_until_sunday)
        return {
            "start": today.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        }
    
    return None

def _extract_date_time(query: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract specific date and time from query."""
    # This is a simplified implementation
    # In production, you'd want more sophisticated date/time parsing
    
    today = datetime.now()
    query_lower = query.lower()
    
    # Simple date extraction
    date = None
    if "today" in query_lower:
        date = today.strftime("%Y-%m-%d")
    elif "tomorrow" in query_lower:
        date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Simple time extraction
    time = None
    time_patterns = [
        r"(\d{1,2}):(\d{2})\s*(am|pm)",
        r"(\d{1,2})\s*(am|pm)",
        r"(\d{1,2}):(\d{2})"
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, query_lower)
        if match:
            if len(match.groups()) == 3:  # HH:MM AM/PM
                hour, minute, period = match.groups()
                hour = int(hour)
                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                time = f"{hour:02d}:{minute}"
            elif len(match.groups()) == 2:  # HH AM/PM or HH:MM
                if match.groups()[1] in ["am", "pm"]:  # HH AM/PM
                    hour, period = match.groups()
                    hour = int(hour)
                    if period == "pm" and hour != 12:
                        hour += 12
                    elif period == "am" and hour == 12:
                        hour = 0
                    time = f"{hour:02d}:00"
                else:  # HH:MM
                    hour, minute = match.groups()
                    time = f"{hour.zfill(2)}:{minute}"
            break
    
    return date, time

def _extract_service_filter(query: str) -> Optional[str]:
    """Extract service type from query."""
    query_lower = query.lower()

    for service in APPOINTMENT_SERVICE_TYPES:
        if service in query_lower:
            return service
    
    return None

def _extract_provider_filter(query: str, ner: Optional[Any]) -> Optional[str]:
    """Extract provider name from query."""
    if not ner:
        logger.warning("SpaCy model not available for name extraction")
        return None
        
    try:
        doc = ner(query)
        names = []
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                names.append(ent.text)

        match = ", ".join(names)
        if match:
            return match
        
        return None
    
    except Exception as e:
        logger.warning(f"NER extraction failed: {e}")
        return None

def _extract_notes(query: str) -> Optional[str]:
    """Extract any notes or special requests from query."""
    notes_patterns = [
        r"note[s]?:\s*(.+)",
        r"special request[s]?:\s*(.+)",
        r"mention:\s*(.+)"
    ]
    
    for pattern in notes_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def _extract_appointment_id(query: str) -> Optional[str]:
    """Extract appointment ID from query."""
    # Enhanced patterns for various ID formats
    id_patterns = [
        r"appointment\s+([a-zA-Z0-9]{6,24})",           # appointment ABC123456
        r"id:?\s*([a-zA-Z0-9]{6,24})",                  # id: ABC123 or ID ABC123
        r"confirmation\s+([a-zA-Z0-9]{6,24})",          # confirmation ABC123
        r"reference\s+([a-zA-Z0-9]{6,24})",             # reference ABC123
        r"booking\s+([a-zA-Z0-9]{6,24})",               # booking ABC123
        r"#([a-zA-Z0-9]{6,24})",                        # #ABC123
        r"([a-fA-F0-9]{24})",                           # MongoDB ObjectId (24 hex chars)
        r"([a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12})",  # UUID format
        r"([A-Z]{2,3}\d{4,8})",                         # APPT12345, REF123456
    ]
    
    for pattern in id_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def _extract_cancellation_reason(query: str) -> Optional[str]:
    """Extract cancellation reason from query."""
    reason_patterns = [
        r"because\s+(.+?)(?:\.|$)",                     # because I'm sick.
        r"reason:?\s*(.+?)(?:\.|$)",                    # reason: emergency
        r"due\s+to\s+(.+?)(?:\.|$)",                    # due to illness
        r"since\s+(.+?)(?:\.|$)",                       # since I can't make it
        r"as\s+(.+?)(?:\.|$)",                          # as I have conflict
        r"note:?\s*(.+?)(?:\.|$)",                      # note: family emergency
        r"explanation:?\s*(.+?)(?:\.|$)",               # explanation: work conflict
        r"cancelled?\s+(?:because|due to|since)?\s*(.+?)(?:\.|$)",  # cancelled due to...
    ]

    for pattern in reason_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            reason = match.group(1).strip()
            # Clean up common artifacts
            reason = re.sub(r'^(of|that|I|we|the)\s+', '', reason, flags=re.IGNORECASE)
            if len(reason) > 3:  # Reasonable minimum length
                return reason

    # Fallback: look for common cancellation keywords
    query_lower = query.lower()
    for keyword, default_reason in CANCELLATION_KEYWORDS.items():
        if keyword in query_lower:
            return default_reason
    
    return "User requested cancellation"

def _format_availability_results(results: List[Dict[str, Any]]) -> str:
    """Format availability search results."""
    formatted_results = ["AVAILABLE APPOINTMENTS:"]
    
    for i, appointment in enumerate(results, 1):
        date = appointment.get('date', 'N/A')
        time = appointment.get('time', 'N/A')
        service_type = appointment.get('service_type', 'N/A')
        provider = appointment.get('provider', 'N/A')
        duration = appointment.get('duration', 60)
        
        appointment_info = (
            f"{i}. {date} at {time}\n"
            f"   Service: {service_type}\n"
            f"   Provider: {provider}\n"
            f"   Duration: {duration} minutes"
        )
        formatted_results.append(appointment_info)
    
    formatted_results.append("\nTo book any of these slots, please specify the date and time in your request.")
    return "\n\n".join(formatted_results)

def _format_user_appointments(appointments: List[Dict[str, Any]]) -> str:
    """Format user's appointments for display."""
    formatted_results = ["YOUR APPOINTMENTS:"]
    
    for i, appointment in enumerate(appointments, 1):
        date = appointment.get('date', 'N/A')
        time = appointment.get('time', 'N/A')
        service_type = appointment.get('service_type', 'N/A')
        provider = appointment.get('provider', 'N/A')
        status = appointment.get('status', 'N/A')
        appointment_id = appointment.get('_id', 'N/A')
        
        status_emoji = "✅" if status == "booked" else "❌" if status == "cancelled" else "⏳"
        
        appointment_info = (
            f"{i}. {status_emoji} {date} at {time}\n"
            f"   Service: {service_type}\n"
            f"   Provider: {provider}\n"
            f"   Status: {status}\n"
            f"   ID: {appointment_id[:8] if appointment_id != 'N/A' else 'N/A'}"
        )
        
        # Add cancellation info if cancelled
        if status == "cancelled":
            metadata = appointment.get('metadata', {})
            reason = metadata.get('cancellation_reason', 'No reason provided')
            appointment_info += f"\n   Cancellation reason: {reason}"
        
        formatted_results.append(appointment_info)
    
    return "\n\n".join(formatted_results)
