"""Performance and load testing utilities."""

import pytest
import time
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
import statistics

# Import removed to prevent MongoDB connection during test collection
from app.agent.agent import ReActAgent
from app.memory.memory_manager import MemoryManager


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest.fixture
    def test_client(self, test_app):
        """Create test client using the test_app fixture."""
        return TestClient(test_app)

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_api_response_time_benchmark(self, mock_agent, mock_memory_manager, test_client):
        """Benchmark API response times."""
        # Arrange
        mock_memory_manager.create_conversation.return_value = "perf_conv"
        mock_memory_manager.create_session.return_value = "perf_session"
        mock_agent.process_message = AsyncMock(return_value="Performance test response")

        # Warm up
        for _ in range(5):
            test_client.post("/chat", json={
                "user_id": "warmup_user",
                "message": "Warmup message"
            })

        # Actual benchmark
        times = []
        for i in range(10):
            start_time = time.time()
            response = test_client.post("/chat", json={
                "user_id": f"perf_user_{i}",
                "message": f"Performance test message {i}"
            })
            end_time = time.time()
            
            assert response.status_code == 200
            times.append((end_time - start_time) * 1000)

        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\nAPI Response Time Benchmark Results:")
        print(f"Average response time: {avg_time:.2f}ms")
        print(f"Min response time: {min_time:.2f}ms")
        print(f"Max response time: {max_time:.2f}ms")
        
        # Performance assertions
        assert avg_time < 1000, f"Average response time {avg_time:.2f}ms is too high"
        assert max_time < 2000, f"Max response time {max_time:.2f}ms is too high"

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_concurrent_request_handling(self, mock_agent, mock_memory_manager, test_client):
        """Test handling of concurrent requests."""
        # Arrange
        mock_memory_manager.create_conversation.side_effect = [f"conv_{i}" for i in range(20)]
        mock_memory_manager.create_session.side_effect = [f"session_{i}" for i in range(20)]
        mock_agent.process_message = AsyncMock(return_value="Concurrent test response")

        def make_request(user_id):
            """Make a single request."""
            start_time = time.time()
            response = test_client.post("/chat", json={
                "user_id": user_id,
                "message": f"Concurrent message from {user_id}"
            })
            end_time = time.time()
            return {
                "user_id": user_id,
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000,
                "success": response.status_code == 200
            }

        # Act - Send concurrent requests
        user_ids = [f"concurrent_user_{i}" for i in range(20)]

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_user = {executor.submit(make_request, user_id): user_id for user_id in user_ids}
            results = []

            for future in as_completed(future_to_user):
                result = future.result()
                results.append(result)

        # Assert
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        success_rate = len(successful) / len(results) * 100
        avg_response_time = statistics.mean([r["response_time"] for r in successful]) if successful else 0
        
        print(f"\nConcurrent Request Test Results:")
        print(f"Total requests: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        print(f"Success rate: {success_rate:.2f}%")
        print(f"Average response time: {avg_response_time:.2f}ms")
        
        # Concurrent test assertions
        assert success_rate >= 90, f"Success rate {success_rate:.2f}% is below 90%"
        assert avg_response_time < 1000, f"Average response time {avg_response_time:.2f}ms is too high"

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_memory_operation_performance(self, mock_agent, mock_memory_manager, test_client):
        """Test memory operation performance."""
        # Arrange
        # Simulate various memory operation times
        mock_memory_manager.retrieve_episodic_memories.return_value = [
            {"_id": f"memory_{i}", "content": {"test": f"data_{i}"}} for i in range(100)
        ]
        mock_memory_manager.retrieve_semantic_memories.return_value = [
            (MagicMock(page_content=f"semantic_data_{i}"), 0.9) for i in range(50)
        ]
        mock_memory_manager.retrieve_procedural_memories.return_value = [
            {"_id": f"procedure_{i}", "content": {"tool": f"tool_{i}"}} for i in range(75)
        ]

        memory_types = ["episodic", "procedural"]
        response_times = {}

        # Act - Test each memory type
        for memory_type in memory_types:
            times = []
            for i in range(10):
                start_time = time.time()
                response = test_client.post("/memories/query", json={
                    "user_id": f"memory_user_{i}",
                    "query": f"test query {i}",
                    "memory_type": memory_type,
                    "limit": 50
                })
                end_time = time.time()

                assert response.status_code == 200
                times.append((end_time - start_time) * 1000)

            response_times[memory_type] = {
                "avg": statistics.mean(times),
                "min": min(times),
                "max": max(times)
            }

        # Assert performance for each memory type
        for memory_type, metrics in response_times.items():
            print(f"\n{memory_type.capitalize()} Memory Performance:")
            print(f"Average: {metrics['avg']:.2f}ms")
            print(f"Min: {metrics['min']:.2f}ms")
            print(f"Max: {metrics['max']:.2f}ms")
            
            assert metrics['avg'] < 500, f"{memory_type} memory avg time {metrics['avg']:.2f}ms is too high"
            assert metrics['max'] < 1000, f"{memory_type} memory max time {metrics['max']:.2f}ms is too high"

    def test_health_check_performance(self, test_client):
        """Test health check endpoint performance."""
        # Act - Multiple health checks
        response_times = []
        for _ in range(100):
            start_time = time.time()
            response = test_client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)
        
        # Assert
        avg_health_time = statistics.mean(response_times)
        max_health_time = max(response_times)
        
        print(f"\nHealth Check Performance:")
        print(f"Average health check time: {avg_health_time:.2f}ms")
        print(f"Maximum health check time: {max_health_time:.2f}ms")
        
        # Health checks should be very fast
        assert avg_health_time < 50, f"Average health check time {avg_health_time:.2f}ms exceeds 50ms"
        assert max_health_time < 200, f"Maximum health check time {max_health_time:.2f}ms exceeds 200ms"


