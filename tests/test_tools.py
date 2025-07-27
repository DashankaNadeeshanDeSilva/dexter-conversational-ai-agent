"""Tests for tool implementations."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
import json

from app.tools.web_search_tool import WebSearchTool
from app.tools.product_search_tool import ProductSearchTool
from app.tools.appointment_tool import AppointmentTool
from app.tools.semantic_retrieval_tool import SemanticRetrievalTool


class TestWebSearchTool:
    """Tests for web search tool."""
    
    def test_init(self):
        """Test initialization of web search tool."""
        # Act
        tool = WebSearchTool()
        
        # Assert
        assert tool.name == "internet_search"
        assert "search the internet" in tool.description.lower()

    @patch('app.tools.web_search_tool.DDGS')
    def test_run_success(self, mock_ddgs_cls):
        """Test successful web search."""
        # Arrange
        mock_ddgs = MagicMock()
        mock_results = [
            {
                "title": "Python Tutorial",
                "body": "Learn Python programming",
                "href": "https://example.com/python"
            },
            {
                "title": "Advanced Python",
                "body": "Advanced Python concepts",
                "href": "https://example.com/advanced-python"
            }
        ]
        mock_ddgs.text.return_value = mock_results
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        
        tool = WebSearchTool()
        
        # Act
        result = tool._run("Python programming tutorial")
        
        # Assert
        assert "Python Tutorial" in result
        assert "Learn Python programming" in result
        assert "https://example.com/python" in result
        assert "Advanced Python" in result
        mock_ddgs.text.assert_called_once_with("Python programming tutorial", max_results=5)

    @patch('app.tools.web_search_tool.DDGS')
    def test_run_no_results(self, mock_ddgs_cls):
        """Test web search with no results."""
        # Arrange
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = []
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        
        tool = WebSearchTool()
        
        # Act
        result = tool._run("very obscure query that returns nothing")
        
        # Assert
        assert "No search results found" in result

    @patch('app.tools.web_search_tool.DDGS')
    def test_run_with_custom_max_results(self, mock_ddgs_cls):
        """Test web search with custom max results."""
        # Arrange
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [{"title": "Test", "body": "Test", "href": "test.com"}]
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        
        tool = WebSearchTool()
        
        # Act
        result = tool._run("test query", max_results=3)
        
        # Assert
        mock_ddgs.text.assert_called_once_with("test query", max_results=3)

    @patch('app.tools.web_search_tool.DDGS')
    def test_run_exception_handling(self, mock_ddgs_cls):
        """Test web search exception handling."""
        # Arrange
        mock_ddgs_cls.side_effect = Exception("Network error")
        
        tool = WebSearchTool()
        
        # Act
        result = tool._run("test query")
        
        # Assert
        assert "Error performing search" in result
        assert "Network error" in result


class TestProductSearchTool:
    """Tests for product search tool."""
    
    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_init(self, mock_db_cls):
        """Test initialization of product search tool."""
        # Arrange
        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db
        
        # Act
        tool = ProductSearchTool()
        
        # Assert
        assert tool.name == "product_search"
        assert "search for products" in tool.description.lower()
        assert tool.db_client == mock_db

    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_run_success(self, mock_db_cls):
        """Test successful product search."""
        # Arrange
        mock_db = MagicMock()
        mock_products = [
            {
                "_id": "product_1",
                "name": "Laptop Pro",
                "price": 1299.99,
                "category": "Electronics",
                "description": "High-performance laptop"
            },
            {
                "_id": "product_2", 
                "name": "Gaming Laptop",
                "price": 1599.99,
                "category": "Electronics",
                "description": "Gaming laptop with RTX graphics"
            }
        ]
        mock_db.search_products.return_value = mock_products
        mock_db_cls.return_value = mock_db
        
        tool = ProductSearchTool()
        
        # Act
        result = tool._run("laptop")
        
        # Assert
        assert "Laptop Pro" in result
        assert "$1299.99" in result
        assert "Gaming Laptop" in result
        assert "$1599.99" in result
        mock_db.search_products.assert_called_once_with("laptop", limit=5)

    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_run_no_products(self, mock_db_cls):
        """Test product search with no results."""
        # Arrange
        mock_db = MagicMock()
        mock_db.search_products.return_value = []
        mock_db_cls.return_value = mock_db
        
        tool = ProductSearchTool()
        
        # Act
        result = tool._run("nonexistent product")
        
        # Assert
        assert "No products found" in result

    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_run_with_custom_limit(self, mock_db_cls):
        """Test product search with custom limit."""
        # Arrange
        mock_db = MagicMock()
        mock_db.search_products.return_value = []
        mock_db_cls.return_value = mock_db
        
        tool = ProductSearchTool()
        
        # Act
        result = tool._run("laptop", limit=10)
        
        # Assert
        mock_db.search_products.assert_called_once_with("laptop", limit=10)

    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_run_exception_handling(self, mock_db_cls):
        """Test product search exception handling."""
        # Arrange
        mock_db = MagicMock()
        mock_db.search_products.side_effect = Exception("Database error")
        mock_db_cls.return_value = mock_db
        
        tool = ProductSearchTool()
        
        # Act
        result = tool._run("laptop")
        
        # Assert
        assert "Error searching for products" in result


class TestAppointmentTool:
    """Tests for appointment tool."""
    
    @patch('app.tools.appointment_tool.DatabaseClient')
    @patch('app.tools.appointment_tool.spacy.load')
    def test_init(self, mock_spacy_load, mock_db_cls):
        """Test initialization of appointment tool."""
        # Arrange
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp
        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db
        
        # Act
        tool = AppointmentTool()
        
        # Assert
        assert tool.name == "appointment_tool"
        assert "manage appointments" in tool.description.lower()
        assert tool.nlp == mock_nlp
        assert tool.db_client == mock_db

    @patch('app.tools.appointment_tool.DatabaseClient')
    @patch('app.tools.appointment_tool.spacy.load')
    def test_extract_appointment_info(self, mock_spacy_load, mock_db_cls):
        """Test extracting appointment information from text."""
        # Arrange
        mock_nlp = MagicMock()
        mock_doc = MagicMock()
        
        # Mock entity extraction
        mock_person = MagicMock()
        mock_person.label_ = "PERSON"
        mock_person.text = "Dr. Smith"
        
        mock_date = MagicMock()
        mock_date.label_ = "DATE"
        mock_date.text = "tomorrow"
        
        mock_time = MagicMock()
        mock_time.label_ = "TIME"
        mock_time.text = "2 PM"
        
        mock_doc.ents = [mock_person, mock_date, mock_time]
        mock_nlp.return_value = mock_doc
        mock_spacy_load.return_value = mock_nlp
        
        tool = AppointmentTool()
        
        # Act
        info = tool._extract_appointment_info("Schedule appointment with Dr. Smith tomorrow at 2 PM")
        
        # Assert
        assert "Dr. Smith" in info["providers"]
        assert "tomorrow" in info["dates"]
        assert "2 PM" in info["times"]

    @patch('app.tools.appointment_tool.DatabaseClient')
    @patch('app.tools.appointment_tool.spacy.load')
    def test_run_book_appointment(self, mock_spacy_load, mock_db_cls):
        """Test booking an appointment."""
        # Arrange
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp
        
        mock_db = MagicMock()
        mock_db.create_appointment.return_value = "appointment_123"
        mock_db_cls.return_value = mock_db
        
        tool = AppointmentTool()
        tool._extract_appointment_info = MagicMock(return_value={
            "providers": ["Dr. Smith"],
            "dates": ["2024-01-15"],
            "times": ["2 PM"],
            "purposes": ["checkup"]
        })
        
        # Act
        result = tool._run("book appointment with Dr. Smith on January 15th at 2 PM for checkup")
        
        # Assert
        assert "appointment has been booked" in result.lower()
        assert "appointment_123" in result
        mock_db.create_appointment.assert_called_once()

    @patch('app.tools.appointment_tool.DatabaseClient')
    @patch('app.tools.appointment_tool.spacy.load')
    def test_run_list_appointments(self, mock_spacy_load, mock_db_cls):
        """Test listing appointments."""
        # Arrange
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp
        
        mock_db = MagicMock()
        mock_appointments = [
            {
                "_id": "appointment_1",
                "provider": "Dr. Smith",
                "date": "2024-01-15",
                "time": "2 PM",
                "purpose": "checkup"
            },
            {
                "_id": "appointment_2",
                "provider": "Dr. Johnson", 
                "date": "2024-01-20",
                "time": "10 AM",
                "purpose": "consultation"
            }
        ]
        mock_db.get_user_appointments.return_value = mock_appointments
        mock_db_cls.return_value = mock_db
        
        tool = AppointmentTool()
        
        # Act
        result = tool._run("list my appointments")
        
        # Assert
        assert "Dr. Smith" in result
        assert "2024-01-15" in result
        assert "Dr. Johnson" in result
        assert "2024-01-20" in result

    @patch('app.tools.appointment_tool.DatabaseClient')
    @patch('app.tools.appointment_tool.spacy.load')
    def test_run_cancel_appointment(self, mock_spacy_load, mock_db_cls):
        """Test canceling an appointment."""
        # Arrange
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp
        
        mock_db = MagicMock()
        mock_db.cancel_appointment.return_value = True
        mock_db_cls.return_value = mock_db
        
        tool = AppointmentTool()
        
        # Act
        result = tool._run("cancel appointment appointment_123")
        
        # Assert
        assert "appointment has been cancelled" in result.lower()
        mock_db.cancel_appointment.assert_called_once_with("appointment_123")


class TestSemanticRetrievalTool:
    """Tests for semantic retrieval tool."""
    
    def test_init(self):
        """Test initialization of semantic retrieval tool."""
        # Act
        tool = SemanticRetrievalTool()
        
        # Assert
        assert tool.name == "semantic_retrieval"
        assert "retrieve relevant information" in tool.description.lower()
        assert tool.memory_manager is not None

    @patch('app.tools.semantic_retrieval_tool.MemoryManager')
    def test_run_success(self, mock_memory_manager_cls):
        """Test successful semantic retrieval."""
        # Arrange
        mock_memory_manager = MagicMock()
        mock_documents = [
            (MagicMock(page_content="User likes coffee in the morning", metadata={"confidence": 0.95}), 0.95),
            (MagicMock(page_content="User prefers remote work", metadata={"confidence": 0.87}), 0.87)
        ]
        mock_memory_manager.retrieve_semantic_memories.return_value = mock_documents
        mock_memory_manager_cls.return_value = mock_memory_manager
        
        tool = SemanticRetrievalTool()
        
        # Act
        result = tool._run("coffee preferences", user_id="test_user")
        
        # Assert
        assert "coffee in the morning" in result
        assert "remote work" in result
        assert "confidence: 0.95" in result
        assert "confidence: 0.87" in result
        mock_memory_manager.retrieve_semantic_memories.assert_called_once_with(
            user_id="test_user",
            query="coffee preferences",
            k=5
        )

    @patch('app.tools.semantic_retrieval_tool.MemoryManager')
    def test_run_no_results(self, mock_memory_manager_cls):
        """Test semantic retrieval with no results."""
        # Arrange
        mock_memory_manager = MagicMock()
        mock_memory_manager.retrieve_semantic_memories.return_value = []
        mock_memory_manager_cls.return_value = mock_memory_manager
        
        tool = SemanticRetrievalTool()
        
        # Act
        result = tool._run("nonexistent information", user_id="test_user")
        
        # Assert
        assert "No relevant information found" in result

    @patch('app.tools.semantic_retrieval_tool.MemoryManager')
    def test_run_with_custom_k(self, mock_memory_manager_cls):
        """Test semantic retrieval with custom k parameter."""
        # Arrange
        mock_memory_manager = MagicMock()
        mock_memory_manager.retrieve_semantic_memories.return_value = []
        mock_memory_manager_cls.return_value = mock_memory_manager
        
        tool = SemanticRetrievalTool()
        
        # Act
        result = tool._run("test query", user_id="test_user", k=10)
        
        # Assert
        mock_memory_manager.retrieve_semantic_memories.assert_called_once_with(
            user_id="test_user",
            query="test query",
            k=10
        )

    @patch('app.tools.semantic_retrieval_tool.MemoryManager')
    def test_run_exception_handling(self, mock_memory_manager_cls):
        """Test semantic retrieval exception handling."""
        # Arrange
        mock_memory_manager = MagicMock()
        mock_memory_manager.retrieve_semantic_memories.side_effect = Exception("Retrieval error")
        mock_memory_manager_cls.return_value = mock_memory_manager
        
        tool = SemanticRetrievalTool()
        
        # Act
        result = tool._run("test query", user_id="test_user")
        
        # Assert
        assert "Error retrieving information" in result
        assert "Retrieval error" in result

    def test_missing_user_id(self):
        """Test semantic retrieval without user_id."""
        # Arrange
        tool = SemanticRetrievalTool()
        
        # Act
        result = tool._run("test query")
        
        # Assert
        assert "user_id is required" in result.lower()


class TestToolIntegration:
    """Integration tests for tools working together."""
    
    @patch('app.tools.web_search_tool.DDGS')
    @patch('app.tools.product_search_tool.DatabaseClient')
    def test_web_search_and_product_search_integration(self, mock_product_db_cls, mock_ddgs_cls):
        """Test web search and product search working together."""
        # Arrange
        # Web search mock
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [
            {"title": "Best Laptops 2024", "body": "Top laptop reviews", "href": "reviews.com"}
        ]
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        
        # Product search mock
        mock_product_db = MagicMock()
        mock_product_db.search_products.return_value = [
            {"name": "MacBook Pro", "price": 1999.99, "category": "Laptops"}
        ]
        mock_product_db_cls.return_value = mock_product_db
        
        web_tool = WebSearchTool()
        product_tool = ProductSearchTool()
        
        # Act
        web_result = web_tool._run("best laptops 2024")
        product_result = product_tool._run("laptop")
        
        # Assert
        assert "Best Laptops 2024" in web_result
        assert "MacBook Pro" in product_result
        assert "$1999.99" in product_result

    def test_tool_error_isolation(self):
        """Test that tool errors don't affect other tools."""
        # Arrange
        tool1 = WebSearchTool()
        tool2 = ProductSearchTool()
        
        with patch('app.tools.web_search_tool.DDGS', side_effect=Exception("Web error")):
            with patch('app.tools.product_search_tool.DatabaseClient') as mock_db_cls:
                mock_db = MagicMock()
                mock_db.search_products.return_value = [{"name": "Test Product"}]
                mock_db_cls.return_value = mock_db
                
                # Act
                web_result = tool1._run("test query")
                product_result = tool2._run("test product")
                
                # Assert
                assert "Error performing search" in web_result
                assert "Test Product" in product_result  # Product search should still work
