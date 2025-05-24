from pydantic import BaseModel


class Function(BaseModel):
    """Function model."""

    name: str
    code: str
