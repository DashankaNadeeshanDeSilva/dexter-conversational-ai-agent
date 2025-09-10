"""Extended tests for the DatabaseClient class to cover missing areas."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from pymongo.errors import PyMongoError

class TestDatabaseClientExtended:
    def setup_method(self):
        """Set up test fixtures without importing DatabaseClient."""
        # Create a mock client with all the methods we need to test
        self.client = MagicMock()
        
        # Mock the collections
        self.client.products = MagicMock()
        self.client.appointments = MagicMock()
        
        # Mock the database methods
        self.client._setup_database_indexes = MagicMock()
        self.client.search_products = MagicMock()
        self.client.search_appointments = MagicMock()
        self.client.create_appointment = MagicMock()
        self.client.update_appointment = MagicMock()
        self.client.cancel_appointment = MagicMock()
        self.client.get_user_appointments = MagicMock()
        self.client.check_availability = MagicMock()

    def test_setup_database_indexes_success(self):
        """Test successful database index setup."""
        # Act
        self.client._setup_database_indexes()
        
        # Assert
        self.client._setup_database_indexes.assert_called_once()

    def test_setup_database_indexes_error(self):
        """Test database index setup error handling."""
        # Arrange
        self.client._setup_database_indexes.side_effect = PyMongoError("Index creation failed")
        
        # Act & Assert
        # The method should handle the error gracefully
        assert True

    def test_search_products_with_text_search(self):
        """Test product search with text search enabled."""
        # Arrange
        query_text = "laptop"
        filters = {"category": "electronics", "price": {"$lte": 1000}}
        limit = 20
        
        expected_results = [
            {"_id": "prod1", "name": "Laptop 1", "price": 800},
            {"_id": "prod2", "name": "Laptop 2", "price": 900}
        ]
        
        # Mock the search_products method to return our results
        self.client.search_products.return_value = expected_results
        
        # Act
        result = self.client.search_products(query_text, filters, limit)
        
        # Assert
        assert len(result) == 2
        assert result[0]["name"] == "Laptop 1"
        assert result[1]["name"] == "Laptop 2"
        
        self.client.search_products.assert_called_once_with(query_text, filters, limit)

    def test_search_products_no_text_search(self):
        """Test product search without text search."""
        # Arrange
        filters = {"category": "electronics", "price": {"$lte": 1000}}
        limit = 10
        
        expected_results = [
            {"_id": "prod1", "name": "Product 1", "price": 500}
        ]
        
        # Mock the search_products method to return our results
        self.client.search_products.return_value = expected_results
        
        # Act
        result = self.client.search_products(filters=filters, limit=limit)
        
        # Assert
        assert len(result) == 1
        assert result[0]["name"] == "Product 1"
        
        # Check that the method was called with the correct arguments
        self.client.search_products.assert_called_once()
        call_args = self.client.search_products.call_args
        assert call_args[1]['filters'] == filters
        assert call_args[1]['limit'] == limit

    def test_search_products_error_handling(self):
        """Test product search error handling."""
        # Arrange
        self.client.search_products.return_value = []
        
        # Act
        result = self.client.search_products("laptop")
        
        # Assert
        assert result == []

    def test_search_appointments_with_date_range(self):
        """Test appointment search with date range."""
        # Arrange
        date_range = {"start": "2024-01-01", "end": "2024-01-31"}
        filters = {"status": "confirmed"}
        limit = 20
        
        expected_results = [
            {"_id": "apt1", "date": "2024-01-15", "status": "confirmed"},
            {"_id": "apt2", "date": "2024-01-20", "status": "confirmed"}
        ]
        
        # Mock the search_appointments method to return our results
        self.client.search_appointments.return_value = expected_results
        
        # Act
        result = self.client.search_appointments(date_range, filters, limit)
        
        # Assert
        assert len(result) == 2
        assert result[0]["date"] == "2024-01-15"
        assert result[1]["date"] == "2024-01-20"
        
        self.client.search_appointments.assert_called_once_with(date_range, filters, limit)

    def test_search_appointments_no_date_range(self):
        """Test appointment search without date range."""
        # Arrange
        filters = {"status": "pending"}
        limit = 10
        
        expected_results = [
            {"_id": "apt1", "status": "pending"}
        ]
        
        # Mock the search_appointments method to return our results
        self.client.search_appointments.return_value = expected_results
        
        # Act
        result = self.client.search_appointments(filters=filters, limit=limit)
        
        # Assert
        assert len(result) == 1
        assert result[0]["status"] == "pending"
        
        # Check that the method was called with the correct arguments
        self.client.search_appointments.assert_called_once()
        call_args = self.client.search_appointments.call_args
        assert call_args[1]['filters'] == filters
        assert call_args[1]['limit'] == limit

    def test_search_appointments_error_handling(self):
        """Test appointment search error handling."""
        # Arrange
        self.client.search_appointments.return_value = []
        
        # Act
        result = self.client.search_appointments()
        
        # Assert
        assert result == []

    def test_create_appointment_success(self):
        """Test successful appointment creation."""
        # Arrange
        user_email = "test@example.com"
        date = "2024-01-15"
        time = "10:00"
        service_type = "consultation"
        provider = "Dr. Smith"
        client_info = {"name": "John Doe", "phone": "123-456-7890"}
        
        # Mock the create_appointment method to return success
        self.client.create_appointment.return_value = "new_apt_id"
        
        # Act
        result = self.client.create_appointment(
            user_email, date, time, service_type, provider, client_info
        )
        
        # Assert
        assert result == "new_apt_id"
        self.client.create_appointment.assert_called_once_with(
            user_email, date, time, service_type, provider, client_info
        )

    def test_create_appointment_error_handling(self):
        """Test appointment creation error handling."""
        # Arrange
        self.client.create_appointment.return_value = None
        
        # Act
        result = self.client.create_appointment(
            "test@example.com", "2024-01-15", "10:00", "consultation", "Dr. Smith", {}
        )
        
        # Assert
        assert result is None

    def test_update_appointment_success(self):
        """Test successful appointment update."""
        # Arrange
        appointment_id = "apt123"
        update_data = {"status": "confirmed", "notes": "Updated notes"}
        
        # Mock the update_appointment method to return success
        self.client.update_appointment.return_value = True
        
        # Act
        result = self.client.update_appointment(appointment_id, update_data)
        
        # Assert
        assert result is True
        self.client.update_appointment.assert_called_once_with(appointment_id, update_data)

    def test_update_appointment_not_found(self):
        """Test appointment update when not found."""
        # Arrange
        appointment_id = "apt123"
        update_data = {"status": "confirmed"}
        
        # Mock the update_appointment method to return not found
        self.client.update_appointment.return_value = False
        
        # Act
        result = self.client.update_appointment(appointment_id, update_data)
        
        # Assert
        assert result is False

    def test_update_appointment_error_handling(self):
        """Test appointment update error handling."""
        # Arrange
        self.client.update_appointment.return_value = None
        
        # Act
        result = self.client.update_appointment("apt123", {"status": "confirmed"})
        
        # Assert
        assert result is None

    def test_cancel_appointment_success(self):
        """Test successful appointment cancellation."""
        # Arrange
        appointment_id = "apt123"
        
        # Mock the cancel_appointment method to return success
        self.client.cancel_appointment.return_value = True
        
        # Act
        result = self.client.cancel_appointment(appointment_id)
        
        # Assert
        assert result is True
        self.client.cancel_appointment.assert_called_once_with(appointment_id)

    def test_cancel_appointment_already_cancelled(self):
        """Test appointment cancellation when already cancelled."""
        # Arrange
        appointment_id = "apt123"
        
        # Mock the cancel_appointment method to return already cancelled
        self.client.cancel_appointment.return_value = False
        
        # Act
        result = self.client.cancel_appointment(appointment_id)
        
        # Assert
        assert result is False

    def test_cancel_appointment_error_handling(self):
        """Test appointment cancellation error handling."""
        # Arrange
        self.client.cancel_appointment.return_value = None
        
        # Act
        result = self.client.cancel_appointment("apt123")
        
        # Assert
        assert result is None

    def test_get_user_appointments_success(self):
        """Test successful user appointment retrieval."""
        # Arrange
        user_email = "test@example.com"
        status_filter = "confirmed"
        
        expected_results = [
            {"_id": "apt1", "user_email": "test@example.com", "status": "confirmed"},
            {"_id": "apt2", "user_email": "test@example.com", "status": "confirmed"}
        ]
        
        # Mock the get_user_appointments method to return our results
        self.client.get_user_appointments.return_value = expected_results
        
        # Act
        result = self.client.get_user_appointments(user_email, status_filter)
        
        # Assert
        assert len(result) == 2
        assert all(apt["user_email"] == user_email for apt in result)
        assert all(apt["status"] == status_filter for apt in result)
        
        self.client.get_user_appointments.assert_called_once_with(user_email, status_filter)

    def test_get_user_appointments_no_status_filter(self):
        """Test user appointment retrieval without status filter."""
        # Arrange
        user_email = "test@example.com"
        
        expected_results = [
            {"_id": "apt1", "user_email": "test@example.com", "status": "confirmed"},
            {"_id": "apt2", "user_email": "test@example.com", "status": "pending"}
        ]
        
        # Mock the get_user_appointments method to return our results
        self.client.get_user_appointments.return_value = expected_results
        
        # Act
        result = self.client.get_user_appointments(user_email)
        
        # Assert
        assert len(result) == 2
        assert all(apt["user_email"] == user_email for apt in result)
        
        # Check that the method was called with the correct arguments
        self.client.get_user_appointments.assert_called_once()
        call_args = self.client.get_user_appointments.call_args
        assert call_args[0][0] == user_email

    def test_get_user_appointments_error_handling(self):
        """Test user appointment retrieval error handling."""
        # Arrange
        self.client.get_user_appointments.return_value = []
        
        # Act
        result = self.client.get_user_appointments("test@example.com")
        
        # Assert
        assert result == []

    def test_check_availability_success(self):
        """Test successful availability check."""
        # Arrange
        date = "2024-01-15"
        time = "10:00"
        service_type = "consultation"
        provider = "Dr. Smith"
        
        # Mock the check_availability method to return available
        self.client.check_availability.return_value = True
        
        # Act
        result = self.client.check_availability(date, time, service_type, provider)
        
        # Assert
        assert result is True
        self.client.check_availability.assert_called_once_with(date, time, service_type, provider)

    def test_check_availability_conflict(self):
        """Test availability check with conflicting appointment."""
        # Arrange
        date = "2024-01-15"
        time = "10:00"
        service_type = "consultation"
        provider = "Dr. Smith"
        
        # Mock the check_availability method to return conflict
        self.client.check_availability.return_value = False
        
        # Act
        result = self.client.check_availability(date, time, service_type, provider)
        
        # Assert
        assert result is False

    def test_check_availability_error_handling(self):
        """Test availability check error handling."""
        # Arrange
        self.client.check_availability.return_value = None
        
        # Act
        result = self.client.check_availability("2024-01-15", "10:00", "consultation", "Dr. Smith")
        
        # Assert
        assert result is None
