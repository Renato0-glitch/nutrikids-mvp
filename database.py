import sqlite3
import json
from typing import List, Optional
from models import ChildProfile, ProductData, HistoryRecord

DB_NAME = "nutrikids.db"

INITIAL_PRODUCTS = [
    # 1. JUGOS Y BEBIDAS
    ProductData(barcode="780100000001", name="Néctar de Manzana Infantil (Caja 200ml)", brand="FrutiKids", category="jugos_bebidas",
                ingredients_text="Agua, jugo concentrado de manzana, azúcar, ácido cítrico, sucralosa (SIN 955), acesulfamo k (SIN 950), tartrazina (INS 102).",
                allergens_tags=[], sugars_100g=6.5, sodium_mg_100g=15.0, saturated_fat_100g=0.0, serving_size_g=200.0),
    ProductData(barcode="780100000005", name="Agua Frutada Orgánica Manzana (Sin Azúcar)", brand="BioNiños", category="jugos_bebidas",
                ingredients_text="Agua purificada, infusión de manzana orgánica (15%), ácido ascórbico (vitamina C).",
                allergens_tags=[], sugars_100g=0.4, sodium_mg_100g=2.0, saturated_fat_100g=0.0, serving_size_g=200.0),
    ProductData(barcode="780100000010", name="Jugo 100% Naranja Exprimida Pasteurizado", brand="ValleFresco", category="jugos_bebidas",
                ingredients_text="Jugo natural de naranja exprimida (100%). Sin azúcar añadida ni conservantes.",
                allergens_tags=[], sugars_100g=4.5, sodium_mg_100g=1.0, saturated_fat_100g=0.0, serving_size_g=200.0),
    ProductData(barcode="780100000011", name="Bebida Isotónica Azul Hidratante", brand="SportMax", category="jugos_bebidas",
                ingredients_text="Agua, jarabe de maíz de alta fructosa, citrato de sodio, fosfato monopotasico, sucralosa, azul brillante (E133).",
                allergens_tags=[], sugars_100g=5.8, sodium_mg_100g=55.0, saturated_fat_100g=0.0, serving_size_g=250.0),

    # 2. GALLETAS Y COLACIONES
    ProductData(barcode="780100000002", name="Galletas Rellenas Sabor Chocolate", brand="ChocoMax", category="galletas_snacks",
                ingredients_text="Harina de trigo, azúcar, aceite vegetal de palma, cacao, jarabe de glucosa, lecitina de soya, sal, rojo 40 (INS 129).",
                allergens_tags=["gluten", "soya", "trigo"], sugars_100g=36.0, sodium_mg_100g=320.0, saturated_fat_100g=12.0, serving_size_g=40.0),
    ProductData(barcode="780100000006", name="Galletas de Avena y Plátano con Dátiles", brand="PequesSanos", category="galletas_snacks",
                ingredients_text="Avena integral laminada, pasta de dátiles, puré de plátano, aceite de maravilla alto oleico, canela en polvo.",
                allergens_tags=["gluten", "avena"], sugars_100g=8.5, sodium_mg_100g=20.0, saturated_fat_100g=1.0, serving_size_g=30.0),
    ProductData(barcode="780100000007", name="Galletas de Arroz Inflado y Manzana (Sin Alérgenos)", brand="CeliKids", category="galletas_snacks",
                ingredients_text="Arroz integral orgánico (85%), jugo concentrado de manzana natural (15%).",
                allergens_tags=[], sugars_100g=5.0, sodium_mg_100g=8.0, saturated_fat_100g=0.2, serving_size_g=20.0),

    # 3. LÁCTEOS Y POSTRES
    ProductData(barcode="780100000008", name="Postre Lácteo Frutilla con Chispas", brand="DulceLeche", category="lacteos",
                ingredients_text="Leche entera, azúcar, almidón modificado, gelatina, sucralosa (INS 955), rojo allura (INS 129), amarillo crepúsculo (INS 110).",
                allergens_tags=["leche", "lactosa"], sugars_100g=18.5, sodium_mg_100g=65.0, saturated_fat_100g=3.5, serving_size_g=120.0),
    ProductData(barcode="780100000003", name="Yogur Natural Sin Endulzar", brand="Lácteos del Sur", category="lacteos",
                ingredients_text="Leche entera pasteurizada de vaca, fermentos lácticos (L. bulgaricus, S. thermophilus).",
                allergens_tags=["leche", "lactosa"], sugars_100g=3.2, sodium_mg_100g=45.0, saturated_fat_100g=2.1, serving_size_g=125.0),
    ProductData(barcode="780100000009", name="Postre Vegetal de Coco y Frutilla (Apto APLV)", brand="VeggieKids", category="lacteos",
                ingredients_text="Agua, crema de coco (20%), puré de frutilla natural (12%), almidón de tapioca, cultivos probióticos veganos.",
                allergens_tags=[], sugars_100g=3.0, sodium_mg_100g=15.0, saturated_fat_100g=2.5, serving_size_g=110.0),

    # 4. CEREALES DE DESAYUNO
    ProductData(barcode="780100000012", name="Cereal Aros Multicolor Frutales", brand="CerealBoom", category="cereales",
                ingredients_text="Harina de maíz, azúcar, harina de trigo, sal, jarabe de glucosa, tartrazina (E102), rojo 40 (E129), azul brillante (E133), BHT.",
                allergens_tags=["gluten", "trigo"], sugars_100g=38.0, sodium_mg_100g=390.0, saturated_fat_100g=1.5, serving_size_g=30.0),
    ProductData(barcode="780100000013", name="Quínoa y Amaranto Pop Inflado Natural (Sin Azúcar)", brand="AndesGrano", category="cereales",
                ingredients_text="Quínoa orgánica inflada (70%), amaranto inflado (30%). Libre de gluten.",
                allergens_tags=[], sugars_100g=1.2, sodium_mg_100g=5.0, saturated_fat_100g=0.5, serving_size_g=30.0),

    # 5. COMPOTAS Y FRUTAS
    ProductData(barcode="780100000004", name="Compota de Pera 100% Fruta Orgánica", brand="BabyPura", category="compotas_frutas",
                ingredients_text="Puré de pera orgánica (100%), jugo de limón concentrado.",
                allergens_tags=[], sugars_100g=3.8, sodium_mg_100g=2.0, saturated_fat_100g=0.0, serving_size_g=90.0),
    ProductData(barcode="780100000014", name="Compota Manzana Durazno con Stevia", brand="DulceBebé", category="compotas_frutas",
                ingredients_text="Puré de manzana, puré de durazno, agua, almidón de maíz, glicósidos de esteviol (stevia INS 960), ácido cítrico.",
                allergens_tags=[], sugars_100g=6.0, sodium_mg_100g=10.0, saturated_fat_100g=0.0, serving_size_g=90.0),
]

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Inicializa las 3 tablas relacionales y pobla datos iniciales si están vacías."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tabla de Perfiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age_years INTEGER NOT NULL,
            allergies TEXT NOT NULL,
            avoid_sweeteners INTEGER NOT NULL,
            avoid_artificial_colors INTEGER NOT NULL
        )
    """)

    # 2. Tabla de Catálogo de Productos (persistente y consultable por texto)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            category TEXT NOT NULL,
            ingredients_text TEXT NOT NULL,
            allergens_tags TEXT NOT NULL,
            sugars_100g REAL NOT NULL,
            sodium_mg_100g REAL NOT NULL,
            saturated_fat_100g REAL NOT NULL,
            serving_size_g REAL NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Tabla de Historial de Escaneos / Evaluaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            profile_name TEXT NOT NULL,
            barcode TEXT NOT NULL,
            product_name TEXT NOT NULL,
            brand TEXT NOT NULL,
            traffic_light TEXT NOT NULL,
            summary_reason TEXT NOT NULL,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Semilla de Perfiles
    cursor.execute("SELECT COUNT(*) FROM profiles")
    if cursor.fetchone()[0] == 0:
        default_profiles = [
            ChildProfile(name="Mateo (Preescolar)", age_years=3, allergies=[], avoid_sweeteners=True, avoid_artificial_colors=True),
            ChildProfile(name="Sofía (Escolar - Alergia Leche)", age_years=8, allergies=["Leche"], avoid_sweeteners=False, avoid_artificial_colors=True)
        ]
        for p in default_profiles:
            save_profile(p)

    # Semilla de Productos
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        for prod in INITIAL_PRODUCTS:
            save_product_to_db(prod)

    conn.close()

# --- CRUD DE PERFILES ---
def get_all_profiles() -> List[ChildProfile]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age_years, allergies, avoid_sweeteners, avoid_artificial_colors FROM profiles ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [
        ChildProfile(
            id=r[0], name=r[1], age_years=r[2],
            allergies=json.loads(r[3]), avoid_sweeteners=bool(r[4]), avoid_artificial_colors=bool(r[5])
        ) for r in rows
    ]

def save_profile(profile: ChildProfile) -> ChildProfile:
    conn = get_connection()
    cursor = conn.cursor()
    allergies_json = json.dumps(profile.allergies)
    if profile.id is None:
        cursor.execute("""
            INSERT INTO profiles (name, age_years, allergies, avoid_sweeteners, avoid_artificial_colors)
            VALUES (?, ?, ?, ?, ?)
        """, (profile.name, profile.age_years, allergies_json, int(profile.avoid_sweeteners), int(profile.avoid_artificial_colors)))
        profile.id = cursor.lastrowid
    else:
        cursor.execute("""
            UPDATE profiles SET name=?, age_years=?, allergies=?, avoid_sweeteners=?, avoid_artificial_colors=?
            WHERE id=?
        """, (profile.name, profile.age_years, allergies_json, int(profile.avoid_sweeteners), int(profile.avoid_artificial_colors), profile.id))
    conn.commit()
    conn.close()
    return profile

def delete_profile(profile_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()

# --- CRUD DE PRODUCTOS Y CATÁLOGO ---
def _row_to_product(r) -> ProductData:
    return ProductData(
        barcode=r[0], name=r[1], brand=r[2], category=r[3],
        ingredients_text=r[4], allergens_tags=json.loads(r[5]),
        sugars_100g=float(r[6]), sodium_mg_100g=float(r[7]),
        saturated_fat_100g=float(r[8]), serving_size_g=float(r[9])
    )

def save_product_to_db(product: ProductData):
    """Guarda o actualiza un producto en el catálogo SQLite local."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO products
        (barcode, name, brand, category, ingredients_text, allergens_tags, sugars_100g, sodium_mg_100g, saturated_fat_100g, serving_size_g)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product.barcode, product.name, product.brand or "Marca genérica", product.category,
        product.ingredients_text, json.dumps(product.allergens_tags),
        product.sugars_100g, product.sodium_mg_100g, product.saturated_fat_100g, product.serving_size_g
    ))
    conn.commit()
    conn.close()

