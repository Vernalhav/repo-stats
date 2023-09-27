import datetime
from typing import Generic, Literal, NewType, TypeVar

from pydantic import BaseModel, Field

Cursor = NewType("Cursor", str)
State = Literal["CLOSED", "MERGED", "OPEN"]

T = TypeVar("T")


class PageInfo(BaseModel):
    has_next: bool = Field(alias="hasNextPage")
    end_cursor: Cursor | None = Field(alias="endCursor")


class PRNode(BaseModel):
    title: str
    state: State
    changed_files: int = Field(alias="changedFiles")
    created_at: datetime.datetime = Field(alias="createdAt")
    merged_at: datetime.datetime | None = Field(alias="mergedAt")
    base_ref: str = Field(alias="baseRefName")
    head_ref: str = Field(alias="headRefName")


class Node(BaseModel, Generic[T]):
    node: T


class PullRequests(BaseModel):
    edges: list[Node[PRNode]]
    page_info: PageInfo = Field(alias="pageInfo")


class Repository(BaseModel):
    description: str | None
    name: str = Field(alias="nameWithOwner")
    pull_requests: PullRequests = Field(alias="pullRequests")


class Data(BaseModel):
    repository: Repository


class GraphQLPRMetrics(BaseModel):
    data: Data
