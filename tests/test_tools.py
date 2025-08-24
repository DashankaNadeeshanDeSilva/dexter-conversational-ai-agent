"""Tests for the AI Agent tools."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.tools.web_search_tool import WebSearchTool
from app.tools.product_search_tool import ProductSearchTool
from app.tools.appointment_tool import AppointmentTool
from app.tools.semantic_retrieval_tool import KnowledgeRetrievalTool
from app.tools.database_client import DatabaseClient
from app.tools.tool_config import ToolConfig


class TestWebSearchTool:
    """Test the WebSearchTool."""
    
    @pytest.fixture
    def web_search_tool(self):
        """Create a WebSearchTool instance."""
        return WebSearchTool()
    
    @pytest.fixture
    def sample_search_results(self):
        """Sample search results for testing."""
        return [
            {
                "title": "AI and Machine Learning",
                "link": "https://example.com/ai-ml",
                "snippet": "Artificial Intelligence and Machine Learning are transforming industries..."
            },
            {
                "title": "Python Programming",
                "link": "https://example.com/python",
                "snippet": "Python is a versatile programming language..."
            }
        ]
    
    def test_web_search_tool_initialization(self, web_search_tool):
        """Test WebSearchTool initialization."""
        assert web_search_tool.name == "web_search"
        assert "Search the web" in web_search_tool.description
        assert web_search_tool.return_direct is False
    
    @patch('app.tools.web_search_tool.DDGS')
    def test_web_search_tool_search(self, mock_ddgs, web_search_tool, sample_search_results):
        """Test web search functionality."""
        # Mock the search results
        mock_ddgs_instance = MagicMock()
        mock_ddgs.return_value = mock_ddgs_instance
        mock_ddgs_instance.text.return_value.__iter__.return_value = sample_search_results
        
        query = "artificial intelligence"
        result = web_search_tool._run(query)
        
        # Verify the search was called
        mock_ddgs_instance.text.assert_called_once_with(query, max_results=5)
        
        # Verify the result format
        assert "AI and Machine Learning" in result
        assert "Python Programming" in result
        assert "https://example.com/ai-ml" in result
    
    @patch('app.tools.web_search_tool.DDGS')
    def test_web_search_tool_no_results(self, mock_ddgs, web_search_tool):
        """Test web search when no results are found."""
        # Mock empty search results
        mock_ddgs_instance = MagicMock()
        mock_ddgs.return_value = mock_ddgs_instance
        mock_ddgs_instance.text.return_value.__iter__.return_value = []
        
        query = "nonexistent query"
        result = web_search_tool._run(query)
        
        assert "No results found" in result
    
    @patch('app.tools.web_search_tool.DDGS')
    def test_web_search_tool_error_handling(self, mock_ddgs, web_search_tool):
        """Test web search error handling."""
        # Mock an exception
        mock_ddgs.side_effect = Exception("Search error")
        
        query = "test query"
        result = web_search_tool._run(query)
        
        assert "Error performing web search" in result
        assert "Search error" in result


class TestProductSearchTool:
    """Test the ProductSearchTool."""
    
    @pytest.fixture
    def product_search_tool(self):
        """Create a ProductSearchTool instance."""
        return ProductSearchTool()
    
    @pytest.fixture
    def sample_products(self):
        """Sample product data for testing."""
        return [
            {
                "id": "prod1",
                "name": "Laptop",
                "category": "Electronics",
                "price": 999.99,
                "description": "High-performance laptop"
            },
            {
                "id": "prod2",
                "name": "Smartphone",
                "category": "Electronics",
                "price": 599.99,
                "description": "Latest smartphone model"
            }
        ]
    
    def test_product_search_tool_initialization(self, product_search_tool):
        """Test ProductSearchTool initialization."""
        assert product_search_tool.name == "product_search"
        assert "Search for products" in product_search_tool.description
        assert product_search_tool.return_direct is False
    
    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_product_search_tool_search(self, mock_db_client, product_search_tool, sample_products):
        """Test product search functionality."""
        # Mock the database client
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        mock_db_instance.search_products.return_value = sample_products
        
        query = "laptop"
        result = product_search_tool._run(query)
        
        # Verify the search was called
        mock_db_instance.search_products.assert_called_once_with(query)
        
        # Verify the result format
        assert "Laptop" in result
        assert "Smartphone" in result
        assert "999.99" in result
        assert "Electronics" in result
    
    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_product_search_tool_no_results(self, mock_db_client, product_search_tool):
        """Test product search when no results are found."""
        # Mock empty search results
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        mock_db_instance.search_products.return_value = []
        
        query = "nonexistent product"
        result = product_search_tool._run(query)
        
        assert "No products found" in result
    
    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_product_search_tool_error_handling(self, mock_db_client, product_search_tool):
        """Test product search error handling."""
        # Mock an exception
        mock_db_client.side_effect = Exception("Database error")
        
        query = "test query"
        result = product_search_tool._run(query)
        
        assert "Error searching products" in result
        assert "Database error" in result
    
    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_product_search_tool_with_category_filter(self, mock_db_client, product_search_tool, sample_products):
        """Test product search with category filter."""
        # Mock the database client
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        mock_db_instance.search_products.return_value = [sample_products[0]]  # Only laptop
        
        query = "laptop electronics"
        result = product_search_tool._run(query)
        
        # Verify the search was called
        mock_db_instance.search_products.assert_called_once_with(query)
        
        # Verify only laptop is in results
        assert "Laptop" in result
        assert "Smartphone" not in result


class TestAppointmentTool:
    """Test the AppointmentTool."""
    
    @pytest.fixture
    def appointment_tool(self):
        """Create an AppointmentTool instance."""
        return AppointmentTool()
    
    @pytest.fixture
    def sample_appointment_data(self):
        """Sample appointment data for testing."""
        return {
            "user_id": "user123",
            "service": "consultation",
            "date": "2024-01-15",
            "time": "14:00",
            "duration": 60,
            "notes": "AI consultation session"
        }
    
    def test_appointment_tool_initialization(self, appointment_tool):
        """Test AppointmentTool initialization."""
        assert appointment_tool.name == "appointment"
        assert "Book appointments" in appointment_tool.description
        assert appointment_tool.return_direct is False
    
    @patch('app.tools.appointment_tool.DatabaseClient')
    def test_appointment_tool_book_appointment(self, mock_db_client, appointment_tool, sample_appointment_data):
        """Test booking an appointment."""
        # Mock the database client
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        mock_db_instance.book_appointment.return_value = "apt123"
        
        # Test booking
        result = appointment_tool._run(
            user_id=sample_appointment_data["user_id"],
            service=sample_appointment_data["service"],
            date=sample_appointment_data["date"],
            time=sample_appointment_data["time"],
            duration=sample_appointment_data["duration"],
            notes=sample_appointment_data["notes"]
        )
        
        # Verify the booking was called
        mock_db_instance.book_appointment.assert_called_once()
        
        # Verify the result
        assert "Appointment booked successfully" in result
        assert "apt123" in result
    
    @patch('app.tools.appointment_tool.DatabaseClient')
    def test_appointment_tool_check_availability(self, mock_db_client, appointment_tool):
        """Test checking appointment availability."""
        # Mock the database client
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        mock_db_instance.check_availability.return_value = ["09:00", "10:00", "14:00"]
        
        # Test availability check
        result = appointment_tool._run(
            action="check_availability",
            date="2024-01-15",
            service="consultation"
        )
        
        # Verify the availability check was called
        mock_db_instance.check_availability.assert_called_once()
        
        # Verify the result
        assert "Available times" in result
        assert "09:00" in result
        assert "14:00" in result
    
    @patch('app.tools.appointment_tool.DatabaseClient')
    def test_appointment_tool_reschedule_appointment(self, mock_db_client, appointment_tool):
        """Test rescheduling an appointment."""
        # Mock the database client
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        mock_db_instance.reschedule_appointment.return_value = True
        
        # Test rescheduling
        result = appointment_tool._run(
            action="reschedule",
            appointment_id="apt123",
            new_date="2024-01-16",
            new_time="15:00"
        )
        
        # Verify the reschedule was called
        mock_db_instance.reschedule_appointment.assert_called_once()
        
        # Verify the result
        assert "Appointment rescheduled successfully" in result
    
    @patch('app.tools.appointment_tool.DatabaseClient')
    def test_appointment_tool_cancel_appointment(self, mock_db_client, appointment_tool):
        """Test canceling an appointment."""
        # Mock the database client
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        mock_db_instance.cancel_appointment.return_value = True
        
        # Test cancellation
        result = appointment_tool._run(
            action="cancel",
            appointment_id="apt123"
        )
        
        # Verify the cancellation was called
        mock_db_instance.cancel_appointment.assert_called_once()
        
        # Verify the result
        assert "Appointment cancelled successfully" in result
    
    @patch('app.tools.appointment_tool.DatabaseClient')
    def test_appointment_tool_invalid_action(self, mock_db_client, appointment_tool):
        """Test appointment tool with invalid action."""
        # Mock the database client
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        # Test invalid action
        result = appointment_tool._run(action="invalid_action")
        
        # Verify no database calls were made
        mock_db_instance.book_appointment.assert_not_called()
        mock_db_instance.check_availability.assert_not_called()
        
        # Verify error message
        assert "Invalid action" in result
    
    @patch('app.tools.appointment_tool.DatabaseClient')
    def test_appointment_tool_error_handling(self, mock_db_client, appointment_tool):
        """Test appointment tool error handling."""
        # Mock an exception
        mock_db_client.side_effect = Exception("Database error")
        
        result = appointment_tool._run(
            user_id="user123",
            service="consultation",
            date="2024-01-15",
            time="14:00"
        )
        
        assert "Error processing appointment" in result
        assert "Database error" in result


class TestKnowledgeRetrievalTool:
    """Test the KnowledgeRetrievalTool."""
    
    @pytest.fixture
    def knowledge_tool(self):
        """Create a KnowledgeRetrievalTool instance."""
        return KnowledgeRetrievalTool()
    
    @pytest.fixture
    def sample_knowledge_results(self):
        """Sample knowledge results for testing."""
        return [
            {
                "content": "AI is artificial intelligence",
                "source": "textbook",
                "relevance": 0.95
            },
            {
                "content": "Machine learning is a subset of AI",
                "source": "research_paper",
                "relevance": 0.88
            }
        ]
    
    def test_knowledge_retrieval_tool_initialization(self, knowledge_tool):
        """Test KnowledgeRetrievalTool initialization."""
        assert knowledge_tool.name == "knowledge_retrieval"
        assert "Retrieve knowledge" in knowledge_tool.description
        assert knowledge_tool.return_direct is False
    
    @patch('app.tools.semantic_retrieval_tool.PineconeClient')
    def test_knowledge_retrieval_tool_search(self, mock_pinecone_client, knowledge_tool, sample_knowledge_results):
        """Test knowledge retrieval functionality."""
        # Mock the Pinecone client
        mock_pinecone_instance = MagicMock()
        mock_pinecone_client.return_value = mock_pinecone_instance
        mock_pinecone_instance.search_knowledge.return_value = sample_knowledge_results
        
        query = "What is artificial intelligence?"
        result = knowledge_tool._run(query)
        
        # Verify the search was called
        mock_pinecone_instance.search_knowledge.assert_called_once_with(query)
        
        # Verify the result format
        assert "AI is artificial intelligence" in result
        assert "Machine learning is a subset of AI" in result
        assert "textbook" in result
        assert "research_paper" in result
    
    @patch('app.tools.semantic_retrieval_tool.PineconeClient')
    def test_knowledge_retrieval_tool_no_results(self, mock_pinecone_client, knowledge_tool):
        """Test knowledge retrieval when no results are found."""
        # Mock empty search results
        mock_pinecone_instance = MagicMock()
        mock_pinecone_client.return_value = mock_pinecone_instance
        mock_pinecone_instance.search_knowledge.return_value = []
        
        query = "nonexistent knowledge"
        result = knowledge_tool._run(query)
        
        assert "No relevant knowledge found" in result
    
    @patch('app.tools.semantic_retrieval_tool.PineconeClient')
    def test_knowledge_retrieval_tool_error_handling(self, mock_pinecone_client, knowledge_tool):
        """Test knowledge retrieval error handling."""
        # Mock an exception
        mock_pinecone_client.side_effect = Exception("Pinecone error")
        
        query = "test query"
        result = knowledge_tool._run(query)
        
        assert "Error retrieving knowledge" in result
        assert "Pinecone error" in result


class TestDatabaseClient:
    """Test the DatabaseClient."""
    
    @pytest.fixture
    def db_client(self):
        """Create a DatabaseClient instance."""
        return DatabaseClient()
    
    @patch('app.tools.database_client.MongoClient')
    def test_database_client_initialization(self, mock_mongo_client, db_client):
        """Test DatabaseClient initialization."""
        assert db_client.database is not None
        mock_mongo_client.assert_called_once()
    
    @patch('app.tools.database_client.MongoClient')
    def test_database_client_search_products(self, mock_mongo_client, db_client):
        """Test product search in database."""
        # Mock the database and collection
        mock_collection = MagicMock()
        mock_database = MagicMock()
        mock_mongo_client.return_value.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        
        # Mock search results
        mock_collection.find.return_value = [
            {"name": "Laptop", "price": 999.99},
            {"name": "Smartphone", "price": 599.99}
        ]
        
        query = "laptop"
        results = db_client.search_products(query)
        
        # Verify the search was performed
        mock_collection.find.assert_called_once()
        assert len(results) == 2
        assert results[0]["name"] == "Laptop"
    
    @patch('app.tools.database_client.MongoClient')
    def test_database_client_book_appointment(self, mock_mongo_client, db_client):
        """Test booking appointment in database."""
        # Mock the database and collection
        mock_collection = MagicMock()
        mock_database = MagicMock()
        mock_mongo_client.return_value.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        
        # Mock appointment insertion
        mock_collection.insert_one.return_value.inserted_id = "apt123"
        
        appointment_data = {
            "user_id": "user123",
            "service": "consultation",
            "date": "2024-01-15",
            "time": "14:00"
        }
        
        result = db_client.book_appointment(appointment_data)
        
        # Verify the appointment was inserted
        mock_collection.insert_one.assert_called_once()
        assert result == "apt123"
    
    @patch('app.tools.database_client.MongoClient')
    def test_database_client_check_availability(self, mock_mongo_client, db_client):
        """Test checking appointment availability."""
        # Mock the database and collection
        mock_collection = MagicMock()
        mock_database = MagicMock()
        mock_mongo_client.return_value.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection
        
        # Mock availability check
        mock_collection.find.return_value = [
            {"time": "09:00"},
            {"time": "10:00"},
            {"time": "14:00"}
        ]
        
        date = "2024-01-15"
        service = "consultation"
        available_times = db_client.check_availability(date, service)
        
        # Verify the availability check was performed
        mock_collection.find.assert_called_once()
        assert len(available_times) == 3
        assert "09:00" in available_times


class TestToolConfig:
    """Test the ToolConfig."""
    
    def test_tool_config_initialization(self):
        """Test ToolConfig initialization."""
        config = ToolConfig()
        
        assert hasattr(config, 'WEB_SEARCH_ENABLED')
        assert hasattr(config, 'PRODUCT_SEARCH_ENABLED')
        assert hasattr(config, 'APPOINTMENT_ENABLED')
        assert hasattr(config, 'KNOWLEDGE_RETRIEVAL_ENABLED')
    
    def test_tool_config_default_values(self):
        """Test ToolConfig default values."""
        config = ToolConfig()
        
        assert config.WEB_SEARCH_ENABLED is True
        assert config.PRODUCT_SEARCH_ENABLED is True
        assert config.APPOINTMENT_ENABLED is True
        assert config.KNOWLEDGE_RETRIEVAL_ENABLED is True
    
    def test_tool_config_environment_override(self):
        """Test ToolConfig environment variable override."""
        with patch.dict('os.environ', {
            'WEB_SEARCH_ENABLED': 'false',
            'PRODUCT_SEARCH_ENABLED': 'false'
        }):
            config = ToolConfig()
            
            assert config.WEB_SEARCH_ENABLED is False
            assert config.PRODUCT_SEARCH_ENABLED is False
            assert config.APPOINTMENT_ENABLED is True  # Default value
            assert config.KNOWLEDGE_RETRIEVAL_ENABLED is True  # Default value


class TestToolIntegration:
    """Integration tests for tools."""
    
    @pytest.mark.asyncio
    async def test_tools_with_memory_integration(self):
        """Test tools integration with memory system."""
        # This would test how tools interact with the memory system
        # For now, we'll test basic tool functionality
        web_tool = WebSearchTool()
        product_tool = ProductSearchTool()
        appointment_tool = AppointmentTool()
        knowledge_tool = KnowledgeRetrievalTool()
        
        # Verify all tools are properly initialized
        assert web_tool.name == "web_search"
        assert product_tool.name == "product_search"
        assert appointment_tool.name == "appointment"
        assert knowledge_tool.name == "knowledge_retrieval"
        
        # Verify all tools have descriptions
        assert len(web_tool.description) > 0
        assert len(product_tool.description) > 0
        assert len(appointment_tool.description) > 0
        assert len(knowledge_tool.description) > 0
    
    def test_tool_error_handling_consistency(self):
        """Test that all tools handle errors consistently."""
        tools = [
            WebSearchTool(),
            ProductSearchTool(),
            AppointmentTool(),
            KnowledgeRetrievalTool()
        ]
        
        for tool in tools:
            # All tools should have error handling
            assert hasattr(tool, '_run')
            
            # Test with invalid input to ensure error handling
            try:
                result = tool._run("")
                # Should return an error message, not raise an exception
                assert isinstance(result, str)
            except Exception as e:
                # If an exception is raised, it should be handled gracefully
                assert False, f"Tool {tool.name} raised an exception: {e}"