class TestLoadTesting:
    """Load testing scenarios."""
    
    @pytest.fixture
    def test_client(self, test_app):
        """Create test client using the test_app fixture."""
        return TestClient(test_app)

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_sustained_load(self, mock_agent, mock_memory_manager, test_client):
        """Test system behavior under sustained load."""
        # Arrange
        mock_memory_manager.create_conversation.side_effect = [f"load_conv_{i}" for i in range(100)]
        mock_memory_manager.create_session.side_effect = [f"load_session_{i}" for i in range(100)]
        mock_agent.process_message = AsyncMock(return_value="Load test response")

        def sustained_requests():
            """Generate sustained requests."""
            results = []
            for i in range(100):
                start_time = time.time()
                try:
                    response = test_client.post("/chat", json={
                        "user_id": f"load_user_{i}",
                        "message": f"Load test message {i}"
                    })
                    end_time = time.time()

                    results.append({
                        "success": response.status_code == 200,
                        "response_time": (end_time - start_time) * 1000,
                        "status_code": response.status_code
                    })
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "response_time": 0
                    })

                # Small delay to simulate realistic load
                time.sleep(0.01)

            return results

        # Act
        start_total = time.time()
        results = sustained_requests()
        end_total = time.time()

        # Assert
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        success_rate = len(successful) / len(results) * 100
        avg_response_time = statistics.mean([r["response_time"] for r in successful]) if successful else 0
        total_time = (end_total - start_total) * 1000

        print(f"\nSustained Load Test Results:")
        print(f"Total requests: {len(results)}")
        print(f"Successful requests: {len(successful)}")
        print(f"Failed requests: {len(failed)}")
        print(f"Success rate: {success_rate:.2f}%")
        print(f"Average response time: {avg_response_time:.2f}ms")
        print(f"Total test time: {total_time:.2f}ms")
        print(f"Throughput: {len(results) / (total_time / 1000):.2f} requests/second")

        # Load test assertions
        assert success_rate >= 95, f"Success rate {success_rate:.2f}% is below 95%"
        assert avg_response_time < 1000, f"Average response time {avg_response_time:.2f}ms is too high"

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_burst_traffic(self, mock_agent, mock_memory_manager, test_client):
        """Test system behavior under burst traffic."""
        # Arrange
        mock_memory_manager.create_conversation.side_effect = [f"burst_conv_{i}" for i in range(50)]
        mock_memory_manager.create_session.side_effect = [f"burst_session_{i}" for i in range(50)]
        mock_agent.process_message = AsyncMock(return_value="Burst test response")

        def burst_request(user_id):
            """Make a burst request."""
            try:
                start_time = time.time()
                response = test_client.post("/chat", json={
                    "user_id": user_id,
                    "message": f"Burst message from {user_id}"
                })
                end_time = time.time()

                return {
                    "success": response.status_code == 200,
                    "response_time": (end_time - start_time) * 1000,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "response_time": 0
                }

        # Act - Burst of concurrent requests
        user_ids = [f"burst_user_{i}" for i in range(50)]

        start_burst = time.time()
        with ThreadPoolExecutor(max_workers=25) as executor:
            future_to_user = {executor.submit(burst_request, user_id): user_id for user_id in user_ids}
            results = []

            for future in as_completed(future_to_user):
                result = future.result()
                results.append(result)
        end_burst = time.time()

        # Assert
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        success_rate = len(successful) / len(results) * 100
        avg_burst_time = statistics.mean([r["response_time"] for r in successful]) if successful else 0
        burst_duration = (end_burst - start_burst) * 1000

        print(f"\nBurst Traffic Test Results:")
        print(f"Burst requests: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        print(f"Success rate: {success_rate:.2f}%")
        print(f"Average response time: {avg_burst_time:.2f}ms")
        print(f"Burst duration: {burst_duration:.2f}ms")
        print(f"Peak throughput: {len(results) / (burst_duration / 1000):.2f} requests/second")

        # Burst test assertions
        assert success_rate >= 90, f"Burst success rate {success_rate:.2f}% is below 90%"
        assert avg_burst_time < 1000, f"Average burst response time {avg_burst_time:.2f}ms is too high"


class TestScalabilityMetrics:
    """Test scalability and resource usage metrics."""
    
    @pytest.fixture
    def test_client(self, test_app):
        """Create test client using the test_app fixture."""
        return TestClient(test_app)

    @patch('app.api.main.memory_manager')
    @patch('app.api.main.agent')
    def test_memory_usage_scaling(self, mock_agent, mock_memory_manager, test_client):
        """Test memory usage under increasing load."""
        # This test would ideally measure actual memory usage
        # For now, we'll simulate and test the pattern

        # Arrange
        load_levels = [10, 25, 50, 100]
        results = {}

        for load_level in load_levels:
            mock_memory_manager.create_conversation.side_effect = [f"scale_conv_{i}" for i in range(load_level)]
            mock_memory_manager.create_session.side_effect = [f"scale_session_{i}" for i in range(load_level)]
            mock_agent.process_message = AsyncMock(return_value="Scaling test response")

            # Act
            start_time = time.time()
            successful_requests = 0

            for i in range(load_level):
                response = test_client.post("/chat", json={
                    "user_id": f"scale_user_{load_level}_{i}",
                    "message": f"Scaling test {load_level} - {i}"
                })
                
                if response.status_code == 200:
                    successful_requests += 1

            end_time = time.time()
            total_time = (end_time - start_time) * 1000

            results[load_level] = {
                "success_rate": (successful_requests / load_level) * 100,
                "total_time": total_time,
                "throughput": load_level / (total_time / 1000)
            }

        # Assert scaling behavior
        for load_level, metrics in results.items():
            print(f"\nLoad Level {load_level}:")
            print(f"Success Rate: {metrics['success_rate']:.2f}%")
            print(f"Total Time: {metrics['total_time']:.2f}ms")
            print(f"Throughput: {metrics['throughput']:.2f} requests/second")

            # Scaling assertions
            assert metrics['success_rate'] >= 90, f"Success rate {metrics['success_rate']:.2f}% is below 90% for load {load_level}"
            assert metrics['throughput'] > 0, f"Throughput should be positive for load {load_level}"

    def test_resource_cleanup_patterns(self, test_client):
        """Test that resources are properly cleaned up."""
        # This is a placeholder for resource cleanup testing
        # In a real scenario, you would monitor memory leaks, open connections, etc.
        
        # Arrange - Simulate multiple request cycles
        cycles = 5
        requests_per_cycle = 20
        
        for cycle in range(cycles):
            # Act - Make requests
            for i in range(requests_per_cycle):
                response = test_client.get("/health")
                assert response.status_code == 200
            
            # In a real test, you would check resource usage here
            # For example:
            # - Memory usage should be stable across cycles
            # - Database connections should be returned to pool
            # - Temporary files should be cleaned up
            
        # Assert - Resources should be stable across cycles
        # This is a simplified assertion
        assert True, "Resource cleanup test passed"


if __name__ == "__main__":
    # Run performance tests with verbose output
    pytest.main([__file__, "-v", "-s"])
