"""Appointment management tool for scheduling, booking, and managing appointments."""

import logging
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun

from app.tools.database_client import DatabaseClient
from app.tools.tool_config import (
    APPOINTMENT_SERVICE_TYPES,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES
)

logger = logging.getLogger(__name__)

# Initialize database client
try:
    _DB_CLIENT = DatabaseClient()
except Exception as e:
    logger.error(f"Failed to initialize appointment database at import: {e}")
    _DB_CLIENT = None

class AppointmentInput(BaseModel):
    """Input schema for appointment operations."""
    operation: str = Field(..., description="Operation type: 'book', 'cancel', 'reschedule', 'view', or 'search_availability'")
    user_email: str = Field(..., description="User's email address")
    user_name: Optional[str] = Field(None, description="User's name (required for booking)")
    date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format (required for booking/rescheduling)")
    time: Optional[str] = Field(None, description="Time in HH:MM format (required for booking/rescheduling)")
    service_type: Optional[str] = Field(None, description="Type of service (required for booking)")
    provider: Optional[str] = Field(None, description="Provider name (optional)")
    appointment_id: Optional[str] = Field(None, description="Appointment ID (required for cancel/reschedule)")
    status_filter: Optional[str] = Field(None, description="Status filter for viewing appointments (optional)")

