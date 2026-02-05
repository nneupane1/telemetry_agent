from pydantic import BaseModel, Field\n\nclass ActionPack(BaseModel):\n    recommendation: str = Field(..., description=\
