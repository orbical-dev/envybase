from pydantic import BaseModel


class Function(BaseModel):
    """Edge function model."""

    name: str
    code: str