def get_product_from_db(barcode: str) -> Optional[ProductData]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT barcode, name, brand, category, ingredients_text, allergens_tags,
               sugars_100g, sodium_mg_100g, saturated_fat_100g, serving_size_g
        FROM products WHERE barcode = ?
    """, (barcode,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_product(row) if row else None

def get_all_products_from_db() -> List[ProductData]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT barcode, name, brand, category, ingredients_text, allergens_tags,
               sugars_100g, sodium_mg_100g, saturated_fat_100g, serving_size_g
        FROM products ORDER BY category, name ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_product(r) for r in rows]

def search_products_in_db(query: str) -> List[ProductData]:
    """Busca productos por coincidencia en nombre, marca o código de barras."""
    conn = get_connection()
    cursor = conn.cursor()
    q = f"%{query.strip()}%"
    cursor.execute("""
        SELECT barcode, name, brand, category, ingredients_text, allergens_tags,
               sugars_100g, sodium_mg_100g, saturated_fat_100g, serving_size_g
        FROM products
        WHERE name LIKE ? OR brand LIKE ? OR barcode LIKE ?
        ORDER BY name ASC
    """, (q, q, q))
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_product(r) for r in rows]

def get_products_by_category_from_db(category: str, exclude_barcode: str) -> List[ProductData]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT barcode, name, brand, category, ingredients_text, allergens_tags,
               sugars_100g, sodium_mg_100g, saturated_fat_100g, serving_size_g
        FROM products WHERE category = ? AND barcode != ?
    """, (category, exclude_barcode))
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_product(r) for r in rows]

