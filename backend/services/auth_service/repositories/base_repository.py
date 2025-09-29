"""
Base repository pattern implementation.

This module provides the base repository class with common CRUD operations
that can be extended by specific entity repositories.
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from abc import ABC, abstractmethod
import uuid

# Generic type for database models
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Base repository class with common CRUD operations.
    
    Requirements: 1.1, 1.2, 1.5, 1.6
    - Standardized database operations
    - Error handling and transaction management
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository with model and database session.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def get_by_id(self, entity_id: uuid.UUID) -> Optional[ModelType]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            Entity instance or None if not found
        """
        return self.db.query(self.model).filter(
            getattr(self.model, self._get_id_field()) == entity_id
        ).first()
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get all entities with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply
            
        Returns:
            List of entity instances
        """
        query = self.db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create new entity.
        
        Args:
            obj_in: Creation schema with entity data
            
        Returns:
            Created entity instance
            
        Raises:
            IntegrityError: If entity violates database constraints
        """
        try:
            # Convert Pydantic model to dict if needed
            if hasattr(obj_in, 'model_dump'):
                obj_data = obj_in.model_dump(exclude_unset=True)
            elif hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict(exclude_unset=True)
            else:
                obj_data = obj_in
            
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            raise e
    
    def update(
        self, 
        entity_id: uuid.UUID, 
        obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        """
        Update existing entity.
        
        Args:
            entity_id: Entity UUID
            obj_in: Update schema with new data
            
        Returns:
            Updated entity instance or None if not found
        """
        db_obj = self.get_by_id(entity_id)
        if not db_obj:
            return None
        
        # Convert Pydantic model to dict if needed
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(exclude_unset=True)
        elif hasattr(obj_in, 'dict'):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            raise e
    
    def delete(self, entity_id: uuid.UUID) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get_by_id(entity_id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filtering.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Number of matching entities
        """
        query = self.db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.count()
    
    def exists(self, entity_id: uuid.UUID) -> bool:
        """
        Check if entity exists by ID.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if exists, False otherwise
        """
        return self.db.query(self.model).filter(
            getattr(self.model, self._get_id_field()) == entity_id
        ).first() is not None
    
    @abstractmethod
    def _get_id_field(self) -> str:
        """
        Get the name of the ID field for this model.
        
        Returns:
            Name of the ID field
        """
        pass