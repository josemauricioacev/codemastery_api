from pydantic import BaseModel, Field
from datetime import datetime


class UserProgress(BaseModel):
    user_id: int = Field(..., gt=0, description="ID del usuario, debe ser mayor que 0")
    module_id: str = Field(..., min_length=3, max_length=100, description="Identificador del módulo")
    completed: int = Field(..., ge=0, le=1, description="0 = incompleto, 1 = completado")
    completion_date: datetime = Field(..., description="Fecha en que se completó el módulo")