class AppointmentTool(BaseTool):
    """Tool for managing appointments with full CRUD operations.
    
    Required information for each operation:
    - book: user_email, user_name, date, time, service_type (optional: provider)
    - cancel: user_email, appointment_id
    - reschedule: user_email, appointment_id, date, time
    - view: user_email (optional: status_filter)
    - search_availability: user_email (optional: date, service_type, provider)
    
    The agent should collect all required information before running operations in the tool.
    """
    
    name: str = "appointment_management"
    description: str = (
        "Manage appointments: book new appointments, cancel existing ones, reschedule, view user appointments, "
        "and search for available slots. Required fields: book (user_email, user_name, date, time, service_type), "
        "cancel (user_email, appointment_id), reschedule (user_email, appointment_id, date, time), "
        "view (user_email, optional: status_filter), search_availability (user_email, optional: date, service_type, provider). "
        "Always provide user_email."
    )
    args_schema: Type[BaseModel] = AppointmentInput

    def _run(
        self, 
        operation: str, 
        user_email: str, 
        user_name: str = "", 
        date: str = "", 
        time: str = "", 
        service_type: str = "", 
        provider: str = "", 
        appointment_id: str = "", 
        status_filter: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute appointment management operation."""
        try:
            if _DB_CLIENT is None:
                return "Appointment Database is not available right now."

            # Validate required fields based on operation
            validation_result = self._validate_operation_fields(
                operation, user_email, user_name, date, time, service_type, appointment_id
            )
            if not validation_result["valid"]:
                return validation_result["message"]

            # Execute the operation
            if operation == "book":
                return self._execute_booking(user_email, user_name, date, time, service_type, provider)
            elif operation == "cancel":
                return self._execute_cancellation(user_email, appointment_id)
            elif operation == "reschedule":
                return self._execute_reschedule(user_email, appointment_id, date, time)
            elif operation == "view":
                return self._execute_view_appointments(user_email, status_filter)
            elif operation == "search_availability":
                return self._execute_availability_search(date, service_type, provider)
            else:
                return f"Unknown operation: {operation}. Supported operations: book, cancel, reschedule, view, search_availability"
                
        except Exception as e:
            logger.error(f"Error during appointment management: {e}")
            return f"Error managing appointments: {str(e)}"

    def _validate_operation_fields(
        self, 
        operation: str, 
        user_email: str, 
        user_name: str, 
        date: str, 
        time: str, 
        service_type: str, 
        appointment_id: str
    ) -> Dict[str, Any]:
        """Validate that all required fields are provided for the operation.
        Uses configuration-driven validation with field mapping."""
        
        # Centralized validation configuration
        VALIDATION_CONFIG = {
            "book": {
                "required": ["user_email", "user_name", "date", "time", "service_type"],
                "field_labels": {
                    "user_name": "name",
                    "date": "date", 
                    "time": "time",
                    "service_type": "service type"
                }
            },
            "cancel": {
                "required": ["user_email", "appointment_id"],
                "field_labels": {"appointment_id": "appointment ID"}
            },
            "reschedule": {
                "required": ["user_email", "appointment_id", "date", "time"],
                "field_labels": {
                    "appointment_id": "appointment ID",
                    "date": "new date",
                    "time": "new time"
                }
            },
            "view": {
                "required": ["user_email"], 
                "field_labels": {}
            },
            "search_availability": {
                "required": ["user_email"], 
                "field_labels": {}
            }
        }
        
        if operation not in VALIDATION_CONFIG:
            return {"valid": False, "message": f"Unknown operation: {operation}"}
        
        # Create field value mapping
        field_values = {
            "user_email": user_email,
            "user_name": user_name,
            "date": date,
            "time": time,
            "service_type": service_type,
            "appointment_id": appointment_id
        }
        
        # Validate required fields
        config = VALIDATION_CONFIG[operation]
        missing_fields = [
            config["field_labels"].get(field, field) 
            for field in config["required"] 
            if not field_values.get(field)
        ]
        
        if missing_fields:
            field_list = ", ".join(missing_fields)
            return {
                "valid": False, 
                "message": f"To {operation} your appointment, I need: {field_list}"
            }
        
        return {"valid": True, "message": "Validation passed"}

    def _execute_booking(
        self, 
        user_email: str, 
        user_name: str, 
        date: str, 
        time: str, 
        service_type: str, 
        provider: str
    ) -> str:
        """Execute appointment booking."""
        try:
            # Check availability
            is_available = _DB_CLIENT.check_availability(
                date=date,
                time=time,
                provider=provider
            )
            
            if not is_available:
                return f"Unfortunately, {date} at {time} is not available. Please check available slots and choose a different time."
            
            # Create the appointment
            appointment_id = _DB_CLIENT.create_appointment(
                user_name=user_name,
                user_email=user_email,
                date=date,
                time=time,
                service_type=service_type,
                provider=provider
            )
            
            if appointment_id:
                provider_info = f" with {provider}" if provider else ""
                return f"✅ Appointment booked successfully!\n\nDetails:\n- Date: {date}\n- Time: {time}\n- Service: {service_type}{provider_info}\n- Confirmation ID: {appointment_id[:8]}"
            else:
                return "Failed to book the appointment. Please try again or contact support."
                
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return f"Error booking appointment: {str(e)}"

    def _execute_cancellation(self, user_email: str, appointment_id: str) -> str:
        """Execute appointment cancellation."""
        try:
            success = _DB_CLIENT.cancel_appointment(
                appointment_id=appointment_id,
                user_email=user_email
            )
            
            if success:
                return f"✅ Appointment {appointment_id[:8]} has been cancelled successfully."
            else:
                return f"Could not cancel appointment {appointment_id[:8]}. Please check the ID and try again."
                
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return f"Error cancelling appointment: {str(e)}"

    def _execute_reschedule(self, user_email: str, appointment_id: str, date: str, time: str) -> str:
        """Execute appointment rescheduling."""
        try:
            # Check availability for new slot
            is_available = _DB_CLIENT.check_availability(
                date=date,
                time=time
            )
            
            if not is_available:
                return f"Unfortunately, {date} at {time} is not available. Please choose a different time."
            
            # Update the appointment
            success = _DB_CLIENT.update_appointment(
                appointment_id=appointment_id,
                user_email=user_email,
                updates={"date": date, "time": time}
            )
            
            if success:
                return f"✅ Appointment {appointment_id[:8]} has been rescheduled to {date} at {time}."
            else:
                return f"Could not reschedule appointment {appointment_id[:8]}. Please check the ID and try again."
                
        except Exception as e:
            logger.error(f"Error rescheduling appointment: {e}")
            return f"Error rescheduling appointment: {str(e)}"

    def _execute_view_appointments(self, user_email: str, status_filter: str = "") -> str:
        """Execute viewing user appointments."""
        try:
            appointments = _DB_CLIENT.get_user_appointments(
                user_email=user_email,
                status_filter=status_filter if status_filter else None,
                limit=10
            )
            
            if not appointments:
                status_desc = f" {status_filter}" if status_filter else ""
                return f"No{status_desc} appointments found for your account."
            
            return self._format_user_appointments(appointments)
            
        except Exception as e:
            logger.error(f"Error viewing appointments: {e}")
            return f"Error viewing appointments: {str(e)}"

    def _execute_availability_search(self, date: str = "", service_type: str = "", provider: str = "") -> str:
        """Execute availability search."""
        try:
            # Build filters - all fields are optional for search
            filters = {"status": "available"}
            
            if service_type:
                filters["service_type"] = {"$regex": service_type, "$options": "i"}
            if provider:
                filters["provider"] = {"$regex": provider, "$options": "i"}
            
            # Search available appointments
            # Note: date is now optional, so we handle it differently
            date_filter = None
            if date:
                date_filter = {"date": date}
            
            results = _DB_CLIENT.search_appointments(
                date_range=date_filter,
                filters=filters,
                limit=10
            )
            
            if not results:
                if date:
                    return f"No available appointments found for {date}."
                else:
                    return "No available appointments found in the near future."
            
            return self._format_availability_results(results)
            
        except Exception as e:
            logger.error(f"Error searching availability: {e}")
            return f"Error searching availability: {str(e)}"

    def _format_availability_results(self, results: List[Dict[str, Any]]) -> str:
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

    def _format_user_appointments(self, appointments: List[Dict[str, Any]]) -> str:
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