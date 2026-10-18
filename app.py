import streamlit as st
import time
from models import ChildProfile, ProductData
from off_service import fetch_product_by_barcode, CATEGORY_LABELS
from rules_engine import evaluate_product
from database import (
    init_db, get_all_profiles, save_profile, delete_profile,
    get_all_products_from_db, search_products_in_db, save_product_to_db,
    add_scan_history, get_scan_history, clear_scan_history
)

# 1. CONFIGURACIÓN DE PÁGINA: Modo Móvil (Menú lateral colapsado por defecto)
st.set_page_config(
    page_title="NutriKids",
    page_icon="🍏",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILO VISUAL DE APP NATIVA (Oculta interfaces de desarrollo) ---
st.markdown("""
    <style>
        /* Ocultar barra superior de Streamlit, footer y botón Deploy */
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Ajustar márgenes para pantallas de teléfono celular */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 480px !important; /* Proporción ideal de smartphone */
            margin: auto;
        }
        
        /* Botones redondeados estilo Android/iOS */
        .stButton>button {
            border-radius: 12px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZAR BASE DE DATOS LOCAL
init_db()
saved_profiles = get_all_profiles()

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

# ==============================================================================
# BARRA LATERAL (MENÚ HAMBURGUESA): GESTIÓN DE PERFILES
# ==============================================================================
st.sidebar.header("👶 Perfiles Familiares")

profile_options = {f"{p.name} ({p.age_years} años)": p for p in saved_profiles}
profile_options["➕ Crear nuevo perfil..."] = None

selected_label = st.sidebar.selectbox("Hijo/a activo:", options=list(profile_options.keys()))
current_stored_profile = profile_options[selected_label]

st.sidebar.divider()

if current_stored_profile:
    st.sidebar.subheader("⚙️ Configurar Perfil")
    p_id = current_stored_profile.id
    default_name = current_stored_profile.name
    default_age = current_stored_profile.age_years
    default_allergies = current_stored_profile.allergies
    default_sweet = current_stored_profile.avoid_sweeteners
    default_colors = current_stored_profile.avoid_artificial_colors
else:
    st.sidebar.subheader("🆕 Crear Nuevo Perfil")
    p_id = None
    default_name = ""
    default_age = 3
    default_allergies = []
    default_sweet = True
    default_colors = True

child_name = st.sidebar.text_input("Nombre del menor", value=default_name, placeholder="Ej: Lucas")
child_age = st.sidebar.slider("Edad (años)", min_value=1, max_value=16, value=default_age)
allergies = st.sidebar.multiselect(
    "Alergias o Intolerancias",
    options=["Leche", "Gluten", "Soya", "Mani"],
    default=default_allergies
)
avoid_sweeteners = st.sidebar.checkbox("Evitar edulcorantes artificiales", value=default_sweet)
avoid_colors = st.sidebar.checkbox("Evitar colorantes sintéticos", value=default_colors)

active_profile = ChildProfile(
    id=p_id,
    name=child_name if child_name.strip() else "Menor",
    age_years=child_age,
    allergies=allergies,
    avoid_sweeteners=avoid_sweeteners,
    avoid_artificial_colors=avoid_colors
)

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("💾 Guardar", use_container_width=True, type="primary"):
        if not child_name.strip():
            st.sidebar.error("Ingresa un nombre.")
        else:
            save_profile(active_profile)
            st.sidebar.success("¡Perfil guardado!")
            st.rerun()

with col_btn2:
    if current_stored_profile and len(saved_profiles) > 1:
        if st.button("🗑️ Eliminar", use_container_width=True):
            delete_profile(current_stored_profile.id)
            st.rerun()

# ==============================================================================
# CABECERA PRINCIPAL (HOME)
# ==============================================================================
st.title("🍏 NutriKids")
st.info(
    f"👦 **Activo:** {active_profile.name} ({active_profile.age_years} años)\n\n"
    f"🛡️ **Alergias:** {', '.join(active_profile.allergies) if active_profile.allergies else 'Ninguna'}"
)

# NAVEGACIÓN MULTI-MÓDULO (Pestañas adaptables)
tab_search, tab_manual, tab_catalog, tab_history, tab_install = st.tabs([
    "🔍 Buscar",
    "📝 Evaluar",
    "🗂️ Catálogo",
    "📜 Historial",
    "📲 Instalar App"
])

# ==============================================================================
# MÓDULO 1: BUSCADOR
# ==============================================================================
with tab_search:
    st.subheader("Buscar Alimento")
    
    col_s1, col_s2 = st.columns([3, 1])
    search_query = col_s1.text_input(
        "Nombre, marca o código EAN:",
        placeholder="Ej: Galletas, Yogur o 78010..."
    )
    do_search = col_s2.button("🔍", type="primary", use_container_width=True)

    if search_query:
        clean_q = search_query.strip()
        if clean_q.isdigit() and len(clean_q) >= 8 and do_search:
            with st.spinner("Consultando base de datos..."):
                prod = fetch_product_by_barcode(clean_q)
                if prod:
                    st.session_state.selected_product = prod
                    eval_res = evaluate_product(prod, active_profile)
                    add_scan_history(active_profile, prod, eval_res.traffic_light, eval_res.summary_reason)
                else:
                    st.error("No encontramos ese código EAN. Puedes registrarlo en la pestaña '📝 Evaluar'.")
        else:
            matches = search_products_in_db(clean_q)
            if matches:
                for m in matches:
                    cat_lbl = CATEGORY_LABELS.get(m.category, m.category)
                    c_info, c_act = st.columns([4, 2])
                    c_info.markdown(f"**{m.name}**\n\n<small>{m.brand}</small>", unsafe_allow_html=True)
                    if c_act.button("Analizar", key=f"search_{m.barcode}", use_container_width=True):
                        st.session_state.selected_product = m
                        eval_res = evaluate_product(m, active_profile)
                        add_scan_history(active_profile, m, eval_res.traffic_light, eval_res.summary_reason)
            else:
                st.warning("Sin coincidencias en el catálogo local. Presiona 🔍 para buscar EAN en línea.")

    st.divider()
    all_local_prods = get_all_products_from_db()
    quick_options = {"-- Seleccionar del catálogo rápido --": None}
    for p in all_local_prods:
        quick_options[f"{p.name} ({p.brand})"] = p

    selected_quick = st.selectbox("O selecciona directamente:", options=list(quick_options.keys()))
    if st.button("Evaluar", use_container_width=True):
        if quick_options[selected_quick]:
            prod = quick_options[selected_quick]
            st.session_state.selected_product = prod
            eval_res = evaluate_product(prod, active_profile)
            add_scan_history(active_profile, prod, eval_res.traffic_light, eval_res.summary_reason)

# ==============================================================================
# MÓDULO 2: EVALUADOR MANUAL Y AGREGADOR DE PRODUCTOS
# ==============================================================================
with tab_manual:
    st.subheader("Agregar Nuevo Alimento")
    st.caption("Copia los datos de la etiqueta. Quedará guardado en tu catálogo local.")
    
    m_name = st.text_input("Nombre del producto", value="Cereal Infantil Aros Frutales")
    m_brand = st.text_input("Marca", value="FantasíaKids")
    m_category = st.selectbox("Categoría", options=list(CATEGORY_LABELS.keys()), format_func=lambda k: CATEGORY_LABELS[k], index=3)
    
    m_ing = st.text_area("Lista de Ingredientes", value="Harina de maíz, azúcar, jarabe de maíz, sal, SIN 955, E102, BHT.")
    
    col_n1, col_n2 = st.columns(2)
    m_serving = col_n1.number_input("Porción (g/ml)", value=30.0, min_value=1.0)
    m_sugar = col_n2.number_input("Azúcares (en 100g)", value=32.0, min_value=0.0)
    
    col_n3, col_n4 = st.columns(2)
    m_sodium = col_n3.number_input("Sodio mg (en 100g)", value=280.0, min_value=0.0)
    m_satfat = col_n4.number_input("Grasa Sat. (en 100g)", value=2.5, min_value=0.0)

    save_in_db = st.checkbox("💾 Guardar en catálogo", value=True)
    
    if st.button("🚀 Evaluar Etiqueta", type="primary", use_container_width=True):
        code_to_use = f"LOC{int(time.time())}"
        new_prod = ProductData(
            barcode=code_to_use, name=m_name, brand=m_brand, category=m_category,
            ingredients_text=m_ing, sugars_100g=m_sugar, sodium_mg_100g=m_sodium,
            saturated_fat_100g=m_satfat, serving_size_g=m_serving
        )
        if save_in_db:
            save_product_to_db(new_prod)
            st.toast("Producto guardado en tu catálogo.", icon="✅")
            
        st.session_state.selected_product = new_prod
        eval_res = evaluate_product(new_prod, active_profile)
        add_scan_history(active_profile, new_prod, eval_res.traffic_light, eval_res.summary_reason)

# ==============================================================================
# MÓDULO 3: EXPLORADOR DEL CATÁLOGO
# ==============================================================================
with tab_catalog:
    st.subheader(f"Catálogo en Vivo para {active_profile.name}")
    filter_cat = st.selectbox("Filtro:", options=["TODAS"] + list(CATEGORY_LABELS.keys()), format_func=lambda x: "📦 Todas" if x == "TODAS" else CATEGORY_LABELS[x])
    
    catalog_products = get_all_products_from_db()
    if filter_cat != "TODAS":
        catalog_products = [p for p in catalog_products if p.category == filter_cat]

    for p in catalog_products:
        ev = evaluate_product(p, active_profile, include_alternatives=False)
        badge = {"ROJO": "🔴 No Apto", "AMARILLO": "🟡 Ocasional", "VERDE": "🟢 Apto"}[ev.traffic_light]
        c_cat1, c_cat2 = st.columns([3, 1])
        c_cat1.markdown(f"**{badge}** | {p.name}\n<small>{p.brand}</small>", unsafe_allow_html=True)
        if c_cat2.button("Ver", key=f"cat_{p.barcode}", use_container_width=True):
            st.session_state.selected_product = p
            st.rerun()
        st.divider()

# ==============================================================================
# MÓDULO 4: HISTORIAL
# ==============================================================================
with tab_history:
    st.subheader("📜 Tu Historial")
    history_items = get_scan_history(active_profile.id)
    
    if not history_items:
        st.info("Sin evaluaciones recientes.")
    else:
        if st.button("🗑️ Limpiar historial"):
            clear_scan_history(active_profile.id)
            st.rerun()
            
        for h in history_items:
            icon = {"ROJO": "🔴", "AMARILLO": "🟡", "VERDE": "🟢"}.get(h.traffic_light, "⚪")
            st.markdown(f"**{icon} {h.product_name}** (*{h.brand}*)\n\n<small>{h.summary_reason}</small>", unsafe_allow_html=True)
            st.divider()

# ==============================================================================
# MÓDULO 5: DESCARGAR APP / PRESENTACIÓN (CÓDIGO QR)
# ==============================================================================
with tab_install:
    st.subheader("📲 Descargar APK para Android")
    st.markdown("Escanea este código QR para descargar el instalador directo de la aplicación. **No requiere inicio de sesión.**")
    
    # 1. Enlace directo y puro desde tu propio repositorio de GitHub
    apk_direct_download_url = "https://raw.githubusercontent.com/Renato0-glitch/nutrikids-mvp/main/NutriKids.apk"
    
    # 2. Codificación segura de la URL para el QR
    import urllib.parse
    encoded_url = urllib.parse.quote_plus(apk_direct_download_url)
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_url}"
    
    # 3. Mostrar el código QR centrado
    st.markdown(
        f"""
        <div style="text-align: center; margin: 20px 0;">
            <img src="{qr_image_url}" width="230" style="border-radius: 12px; background: white; padding: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" alt="Código QR Descarga">
            <p style="margin-top: 10px; font-size: 14px;">Escanea para descargar automáticamente</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Botón en HTML que fuerza la descarga sin pasar por bloqueos
    st.markdown(
        f"""
        <div style='text-align: center;'>
            <a href='{apk_direct_download_url}' target='_blank' style='background-color: #2ECC71; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;'>
                📥 Descargar Instalador (.apk)
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.write("")
    st.info("ℹ️ Al abrir el archivo descargado, Android preguntará si deseas instalar aplicaciones de orígenes desconocidos. Presiona **Permitir** o **Configuración > Confiar en esta fuente**.")

# ==============================================================================
# PANEL INFERIOR: RESULTADO DETALLADO DEL PRODUCTO ACTIVO
# ==============================================================================
if st.session_state.selected_product:
    product_to_evaluate = st.session_state.selected_product
    result = evaluate_product(product_to_evaluate, active_profile)
    
    st.divider()
    st.header("📋 Informe Nutricional")
    st.caption(f"CÓDIGO: `{result.barcode}`")

    if result.traffic_light == "ROJO":
        st.error(f"### 🔴 {result.summary_title}\n**{result.product_name}**\n\n**Veredicto:** {result.summary_reason}")
    elif result.traffic_light == "AMARILLO":
        st.warning(f"### 🟡 {result.summary_title}\n**{result.product_name}**\n\n**Veredicto:** {result.summary_reason}")
    else:
        st.success(f"### 🟢 {result.summary_title}\n**{result.product_name}**\n\n**Veredicto:** {result.summary_reason}")

    st.subheader("📊 Impacto en 1 porción")
    c1, c2, c3 = st.columns(3)
    c1.metric("Azúcar Diaria", f"{result.daily_sugar_percentage}%")
    c2.metric("Sodio Diario", f"{result.daily_sodium_percentage}%")
    c3.metric("Grasas Sat.", f"{result.saturated_fat_per_serving}g")

    st.subheader("🔍 Alertas Detectadas")
    if not result.risks:
        st.success("¡Excelente elección! Ningún ingrediente crítico detectado.")
    else:
        for risk in result.risks:
            badge = "🚨 RIESGO ALTO" if risk.severity == "ALTO" else "⚠️ PRECAUCIÓN"
            with st.expander(f"{badge} | {risk.category}: **{risk.item_detected}**", expanded=True):
                st.write(risk.explanation)
                
    if result.traffic_light in ["ROJO", "AMARILLO"]:
        st.subheader("💡 Alternativas Saludables")
        if not result.alternatives:
            st.info("No hay alternativas aptas en el catálogo local.")
        else:
            for alt in result.alternatives:
                st.success(
                    f"**🟢 {alt.name}**\n\n**¿Por qué es mejor?** {alt.why_is_better}\n\n"
                    f"🍬 Azúcar: **{alt.daily_sugar_percentage}%** | 🧂 Sodio: **{alt.daily_sodium_percentage}%**"
                )

    with st.expander("📤 Compartir Reporte por WhatsApp"):
        st.code(result.shareable_text, language="markdown")