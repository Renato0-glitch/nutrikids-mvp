from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from models import ChildProfile, ProductData, EvaluationResponse, HistoryRecord
from off_service import fetch_product_by_barcode
from rules_engine import evaluate_product
from database import (
    init_db, get_all_profiles, save_profile, delete_profile,
    get_all_products_from_db, search_products_in_db, save_product_to_db,
    add_scan_history, get_scan_history
)

init_db()

app = FastAPI(
    title="NutriKids API v2.0",
    description="Backend completo para evaluación nutricional pediátrica, catálogo local e historial.",
    version="2.0.0"
)

class ScanRequest(BaseModel):
    barcode: str
    profile: ChildProfile

class ManualEvaluationRequest(BaseModel):
    product: ProductData
    profile: ChildProfile
    save_to_catalog: bool = False

@app.get("/profiles", response_model=List[ChildProfile])
def api_get_profiles():
    return get_all_profiles()

@app.post("/profiles", response_model=ChildProfile)
def api_save_profile(profile: ChildProfile):
    return save_profile(profile)

@app.delete("/profiles/{profile_id}")
def api_delete_profile(profile_id: int):
    delete_profile(profile_id)
    return {"status": "deleted", "profile_id": profile_id}

@app.get("/products", response_model=List[ProductData])
def api_list_products(q: Optional[str] = None):
    if q:
        return search_products_in_db(q)
    return get_all_products_from_db()

@app.post("/products", response_model=ProductData)
def api_add_product(product: ProductData):
    save_product_to_db(product)
    return product

@app.get("/history", response_model=List[HistoryRecord])
def api_get_history(profile_id: Optional[int] = None):
    return get_scan_history(profile_id)

@app.post("/evaluate/barcode", response_model=EvaluationResponse)
def evaluate_by_barcode(request: ScanRequest):
    product = fetch_product_by_barcode(request.barcode.strip())
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    result = evaluate_product(product, request.profile)
    add_scan_history(request.profile, product, result.traffic_light, result.summary_reason)
    return result

@app.post("/evaluate/manual", response_model=EvaluationResponse)
def evaluate_manually(request: ManualEvaluationRequest):
    if request.save_to_catalog:
        save_product_to_db(request.product)
    result = evaluate_product(request.product, request.profile)
    add_scan_history(request.profile, request.product, result.traffic_light, result.summary_reason)
    return result