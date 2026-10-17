from pydantic import BaseModel, Field
from typing import List, Optional

class ChildProfile(BaseModel):
    """Perfil completo del menor."""
    id: Optional[int] = None
    name: str = Field(..., example="Mateo")
    age_years: int = Field(..., ge=0, le=18)
    allergies: List[str] = Field(default=[])
    avoid_sweeteners: bool = Field(default=True)
    avoid_artificial_colors: bool = Field(default=True)

class ProductData(BaseModel):
    """Entidad de producto alimenticio normalizado."""
    barcode: str
    name: str
    brand: Optional[str] = "Marca genérica"
    category: str = "general"
    ingredients_text: str = ""
    allergens_tags: List[str] = []
    sugars_100g: float = 0.0
    sodium_mg_100g: float = 0.0
    saturated_fat_100g: float = 0.0
    serving_size_g: float = 100.0

class RiskFactor(BaseModel):
    """Detalle individual de un ingrediente o nutriente riesgoso."""
    category: str       # "Alérgeno", "Edulcorante", "Colorante Sintético", "Exceso Nutricional"
    item_detected: str
    severity: str       # "ALTO", "MEDIO"
    explanation: str

class AlternativeProduct(BaseModel):
    """Producto sustituto apto para el perfil activo."""
    barcode: str
    name: str
    brand: str
    serving_size_g: float
    daily_sugar_percentage: float
    daily_sodium_percentage: float
    why_is_better: str

class EvaluationResponse(BaseModel):
    """Respuesta integral del motor de evaluación."""
    barcode: str
    product_name: str
    brand: str
    category: str
    traffic_light: str  # "ROJO", "AMARILLO", "VERDE"
    summary_title: str
    summary_reason: str
    risks: List[RiskFactor]
    daily_sugar_percentage: float
    daily_sodium_percentage: float
    saturated_fat_per_serving: float
    alternatives: List[AlternativeProduct] = []
    shareable_text: str = ""

class HistoryRecord(BaseModel):
    """Registro de auditoría de un producto evaluado por un perfil."""
    id: int
    profile_id: int
    profile_name: str
    barcode: str
    product_name: str
    brand: str
    traffic_light: str
    summary_reason: str
    scanned_at: str