"""
Todo Manager for VisionCraft Pro
Manages todo list with CRUD operations, filtering, and persistence
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class TodoStatus(str, Enum):
    """Todo status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TodoPriority(str, Enum):
    """Todo priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo:
    """Todo item model"""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        status: TodoStatus = TodoStatus.PENDING,
        priority: TodoPriority = TodoPriority.MEDIUM,
        tags: List[str] = None,
        due_date: Optional[str] = None,
        todo_id: str = None
    ):
        self.id = todo_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = status if isinstance(status, TodoStatus) else TodoStatus(status)
        self.priority = priority if isinstance(priority, TodoPriority) else TodoPriority(priority)
        self.tags = tags or []
        self.due_date = due_date
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert todo to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "tags": self.tags,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Todo':
        """Create todo from dictionary"""
        todo = cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            status=TodoStatus(data.get("status", "pending")),
            priority=TodoPriority(data.get("priority", "medium")),
            tags=data.get("tags", []),
            due_date=data.get("due_date"),
            todo_id=data.get("id")
        )
        todo.created_at = data.get("created_at", todo.created_at)
        todo.updated_at = data.get("updated_at", todo.updated_at)
        todo.completed_at = data.get("completed_at")
        return todo


class TodoManager:
    """Manages todo list operations with JSON persistence"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.todos_file = os.path.join(data_dir, "todos.json")
        self.todos: Dict[str, Todo] = {}
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing todos
        self._load_todos()
    
    def _load_todos(self):
        """Load todos from JSON file"""
        if os.path.exists(self.todos_file):
            try:
                with open(self.todos_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for todo_data in data:
                        todo = Todo.from_dict(todo_data)
                        self.todos[todo.id] = todo
                print(f"[TODO] Loaded {len(self.todos)} todos")
            except Exception as e:
                print(f"[TODO] Error loading todos: {e}")
                self.todos = {}
    
    def _save_todos(self):
        """Save todos to JSON file"""
        try:
            data = [todo.to_dict() for todo in self.todos.values()]
            with open(self.todos_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[TODO] Error saving todos: {e}")
    
    def create_todo(
        self,
        title: str,
        description: str = "",
        status: str = "pending",
        priority: str = "medium",
        tags: List[str] = None,
        due_date: Optional[str] = None
    ) -> Todo:
        """Create a new todo"""
        todo = Todo(
            title=title,
            description=description,
            status=TodoStatus(status),
            priority=TodoPriority(priority),
            tags=tags or [],
            due_date=due_date
        )
        self.todos[todo.id] = todo
        self._save_todos()
        print(f"[TODO] Created todo: {todo.id}")
        return todo
    
    def get_todo(self, todo_id: str) -> Optional[Todo]:
        """Get a specific todo by ID"""
        return self.todos.get(todo_id)
    
    def get_all_todos(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: List[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Todo]:
        """Get all todos with optional filtering and sorting"""
        todos = list(self.todos.values())
        
        # Apply filters
        if status:
            todos = [t for t in todos if t.status.value == status]
        
        if priority:
            todos = [t for t in todos if t.priority.value == priority]
        
        if tags:
            todos = [t for t in todos if any(tag in t.tags for tag in tags)]
        
        # Apply sorting
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "priority":
            priority_order = {"high": 3, "medium": 2, "low": 1}
            todos.sort(key=lambda t: priority_order.get(t.priority.value, 0), reverse=reverse)
        elif sort_by == "status":
            status_order = {"pending": 1, "in_progress": 2, "completed": 3, "archived": 4}
            todos.sort(key=lambda t: status_order.get(t.status.value, 0), reverse=reverse)
        elif sort_by == "due_date":
            todos.sort(key=lambda t: t.due_date or "9999-12-31", reverse=reverse)
        else:  # created_at or updated_at
            todos.sort(key=lambda t: getattr(t, sort_by, t.created_at), reverse=reverse)
        
        return todos
    
    def update_todo(
        self,
        todo_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None
    ) -> Optional[Todo]:
        """Update a todo"""
        todo = self.todos.get(todo_id)
        if not todo:
            return None
        
        if title is not None:
            todo.title = title
        if description is not None:
            todo.description = description
        if status is not None:
            todo.status = TodoStatus(status)
            if status == "completed" and not todo.completed_at:
                todo.completed_at = datetime.now().isoformat()
            elif status != "completed":
                todo.completed_at = None
        if priority is not None:
            todo.priority = TodoPriority(priority)
        if tags is not None:
            todo.tags = tags
        if due_date is not None:
            todo.due_date = due_date
        
        todo.updated_at = datetime.now().isoformat()
        self._save_todos()
        print(f"[TODO] Updated todo: {todo_id}")
        return todo
    
    def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo"""
        if todo_id in self.todos:
            del self.todos[todo_id]
            self._save_todos()
            print(f"[TODO] Deleted todo: {todo_id}")
            return True
        return False
    
    def complete_todo(self, todo_id: str) -> Optional[Todo]:
        """Mark a todo as completed"""
        return self.update_todo(
            todo_id,
            status="completed",
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get todo statistics"""
        total = len(self.todos)
        completed = sum(1 for t in self.todos.values() if t.status == TodoStatus.COMPLETED)
        pending = sum(1 for t in self.todos.values() if t.status == TodoStatus.PENDING)
        in_progress = sum(1 for t in self.todos.values() if t.status == TodoStatus.IN_PROGRESS)
        
        high_priority = sum(1 for t in self.todos.values() if t.priority == TodoPriority.HIGH)
        medium_priority = sum(1 for t in self.todos.values() if t.priority == TodoPriority.MEDIUM)
        low_priority = sum(1 for t in self.todos.values() if t.priority == TodoPriority.LOW)
        
        # Get all unique tags
        all_tags = set()
        for todo in self.todos.values():
            all_tags.update(todo.tags)
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "priority_distribution": {
                "high": high_priority,
                "medium": medium_priority,
                "low": low_priority
            },
            "tags": list(all_tags)
        }
    
    def search_todos(self, query: str) -> List[Todo]:
        """Search todos by title or description"""
        query_lower = query.lower()
        results = []
        for todo in self.todos.values():
            if (query_lower in todo.title.lower() or 
                query_lower in todo.description.lower() or
                any(query_lower in tag.lower() for tag in todo.tags)):
                results.append(todo)
        return results
