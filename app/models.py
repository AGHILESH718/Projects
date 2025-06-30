from sqlalchemy import Column,Integer,String,Boolean,ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "user_data"

    id = Column(Integer, primary_key=True,index=True)
    Username = Column(String,index=True,unique=True)
    Password = Column(String)
    
    tasks = relationship("Task",back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True ,index=True)
    title = Column(String,index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer,ForeignKey("user_data.id"))
    owner = relationship("User",back_populates="tasks")