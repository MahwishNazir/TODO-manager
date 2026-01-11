---
name: task-service-crud-operations
description: SQLModel-based task service implementation with user validation for Todo application Phase 2. Includes CRUD operations with proper user isolation and security validation.
---

# Task Service CRUD Operations for Todo Application

## Instructions

Use this skill when implementing the task service layer for the Todo application in Phase 2. Follow these guidelines for proper implementation with user validation and security:

### 1. Service Layer Architecture
- Implement business logic in service layer separate from API endpoints
- Validate user_id in all operations to ensure data isolation
- Use proper error handling with meaningful messages
- Include logging for debugging and monitoring

### 2. Create Operations
- Validate input data before creation
- Set user_id from authenticated context (not from request body)
- Include proper error handling with rollback mechanisms
- Log successful operations

### 3. Read Operations
- Implement efficient queries with proper filtering by user_id
- Use indexing strategies for performance with Neon Serverless
- Implement pagination for list operations
- Include proper error handling for missing records

### 4. Update Operations
- Validate that user owns the task before updating
- Handle partial updates with exclude_unset
- Validate data before updating
- Update timestamps appropriately
- Include proper error handling for non-existent records

### 5. Delete Operations
- Validate that user owns the task before deletion
- Include proper error handling for non-existent records
- Use soft deletes if needed for audit trails
- Include logging for deletion operations

### 6. Security Considerations (Phase 2 Critical!)
- **CRITICAL**: Always validate user_id in all operations
- Ensure data isolation between users
- Use proper filtering by user_id in all queries
- Validate JWT user_id matches operation user_id
- Never allow cross-user data access

### 7. Neon-Optimized Queries
- Use index-optimized ordering and limit/offset
- Implement proper connection handling
- Use appropriate timeouts for Neon connections
- Handle connection timeouts gracefully

### 8. Error Handling
- Implement proper error responses with appropriate HTTP status codes
- Handle database-specific exceptions
- Provide meaningful error messages without exposing sensitive information
- Log errors for debugging and monitoring

## Examples

### Example 1: Task Service with User Validation
```python
# backend/src/services/task_service.py
from sqlmodel import select, Session
from typing import List, Optional
from datetime import datetime
from ..models.task import Task, TaskCreate, TaskUpdate
from fastapi import HTTPException, status
import logging

# Set up logging for database operations
logger = logging.getLogger(__name__)

class TaskService:
    @staticmethod
    def create_task(session: Session, user_id: str, task_create: TaskCreate) -> Task:
        """Create a new task for a user with Neon-optimized operations"""
        try:
            task = Task(
                **task_create.dict(),
                user_id=user_id  # Set user_id from authenticated context, never from request
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            logger.info(f"Created task {task.id} for user {user_id}")
            return task
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating task for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )

    @staticmethod
    def get_task_by_id(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        """Get a specific task by ID for a user - optimized for Neon Serverless"""
        try:
            statement = select(Task).where(
                (Task.id == task_id) & (Task.user_id == user_id)  # CRITICAL: Verify ownership
            )
            task = session.exec(statement).first()
            if task:
                logger.info(f"Retrieved task {task_id} for user {user_id}")
            else:
                logger.info(f"Task {task_id} not found for user {user_id}")
            return task
        except Exception as e:
            logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve task"
            )

    @staticmethod
    def get_tasks_by_user(
        session: Session,
        user_id: str,
        completed: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Task]:
        """Get all tasks for a user with optional filtering - Neon-optimized query"""
        try:
            statement = select(Task).where(Task.user_id == user_id)

            if completed is not None:
                statement = statement.where(Task.completed == completed)

            # Use index-optimized ordering and limit/offset for Neon performance
            statement = statement.offset(offset).limit(limit).order_by(Task.created_at.desc())
            tasks = session.exec(statement).all()
            logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tasks"
            )

    @staticmethod
    def update_task(
        session: Session,
        task_id: int,
        user_id: str,
        task_update: TaskUpdate
    ) -> Optional[Task]:
        """Update an existing task with Neon-optimized operations"""
        try:
            task = TaskService.get_task_by_id(session, task_id, user_id)
            if not task:
                logger.warning(f"Update requested for non-existent task {task_id} by user {user_id}")
                return None

            # Update only fields that are provided
            update_data = task_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(task, field, value)

            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            logger.info(f"Updated task {task_id} for user {user_id}")
            return task
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task"
            )

    @staticmethod
    def delete_task(session: Session, task_id: int, user_id: str) -> bool:
        """Delete a task by ID for a user - Neon-optimized deletion"""
        try:
            task = TaskService.get_task_by_id(session, task_id, user_id)
            if not task:
                logger.warning(f"Delete requested for non-existent task {task_id} by user {user_id}")
                return False

            session.delete(task)
            session.commit()
            logger.info(f"Deleted task {task_id} for user {user_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )

    @staticmethod
    def toggle_task_completion(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        """Toggle the completion status of a task - optimized for Neon"""
        try:
            task = TaskService.get_task_by_id(session, task_id, user_id)
            if not task:
                logger.warning(f"Toggle completion requested for non-existent task {task_id} by user {user_id}")
                return None

            task.completed = not task.completed
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            logger.info(f"Toggled completion for task {task_id} for user {user_id}")
            return task
        except Exception as e:
            session.rollback()
            logger.error(f"Error toggling completion for task {task_id} for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle task completion"
            )
```

