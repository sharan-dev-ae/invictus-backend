import uuid
from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Category(Base):
    __tablename__="categories"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name:Mapped[str]=mapped_column(String(80),unique=True,index=True)

class Plan(Base):
    __tablename__="plans"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    owner_id:Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),nullable=True,index=True)
    title:Mapped[str]=mapped_column(String(200));description:Mapped[str]=mapped_column(Text,default="")
    status:Mapped[str]=mapped_column(String(30),index=True,default="Pending");priority:Mapped[str]=mapped_column(String(20),default="Medium")
    category_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey("categories.id",ondelete="SET NULL"),nullable=True,index=True)
    due_date:Mapped[date|None]=mapped_column(Date,nullable=True);progress:Mapped[int]=mapped_column(Integer,default=0)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    category:Mapped[Category|None]=relationship();tasks:Mapped[list["Task"]]=relationship(back_populates="plan",cascade="all, delete-orphan")

class Task(Base):
    __tablename__="tasks"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4);owner_id:Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),nullable=True,index=True);plan_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey("plans.id",ondelete="SET NULL"),nullable=True,index=True);project_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey("projects.id",ondelete="SET NULL"),nullable=True,index=True);milestone_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey("milestones.id",ondelete="SET NULL"),nullable=True,index=True)
    title:Mapped[str]=mapped_column(String(250));completed:Mapped[bool]=mapped_column(Boolean,default=False);position:Mapped[int]=mapped_column(Integer,default=0)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());plan:Mapped[Plan|None]=relationship(back_populates="tasks")

class Project(Base):
    __tablename__="projects"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4);owner_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
    title:Mapped[str]=mapped_column(String(200));description:Mapped[str]=mapped_column(Text,default="");status:Mapped[str]=mapped_column(String(30),default="Active");created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())

class Milestone(Base):
    __tablename__="milestones"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4);owner_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True);project_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey("projects.id",ondelete="CASCADE"),nullable=True,index=True)
    title:Mapped[str]=mapped_column(String(200));due_date:Mapped[date|None]=mapped_column(Date,nullable=True);completed:Mapped[bool]=mapped_column(Boolean,default=False);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())

class BucketListItem(Base):
    __tablename__="bucket_list_items"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4);title:Mapped[str]=mapped_column(String(200));category_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey("categories.id",ondelete="SET NULL"),nullable=True)
    owner_id:Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),nullable=True,index=True)
    notes:Mapped[str]=mapped_column(Text,default="");target_date:Mapped[date|None]=mapped_column(Date,nullable=True);achieved:Mapped[bool]=mapped_column(Boolean,default=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());category:Mapped[Category|None]=relationship()

class Activity(Base):
    __tablename__="activity_records"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4);plan_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey("plans.id",ondelete="CASCADE"),nullable=True,index=True)
    action:Mapped[str]=mapped_column(String(80));details:Mapped[str]=mapped_column(Text,default="");created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),index=True)
