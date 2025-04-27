from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Producto(BaseModel):
    nombre: str = Field(..., description="Nombre del producto")
    precio: float = Field(..., ge=0, description="Precio del producto")
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    categoria: Optional[str] = Field(None, description="Categoría del producto")
    imagen: Optional[str] = Field(None, description="URL de la imagen del producto")
    fuente: Optional[str] = Field(None, description="Fuente de donde se extrajo el producto")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Fecha y hora de creación del producto")