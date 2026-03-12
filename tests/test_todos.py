"""
Unit tests for Todo API endpoints
Tests all CRUD operations and filtering/sorting
"""

import unittest
import json
import tempfile
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from todo_manager import TodoManager, TodoStatus, TodoPriority


class TestTodoManager(unittest.TestCase):
    """Test the TodoManager class"""
    
    def setUp(self):
        """Create a temporary directory for test data"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = TodoManager(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_todo(self):
        """Test creating a new todo"""
        todo = self.manager.create_todo(
            title="Test Todo",
            description="Test Description",
            status="pending",
            priority="high",
            tags=["test", "todo"]
        )
        
        self.assertIsNotNone(todo)
        self.assertEqual(todo.title, "Test Todo")
        self.assertEqual(todo.description, "Test Description")
        self.assertEqual(todo.status, TodoStatus.PENDING)
        self.assertEqual(todo.priority, TodoPriority.HIGH)
        self.assertEqual(todo.tags, ["test", "todo"])
        self.assertIsNotNone(todo.id)
    
    def test_get_todo(self):
        """Test retrieving a todo by ID"""
        created = self.manager.create_todo(title="Get Test")
        retrieved = self.manager.get_todo(created.id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, created.id)
        self.assertEqual(retrieved.title, "Get Test")
    
    def test_get_todo_not_found(self):
        """Test retrieving a non-existent todo"""
        result = self.manager.get_todo("non-existent-id")
        self.assertIsNone(result)
    
    def test_get_all_todos(self):
        """Test retrieving all todos"""
        self.manager.create_todo(title="Todo 1")
        self.manager.create_todo(title="Todo 2")
        self.manager.create_todo(title="Todo 3")
        
        todos = self.manager.get_all_todos()
        self.assertEqual(len(todos), 3)
    
    def test_filter_by_status(self):
        """Test filtering todos by status"""
        self.manager.create_todo(title="Pending", status="pending")
        self.manager.create_todo(title="Completed", status="completed")
        self.manager.create_todo(title="In Progress", status="in_progress")
        
        pending = self.manager.get_all_todos(status="pending")
        completed = self.manager.get_all_todos(status="completed")
        
        self.assertEqual(len(pending), 1)
        self.assertEqual(len(completed), 1)
        self.assertEqual(pending[0].title, "Pending")
        self.assertEqual(completed[0].title, "Completed")
    
    def test_filter_by_priority(self):
        """Test filtering todos by priority"""
        self.manager.create_todo(title="High", priority="high")
        self.manager.create_todo(title="Medium", priority="medium")
        self.manager.create_todo(title="Low", priority="low")
        
        high_priority = self.manager.get_all_todos(priority="high")
        self.assertEqual(len(high_priority), 1)
        self.assertEqual(high_priority[0].title, "High")
    
    def test_filter_by_tags(self):
        """Test filtering todos by tags"""
        self.manager.create_todo(title="Work", tags=["work", "urgent"])
        self.manager.create_todo(title="Personal", tags=["personal"])
        self.manager.create_todo(title="Work Urgent", tags=["work", "urgent"])
        
        work_todos = self.manager.get_all_todos(tags=["work"])
        self.assertEqual(len(work_todos), 2)
    
    def test_sort_by_priority(self):
        """Test sorting todos by priority"""
        self.manager.create_todo(title="Low", priority="low")
        self.manager.create_todo(title="High", priority="high")
        self.manager.create_todo(title="Medium", priority="medium")
        
        sorted_todos = self.manager.get_all_todos(sort_by="priority", sort_order="desc")
        self.assertEqual(sorted_todos[0].priority, TodoPriority.HIGH)
        self.assertEqual(sorted_todos[1].priority, TodoPriority.MEDIUM)
        self.assertEqual(sorted_todos[2].priority, TodoPriority.LOW)
    
    def test_update_todo(self):
        """Test updating a todo"""
        todo = self.manager.create_todo(title="Original")
        
        updated = self.manager.update_todo(
            todo.id,
            title="Updated",
            description="New description",
            status="completed"
        )
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated.title, "Updated")
        self.assertEqual(updated.description, "New description")
        self.assertEqual(updated.status, TodoStatus.COMPLETED)
        self.assertIsNotNone(updated.completed_at)
    
    def test_complete_todo(self):
        """Test marking a todo as completed"""
        todo = self.manager.create_todo(title="To Complete")
        completed = self.manager.complete_todo(todo.id)
        
        self.assertIsNotNone(completed)
        self.assertEqual(completed.status, TodoStatus.COMPLETED)
        self.assertIsNotNone(completed.completed_at)
    
    def test_delete_todo(self):
        """Test deleting a todo"""
        todo = self.manager.create_todo(title="To Delete")
        result = self.manager.delete_todo(todo.id)
        
        self.assertTrue(result)
        self.assertIsNone(self.manager.get_todo(todo.id))
    
    def test_delete_todo_not_found(self):
        """Test deleting a non-existent todo"""
        result = self.manager.delete_todo("non-existent-id")
        self.assertFalse(result)
    
    def test_get_stats(self):
        """Test getting todo statistics"""
        self.manager.create_todo(title="1", status="completed")
        self.manager.create_todo(title="2", status="pending")
        self.manager.create_todo(title="3", status="pending", priority="high")
        
        stats = self.manager.get_stats()
        
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["pending"], 2)
        self.assertEqual(stats["priority_distribution"]["high"], 1)
        self.assertAlmostEqual(stats["completion_rate"], 33.33, places=2)
    
    def test_search_todos(self):
        """Test searching todos"""
        self.manager.create_todo(title="Project Alpha", description="Important work")
        self.manager.create_todo(title="Shopping List", description="Buy groceries")
        self.manager.create_todo(title="Another Project", tags=["work"])
        
        results = self.manager.search_todos("project")
        self.assertEqual(len(results), 2)
        
        results = self.manager.search_todos("groceries")
        self.assertEqual(len(results), 1)
        
        results = self.manager.search_todos("work")
        self.assertEqual(len(results), 2)
    
    def test_persistence(self):
        """Test that todos are saved and loaded correctly"""
        todo = self.manager.create_todo(title="Persistent")
        todo_id = todo.id
        
        # Create a new manager instance (simulates app restart)
        new_manager = TodoManager(data_dir=self.temp_dir)
        loaded_todo = new_manager.get_todo(todo_id)
        
        self.assertIsNotNone(loaded_todo)
        self.assertEqual(loaded_todo.title, "Persistent")


class TestTodoModel(unittest.TestCase):
    """Test the Todo model class"""
    
    def test_todo_to_dict(self):
        """Test converting todo to dictionary"""
        from todo_manager import Todo
        
        todo = Todo(
            title="Dict Test",
            description="Test description",
            status=TodoStatus.IN_PROGRESS,
            priority=TodoPriority.HIGH
        )
        
        data = todo.to_dict()
        
        self.assertEqual(data["title"], "Dict Test")
        self.assertEqual(data["description"], "Test description")
        self.assertEqual(data["status"], "in_progress")
        self.assertEqual(data["priority"], "high")
        self.assertIn("id", data)
        self.assertIn("created_at", data)
    
    def test_todo_from_dict(self):
        """Test creating todo from dictionary"""
        from todo_manager import Todo
        
        data = {
            "id": "test-id-123",
            "title": "From Dict",
            "description": "Description",
            "status": "completed",
            "priority": "low",
            "tags": ["tag1", "tag2"],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
            "completed_at": "2024-01-02T00:00:00"
        }
        
        todo = Todo.from_dict(data)
        
        self.assertEqual(todo.id, "test-id-123")
        self.assertEqual(todo.title, "From Dict")
        self.assertEqual(todo.status, TodoStatus.COMPLETED)
        self.assertEqual(todo.priority, TodoPriority.LOW)
        self.assertEqual(todo.tags, ["tag1", "tag2"])


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoint integration"""
    
    def setUp(self):
        """Set up test client"""
        from fastapi.testclient import TestClient
        from visioncraft_server import app, todo_manager
        
        self.client = TestClient(app)
        self.todo_manager = todo_manager
        
        # Clear existing todos
        self.todo_manager.todos.clear()
        self.todo_manager._save_todos()
    
    def test_create_todo_endpoint(self):
        """Test POST /todos endpoint"""
        response = self.client.post("/todos", json={
            "title": "API Test Todo",
            "description": "Created via API",
            "priority": "high"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "API Test Todo")
        self.assertEqual(data["priority"], "high")
        self.assertIn("id", data)
    
    def test_get_todos_endpoint(self):
        """Test GET /todos endpoint"""
        # Create some todos
        self.todo_manager.create_todo(title="Todo 1")
        self.todo_manager.create_todo(title="Todo 2")
        
        response = self.client.get("/todos")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["todos"]), 2)
    
    def test_get_todo_by_id_endpoint(self):
        """Test GET /todos/{id} endpoint"""
        todo = self.todo_manager.create_todo(title="Specific Todo")
        
        response = self.client.get(f"/todos/{todo.id}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Specific Todo")
    
    def test_get_todo_not_found(self):
        """Test GET /todos/{id} with non-existent ID"""
        response = self.client.get("/todos/non-existent-id")
        self.assertEqual(response.status_code, 404)
    
    def test_update_todo_endpoint(self):
        """Test PUT /todos/{id} endpoint"""
        todo = self.todo_manager.create_todo(title="Original")
        
        response = self.client.put(f"/todos/{todo.id}", json={
            "title": "Updated Title",
            "status": "completed"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Updated Title")
        self.assertEqual(data["status"], "completed")
    
    def test_delete_todo_endpoint(self):
        """Test DELETE /todos/{id} endpoint"""
        todo = self.todo_manager.create_todo(title="To Delete")
        
        response = self.client.delete(f"/todos/{todo.id}")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        
        # Verify it's gone
        response = self.client.get(f"/todos/{todo.id}")
        self.assertEqual(response.status_code, 404)
    
    def test_complete_todo_endpoint(self):
        """Test POST /todos/{id}/complete endpoint"""
        todo = self.todo_manager.create_todo(title="To Complete")
        
        response = self.client.post(f"/todos/{todo.id}/complete")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")
    
    def test_get_todo_stats_endpoint(self):
        """Test GET /todos/stats endpoint"""
        self.todo_manager.create_todo(title="1", status="completed")
        self.todo_manager.create_todo(title="2", status="pending")
        
        response = self.client.get("/todos/stats")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["completed"], 1)
        self.assertEqual(data["pending"], 1)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTodoManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTodoModel))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
