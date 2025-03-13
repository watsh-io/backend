from enum import Enum
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
from fastapi import APIRouter, status, Depends, Body, Query


from .pyobjectid import PyObjectId

class BaseModelEncoder(BaseModel):
    class Config:
        json_encoders = {ObjectId: str}
        use_enum_values = True

class User(BaseModelEncoder):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str

class Project(BaseModelEncoder):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    slug: str
    description: str
    owner: PyObjectId
    archived: bool

class Member(BaseModelEncoder):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user: PyObjectId
    project: PyObjectId

class Environment(BaseModelEncoder):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    project: PyObjectId
    slug: str
    default: bool

class Branch(BaseModelEncoder):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    project: PyObjectId
    environment: PyObjectId
    slug: str
    default: bool

class Commit(BaseModelEncoder):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    project: PyObjectId
    environment: PyObjectId
    branch: PyObjectId
    author: PyObjectId
    message: str
    timestamp: int

class ItemType(Enum):
    OBJECT = 'object'
    ARRAY = 'array'
    STRING = 'string'
    NUMBER = 'number'
    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    NULL = 'null'

class Item(BaseModelEncoder):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    project: PyObjectId
    environment: PyObjectId
    branch: PyObjectId
    item: PyObjectId
    parent: PyObjectId
    type: ItemType
    active: bool

    slug: Optional[str]

    # item_enum: Optional[list[int]]
    # item_required: Optional[bool]
    # item_examples: Optional[list[str | bool | int | float | None]]
    # item_description: Optional[str]
    # item_constant: Optional[str]
    # item_default: Optional[str]
    # item_depreciated: Optional[bool]

    # string_min_length: Optional[int] # > 0
    # string_max_length: Optional[int] # > 0
    # string_pattern: Optional[str]
    # string_format: Optional[str]

    secret_value: Optional[str | bool | int | float | None] = None
    secret_active: bool

    commit: PyObjectId
    timestamp: int


class ItemUpdate(BaseModelEncoder):
    item: PyObjectId
    parent: PyObjectId
    type: ItemType 
    active: bool 
    slug: str
    secret_value: str
    secret_active: bool


class Token(BaseModelEncoder):
    access_token: str
    token_type: str

class HealthCheck(BaseModelEncoder):
    status: str = "OK"
    version: str
    timestamp: int

class ObjectIDResponse(BaseModelEncoder):
    id: PyObjectId


class EnvironmentSnapshot(BaseModelEncoder):
    environment: Environment
    branches: list[Branch]

class ProjectSnapshot(BaseModelEncoder):
    project: Project
    members: list[Member]
    environments: list[EnvironmentSnapshot]

class UserSnapshot(BaseModelEncoder):
    user: User
    projects: list[ProjectSnapshot]


