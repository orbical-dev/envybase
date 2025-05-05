from pydantic import BaseModel


class EdgeFunction(BaseModel):
    """Edge function model."""

    name: str
    code: str
