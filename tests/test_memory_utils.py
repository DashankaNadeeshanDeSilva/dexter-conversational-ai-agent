"""Tests for the AgentMemoryUtils class."""

import pytest
from unittest.mock import MagicMock, patch
from app.agent.memory_utils import AgentMemoryUtils
from langchain_core.documents import Document


class TestAgentMemoryUtils:
    """Test the AgentMemoryUtils class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_memory_manager = MagicMock()
        self.memory_utils = AgentMemoryUtils(self.mock_memory_manager)

    def test_init(self):
        """Test AgentMemoryUtils initialization."""
        # Act & Assert
        assert self.memory_utils.memory_manager == self.mock_memory_manager

    def test_retrieve_memory_context_success(self):
        """Test successful memory context retrieval."""
        # Arrange
        user_id = "test_user"
        query = "test query"
        
        # Mock semantic memories
        semantic_memories = [
            (Document(page_content="Fact 1"), 0.9),
            (Document(page_content="Fact 2"), 0.8)
        ]
        
        # Mock episodic memories
        episodic_memories = [
            {"content": {"message": {"content": "Past interaction 1"}}},
            {"content": {"message": {"content": "Past interaction 2"}}}
        ]
        
        # Mock procedural memories
        procedural_memories = [
            {"content": {"tool": "search_tool", "arguments": {"query": "test"}}},
            {"content": {"successful_pattern": "direct_response"}}
        ]
        
        # Mock the individual context methods
        with patch.object(self.memory_utils, 'get_semantic_context', return_value=semantic_memories), \
             patch.object(self.memory_utils, 'get_episodic_context', return_value=episodic_memories), \
             patch.object(self.memory_utils, 'get_procedural_context', return_value=procedural_memories):
            
            # Act
            result = self.memory_utils.retrieve_memory_context(user_id, query)
            
            # Assert
            assert "Relevant information from memory:" in result
            assert "Fact: Fact 1 (relevance: 0.90)" in result
            assert "Fact: Fact 2 (relevance: 0.80)" in result
            assert "Past interaction: Past interaction 1" in result
            assert "Past interaction: Past interaction 2" in result
            assert "Learned patterns and tool usage:" in result
            assert "For similar queries, successfully used search_tool with args: {'query': 'test'}" in result
            assert "Successful approach: direct_response" in result

    def test_retrieve_memory_context_no_memories(self):
        """Test memory context retrieval when no memories exist."""
        # Arrange
        user_id = "test_user"
        query = "test query"
        
        # Mock empty memories
        with patch.object(self.memory_utils, 'get_semantic_context', return_value=[]), \
             patch.object(self.memory_utils, 'get_episodic_context', return_value=[]), \
             patch.object(self.memory_utils, 'get_procedural_context', return_value=[]):
            
            # Act
            result = self.memory_utils.retrieve_memory_context(user_id, query)
            
            # Assert
            assert result == "No relevant information found in memory."

    def test_get_semantic_context(self):
        """Test semantic context retrieval."""
        # Arrange
        user_id = "test_user"
        query = "test query"
        k = 5
        expected_memories = [
            (Document(page_content="Fact 1"), 0.9),
            (Document(page_content="Fact 2"), 0.8)
        ]
        
        self.mock_memory_manager.retrieve_semantic_memories.return_value = expected_memories
        
        # Act
        result = self.memory_utils.get_semantic_context(user_id, query, k)
        
        # Assert
        assert result == expected_memories
        self.mock_memory_manager.retrieve_semantic_memories.assert_called_once_with(
            user_id=user_id,
            query=query,
            k=k
        )

    def test_get_semantic_context_default_k(self):
        """Test semantic context retrieval with default k value."""
        # Arrange
        user_id = "test_user"
        query = "test query"
        expected_memories = [(Document(page_content="Fact 1"), 0.9)]
        
        self.mock_memory_manager.retrieve_semantic_memories.return_value = expected_memories
        
        # Act
        result = self.memory_utils.get_semantic_context(user_id, query)
        
        # Assert
        assert result == expected_memories
        self.mock_memory_manager.retrieve_semantic_memories.assert_called_once_with(
            user_id=user_id,
            query=query,
            k=3  # Default value
        )

    def test_get_episodic_context(self):
        """Test episodic context retrieval."""
        # Arrange
        user_id = "test_user"
        query = "test query"
        limit = 5
        expected_memories = [
            {"content": {"message": {"content": "Past interaction 1"}}},
            {"content": {"message": {"content": "Past interaction 2"}}}
        ]
        
        self.mock_memory_manager.retrieve_episodic_memories.return_value = expected_memories
        
        # Act
        result = self.memory_utils.get_episodic_context(user_id, query, limit)
        
        # Assert
        assert result == expected_memories
        self.mock_memory_manager.retrieve_episodic_memories.assert_called_once_with(
            user_id=user_id,
            filter_query={
                "content.message.content": {"$regex": query, "$options": "i"}
            },
            limit=limit
        )

    def test_get_episodic_context_default_limit(self):
        """Test episodic context retrieval with default limit value."""
        # Arrange
        user_id = "test_user"
        query = "test query"
        expected_memories = [{"content": {"message": {"content": "Past interaction"}}}]
        
        self.mock_memory_manager.retrieve_episodic_memories.return_value = expected_memories
        
        # Act
        result = self.memory_utils.get_episodic_context(user_id, query)
        
        # Assert
        assert result == expected_memories
        self.mock_memory_manager.retrieve_episodic_memories.assert_called_once_with(
            user_id=user_id,
            filter_query={
                "content.message.content": {"$regex": query, "$options": "i"}
            },
            limit=3  # Default value
        )

    def test_get_procedural_context(self):
        """Test procedural context retrieval."""
        # Arrange
        user_id = "test_user"
        query = "test query"
        limit = 7
        expected_memories = [
            {"content": {"tool": "search_tool", "arguments": {"query": "test"}}},
            {"content": {"successful_pattern": "direct_response"}}
        ]
        
        self.mock_memory_manager.retrieve_procedural_memories.return_value = expected_memories
        
        # Act
        result = self.memory_utils.get_procedural_context(user_id, query, limit)
        
        # Assert
        assert result == expected_memories
        self.mock_memory_manager.retrieve_procedural_memories.assert_called_once_with(
            user_id=user_id,
            filter_query={
                "$or": [
                    {"content.query_context": {"$regex": query[:50], "$options": "i"}},
                    {"content.tool": {"$exists": True}},
                    {"content.successful_pattern": {"$exists": True}}
                ]
            },
            limit=limit
        )

    def test_get_procedural_context_default_limit(self):
        """Test procedural context retrieval with default limit value."""
        # Arrange
        user_id = "test_user"
        query = "test query"
        expected_memories = [{"content": {"tool": "search_tool"}}]
        
        self.mock_memory_manager.retrieve_procedural_memories.return_value = expected_memories
        
        # Act
        result = self.memory_utils.get_procedural_context(user_id, query)
        
        # Assert
        assert result == expected_memories
        self.mock_memory_manager.retrieve_procedural_memories.assert_called_once_with(
            user_id=user_id,
            filter_query={
                "$or": [
                    {"content.query_context": {"$regex": query[:50], "$options": "i"}},
                    {"content.tool": {"$exists": True}},
                    {"content.successful_pattern": {"$exists": True}}
                ]
            },
            limit=5  # Default value
        )

    def test_get_procedural_context_long_query(self):
        """Test procedural context retrieval with long query (truncation)."""
        # Arrange
        user_id = "test_user"
        query = "this is a very long query that should be truncated to 50 characters for the filter"
        limit = 5
        
        # Act
        self.memory_utils.get_procedural_context(user_id, query, limit)
        
        # Assert
        self.mock_memory_manager.retrieve_procedural_memories.assert_called_once()
        call_args = self.mock_memory_manager.retrieve_procedural_memories.call_args
        filter_query = call_args[1]["filter_query"]
        regex_pattern = filter_query["$or"][0]["content.query_context"]["$regex"]
        # The query should be truncated to 50 characters
        assert len(regex_pattern) <= 50
        assert regex_pattern == query[:50]

    def test_combine_memory_contexts_semantic_only(self):
        """Test combining memory contexts with only semantic memories."""
        # Arrange
        semantic_memories = [
            (Document(page_content="Fact 1"), 0.9),
            (Document(page_content="Fact 2"), 0.8)
        ]
        episodic_memories = []
        procedural_memories = []
        
        # Act
        result = self.memory_utils.combine_memory_contexts(
            semantic_memories, episodic_memories, procedural_memories
        )
        
        # Assert
        assert "Relevant information from memory:" in result
        assert "Fact: Fact 1 (relevance: 0.90)" in result
        assert "Fact: Fact 2 (relevance: 0.80)" in result
        assert "Past interaction:" not in result
        assert "Learned patterns and tool usage:" not in result

    def test_combine_memory_contexts_episodic_only(self):
        """Test combining memory contexts with only episodic memories."""
        # Arrange
        semantic_memories = []
        episodic_memories = [
            {"content": {"message": {"content": "Past interaction 1"}}},
            {"content": {"message": {"content": "Past interaction 2"}}}
        ]
        procedural_memories = []
        
        # Act
        result = self.memory_utils.combine_memory_contexts(
            semantic_memories, episodic_memories, procedural_memories
        )
        
        # Assert
        assert "Relevant information from memory:" in result
        assert "Past interaction: Past interaction 1" in result
        assert "Past interaction: Past interaction 2" in result
        assert "Fact:" not in result
        assert "Learned patterns and tool usage:" not in result

    def test_combine_memory_contexts_procedural_only(self):
        """Test combining memory contexts with only procedural memories."""
        # Arrange
        semantic_memories = []
        episodic_memories = []
        procedural_memories = [
            {"content": {"tool": "search_tool", "arguments": {"query": "test"}}},
            {"content": {"successful_pattern": "direct_response"}}
        ]
        
        # Act
        result = self.memory_utils.combine_memory_contexts(
            semantic_memories, episodic_memories, procedural_memories
        )
        
        # Assert
        assert "Relevant information from memory:" in result
        assert "Learned patterns and tool usage:" in result
        assert "For similar queries, successfully used search_tool with args: {'query': 'test'}" in result
        assert "Successful approach: direct_response" in result
        assert "Fact:" not in result
        assert "Past interaction:" not in result

    def test_combine_memory_contexts_mixed_content(self):
        """Test combining memory contexts with mixed content types."""
        # Arrange
        semantic_memories = [(Document(page_content="Mixed fact"), 0.7)]
        episodic_memories = [{"content": {"message": {"content": "Mixed interaction"}}}]
        procedural_memories = [{"content": {"tool": "mixed_tool"}}]
        
        # Act
        result = self.memory_utils.combine_memory_contexts(
            semantic_memories, episodic_memories, procedural_memories
        )
        
        # Assert
        assert "Relevant information from memory:" in result
        assert "Fact: Mixed fact (relevance: 0.70)" in result
        assert "Past interaction: Mixed interaction" in result
        assert "For similar queries, successfully used mixed_tool with args: {}" in result

    def test_combine_memory_contexts_empty_all(self):
        """Test combining memory contexts with all empty."""
        # Arrange
        semantic_memories = []
        episodic_memories = []
        procedural_memories = []
        
        # Act
        result = self.memory_utils.combine_memory_contexts(
            semantic_memories, episodic_memories, procedural_memories
        )
        
        # Assert
        assert result == "No relevant information found in memory."

    def test_combine_memory_contexts_procedural_tool_pattern(self):
        """Test combining memory contexts with procedural tool patterns."""
        # Arrange
        semantic_memories = []
        episodic_memories = []
        procedural_memories = [
            {"content": {"tool": "search_tool", "arguments": {"query": "test", "limit": 10}}},
            {"content": {"successful_pattern": "tool_assisted_search"}}
        ]
        
        # Act
        result = self.memory_utils.combine_memory_contexts(
            semantic_memories, episodic_memories, procedural_memories
        )
        
        # Assert
        assert "For similar queries, successfully used search_tool with args: {'query': 'test', 'limit': 10}" in result
        assert "Successful approach: tool_assisted_search" in result

    def test_retrieve_memory_context_integration(self):
        """Test the complete memory context retrieval flow."""
        # Arrange
        user_id = "test_user"
        query = "test query"
        
        # Mock all the individual methods to return realistic data
        semantic_memories = [(Document(page_content="Test fact"), 0.85)]
        episodic_memories = [{"content": {"message": {"content": "Test interaction"}}}]
        procedural_memories = [{"content": {"tool": "test_tool"}}]
        
        with patch.object(self.memory_utils, 'get_semantic_context', return_value=semantic_memories), \
             patch.object(self.memory_utils, 'get_episodic_context', return_value=episodic_memories), \
             patch.object(self.memory_utils, 'get_procedural_context', return_value=procedural_memories):
            
            # Act
            result = self.memory_utils.retrieve_memory_context(user_id, query)
            
            # Assert
            assert "Relevant information from memory:" in result
            assert "Fact: Test fact (relevance: 0.85)" in result
            assert "Past interaction: Test interaction" in result
            assert "For similar queries, successfully used test_tool with args: {}" in result
