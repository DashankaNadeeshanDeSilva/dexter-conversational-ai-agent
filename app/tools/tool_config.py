"""Configuration constants for tools and application settings."""

from typing import List, Dict, Any

# ============================================================================
# APPOINTMENT TOOL CONSTANTS
# ============================================================================

# Service types available for appointments
APPOINTMENT_SERVICE_TYPES: List[str] = [
    "consultation",
    "checkup", 
    "meeting",
    "therapy",
    "treatment",
    "examination",
    "follow-up",
    "initial_visit",
    "routine_checkup",
    "emergency",
    "telehealth",
    "group_session",
    "screening",
    "diagnostic",
    "preventive_care",
    "specialist_referral"
]

# Default appointment duration in minutes
DEFAULT_APPOINTMENT_DURATION: int = 60

# Maximum appointments to return in search results
MAX_APPOINTMENT_RESULTS: int = 10

# Appointment status options
APPOINTMENT_STATUSES: List[str] = [
    "available",
    "booked", 
    "cancelled",
    "completed",
    "no_show",
    "rescheduled"
]

# Common cancellation reasons for auto-detection
CANCELLATION_KEYWORDS: Dict[str, str] = {
    "sick": "User is feeling unwell",
    "emergency": "Emergency situation",
    "conflict": "Schedule conflict", 
    "travel": "Travel conflict",
    "work": "Work obligations",
    "family": "Family matter",
    "weather": "Weather-related issue",
    "personal": "Personal reasons"
}

# ============================================================================
# PRODUCT SEARCH TOOL CONSTANTS
# ============================================================================

# Product categories for filtering
PRODUCT_CATEGORIES: List[str] = [
    "electronics",
    "clothing",
    "books",
    "toys",
    "sports",
    "health",
    "beauty",
    "home",
    "automotive",
    "garden",
    "jewelry",
    "music",
    "furniture",
    "kitchen",
    "outdoor"
]

# Product availability statuses
PRODUCT_AVAILABILITY_STATUSES: List[str] = [
    "in_stock",
    "out_of_stock", 
    "limited_stock",
    "pre_order",
    "discontinued"
]

# Maximum products to return in search results
MAX_PRODUCT_RESULTS: int = 10

# ============================================================================
# SEMANTIC RETRIEVAL CONSTANTS
# ============================================================================

# Default similarity threshold for semantic search
SEMANTIC_SIMILARITY_THRESHOLD: float = 0.7

# Maximum semantic search results
MAX_SEMANTIC_RESULTS: int = 5

# ============================================================================
# GENERAL TOOL CONSTANTS
# ============================================================================

# Maximum results for general searches
DEFAULT_MAX_RESULTS: int = 5

# Timeout settings (in seconds)
TOOL_TIMEOUT_SECONDS: int = 30

# SpaCy model name for NER
SPACY_MODEL_NAME: str = "en_core_web_sm"

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES: Dict[str, str] = {
    "missing_user_info": "Please provide your name and email address.",
    "missing_appointment_id": "Please provide the appointment ID.",
    "missing_date_time": "Please specify the date and time.",
    "appointment_not_available": "The requested time slot is not available.",
    "appointment_not_found": "Appointment not found or you don't have permission to access it.",
    "spacy_load_error": "Could not load NLP model for name extraction.",
    "database_connection_error": "Database connection error. Please try again.",
    "invalid_date_format": "Invalid date format. Please use a clear date format.",
    "invalid_time_format": "Invalid time format. Please use format like '2:30pm' or '14:30'."
}

# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_MESSAGES: Dict[str, str] = {
    "appointment_booked": "✅ Appointment booked successfully!",
    "appointment_cancelled": "✅ Appointment cancelled successfully.",
    "appointment_rescheduled": "✅ Appointment rescheduled successfully.",
    "appointment_updated": "✅ Appointment updated successfully."
}

# ============================================================================
# DATABASE COLLECTION NAMES
# ============================================================================

DB_COLLECTIONS: Dict[str, str] = {
    "products": "products",
    "appointments": "appointments",
    "users": "users",
    "sessions": "sessions"
}

# ============================================================================
# VALIDATION RULES
# ============================================================================

VALIDATION_RULES: Dict[str, Any] = {
    "appointment_id_min_length": 6,
    "appointment_id_max_length": 24,
    "reason_min_length": 3,
    "reason_max_length": 500,
    "name_min_length": 2,
    "name_max_length": 100,
    "email_pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
}