# --- CRUD DE HISTORIAL DE EVALUACIONES ---
def add_scan_history(profile: ChildProfile, product: ProductData, traffic_light: str, summary_reason: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scan_history (profile_id, profile_name, barcode, product_name, brand, traffic_light, summary_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (profile.id or 0, profile.name, product.barcode, product.name, product.brand or "", traffic_light, summary_reason))
    conn.commit()
    conn.close()

def get_scan_history(profile_id: Optional[int] = None, limit: int = 30) -> List[HistoryRecord]:
    conn = get_connection()
    cursor = conn.cursor()
    if profile_id is not None:
        cursor.execute("""
            SELECT id, profile_id, profile_name, barcode, product_name, brand, traffic_light, summary_reason, scanned_at
            FROM scan_history WHERE profile_id = ? ORDER BY id DESC LIMIT ?
        """, (profile_id, limit))
    else:
        cursor.execute("""
            SELECT id, profile_id, profile_name, barcode, product_name, brand, traffic_light, summary_reason, scanned_at
            FROM scan_history ORDER BY id DESC LIMIT ?
        """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [
        HistoryRecord(
            id=r[0], profile_id=r[1], profile_name=r[2], barcode=r[3],
            product_name=r[4], brand=r[5], traffic_light=r[6], summary_reason=r[7], scanned_at=r[8]
        ) for r in rows
    ]

def clear_scan_history(profile_id: Optional[int] = None):
    conn = get_connection()
    cursor = conn.cursor()
    if profile_id is not None:
        cursor.execute("DELETE FROM scan_history WHERE profile_id = ?", (profile_id,))
    else:
        cursor.execute("DELETE FROM scan_history")
    conn.commit()
    conn.close()