### Example 2: Bulk Operations
```python
# backend/src/services/task_service.py
from typing import List

class TaskService:
    @staticmethod
    def bulk_create_tasks(session: Session, user_id: str, tasks_create: List[TaskCreate]) -> List[Task]:
        """Create multiple tasks for a user in a single transaction"""
        try:
            created_tasks = []
            for task_create in tasks_create:
                task = Task(
                    **task_create.dict(),
                    user_id=user_id  # Set user_id from authenticated context
                )
                session.add(task)
                created_tasks.append(task)

            session.commit()
            for task in created_tasks:
                session.refresh(task)

            logger.info(f"Bulk created {len(created_tasks)} tasks for user {user_id}")
            return created_tasks
        except Exception as e:
            session.rollback()
            logger.error(f"Error bulk creating tasks for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create tasks"
            )

    @staticmethod
    def bulk_delete_tasks(session: Session, task_ids: List[int], user_id: str) -> int:
        """Delete multiple tasks for a user"""
        try:
            statement = select(Task).where(
                (Task.id.in_(task_ids)) & (Task.user_id == user_id)  # CRITICAL: Verify ownership
            )
            tasks = session.exec(statement).all()

            deleted_count = 0
            for task in tasks:
                session.delete(task)
                deleted_count += 1

            session.commit()
            logger.info(f"Bulk deleted {deleted_count} tasks for user {user_id}")
            return deleted_count
        except Exception as e:
            session.rollback()
            logger.error(f"Error bulk deleting tasks for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete tasks"
            )
```

## Best Practices

- **CRITICAL**: Always validate that user_id in operations matches the authenticated user from JWT
- Use SQLModel's field constraints for data validation at the model level
- Implement proper error handling for database-specific exceptions with logging
- Use pagination for list operations to prevent performance issues (limit/offset with proper indexing)
- Optimize queries using proper indexing and relationship loading strategies for Neon
- Implement connection pooling appropriate for serverless environments (pool_size=5, max_overflow=10)
- Use parameterized queries to prevent SQL injection (SQLModel handles this automatically)
- Monitor query performance and optimize slow queries with Neon's query insights
- Implement proper logging for database operations with structured logging
- Test database operations with concurrent access patterns
- Follow SQLModel best practices for model relationships with proper indexing
- Implement proper access controls based on user authentication (validate user_id in JWT matches operation user_id)
- Implement retry logic for transient database failures with exponential backoff
- Monitor connection pool usage and adjust settings as needed for traffic patterns
- Create indexes on frequently queried fields (user_id, created_at, completed status)
- Implement structured logging to track database operations and performance
- Handle database connection timeouts gracefully with proper error responses
- Use Neon's built-in monitoring and performance insights to optimize queries
- Follow Phase 2 security requirements: validate JWT user_id matches operation user_id in all endpoints
- Implement proper resource cleanup to avoid connection leaks in serverless environment
- Use exclude_unset=True when updating to only update provided fields
- Validate input data before performing operations
- Use appropriate HTTP status codes for different error conditions
- Include meaningful error messages for debugging
- Use datetime.utcnow() for consistent timestamp generation
- Handle edge cases like non-existent records appropriately
- Implement proper transaction management for multi-step operations
- Use select() with appropriate filters to ensure data isolation
- Validate user permissions before allowing operations
- Implement proper session management with rollback mechanisms