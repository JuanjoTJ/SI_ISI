from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Producto(BaseModel):
    product_id: Optional[str] = Field(None, description="ID único del producto")
    product_title: str = Field(..., description="Título o nombre del producto")
    product_price: float = Field(..., ge=0, description="Precio del producto")
    product_url: str = Field(..., description="URL del producto")
    product_photo: Optional[str] = Field(None, description="URL de la imagen del producto")
    product_provider: Optional[str] = Field(None, description="Fuente de donde se extrajo el producto")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Fecha y hora de creación del producto")