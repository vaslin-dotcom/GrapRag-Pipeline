from pydantic import BaseModel, Field
from typing import List, Optional

class NodeProperty(BaseModel):
    key: str = Field( description="Property key e.g. 'founded_year'")
    value: str = Field(description="Property value e.g. '1998'")

class Node(BaseModel):
    name: str = Field(description="Canonical name of the node e.g. 'Saad Khan'")
    type: str = Field(description="Label/category e.g. 'PERSON', 'COMPANY'")
    properties: Optional[List[NodeProperty]] = Field(default_factory=list)

class Relationship(BaseModel):
    source: str = Field(description="name of the source node")
    target: str = Field(description="name of the target node")
    type: str = Field(description="Relationship type e.g. 'WORKS_AT'")
    properties: Optional[List[NodeProperty]] = Field(default_factory=list)

class KnowledgeGraph(BaseModel):
    nodes: List[Node] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)