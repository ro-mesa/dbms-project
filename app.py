import base64
import os
import streamlit as st
import pandas as pd
from db_connection import get_db_connection

# -----------------------------------------------------------------------------
# Custom SVG Favicon (Bold Serif "F" + Saffron Leaf Accent on Deep Basil Tile)
# -----------------------------------------------------------------------------
FAVICON_SVG = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
    "<rect width='64' height='64' rx='16' fill='%233D5A45'/>"
    "<text x='18' y='47' font-family='Georgia, serif' font-size='40' font-weight='bold' fill='%23FFFFFF'>F</text>"
    "<path d='M43 22c5-5 11-4 11-4s1 6-4 11c-3 3-7 3-9 1s-1-6 2-8z' fill='%23D98A2B'/>"
    "</svg>"
)

st.set_page_config(
    page_title="FlavorCraft | Culinary Collection",
    page_icon=FAVICON_SVG,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Olive & Warm Linen Editorial CSS + Vector Styling
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* Hide Streamlit Deploy button, top-right menu & footer; keep Hamburger toggle */
        [data-testid="stAppDeployButton"],
        .stDeployButton,
        #MainMenu,
        footer,
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        /* Make Streamlit Top Header Bar Completely Transparent (No Frosted Strip) */
        header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        border-bottom: none !important;
        }

        /* Soft Linen Canvas & Charcoal Forest Typography */
        .stApp {
            background-color: #F9F8F3;
            color: #1F2421;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .block-container {
            padding-top: 2.2rem;
            padding-bottom: 3rem;
            max-width: 1260px;
        }

        /* Classic High-Contrast Serif Headings */
        h1, h2, h3, .editorial-title {
            font-family: 'Playfair Display', Georgia, serif !important;
            color: #1F2421 !important;
            letter-spacing: -0.01em;
        }

        /* Botanical Cloche Brand Header */
        .brand-banner {
            display: flex;
            align-items: center;
            gap: 18px;
            padding: 0.25rem 0 1.4rem 0;
            border-bottom: 1px solid #E5E2D9;
            margin-bottom: 1.5rem;
        }
        .brand-emblem {
            width: 56px;
            height: 56px;
            border-radius: 16px;
            background: linear-gradient(145deg, #3D5A45 0%, #2C4332 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 18px rgba(61, 90, 69, 0.20);
            flex-shrink: 0;
        }
        .brand-heading {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 2.2rem;
            font-weight: 700;
            color: #1F2421;
            line-height: 1.08;
            margin: 0;
        }
        .brand-sub {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.95rem;
            color: #5C665E;
            margin: 4px 0 0 0;
        }

        /* Sidebar Drawer Styling */
        section[data-testid="stSidebar"] {
            background-color: #F1EFE7;
            border-right: 1px solid #E2DFD5;
        }
        .sidebar-brand-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 4px;
        }
        .sidebar-brand-text {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.35rem;
            font-weight: 700;
            color: #1F2421;
        }
        .kpi-pill-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E2D9;
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 10px;
            box-shadow: 0 2px 6px rgba(31, 36, 33, 0.03);
        }
        .kpi-pill-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #5C665E;
        }
        .kpi-pill-val {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.35rem;
            font-weight: 700;
            color: #3D5A45;
            margin-top: 2px;
        }
        .kpi-pill-val-saffron {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.35rem;
            font-weight: 700;
            color: #D98A2B;
            margin-top: 2px;
        }

        /* Pure White Recipe Cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E2D9 !important;
            border-radius: 16px !important;
            box-shadow: 0 6px 20px rgba(31, 36, 33, 0.04) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 26px rgba(31, 36, 33, 0.08) !important;
        }

        /* Uniform 4:3 Hero Food Photography */
        [data-testid="stImage"] img {
            aspect-ratio: 4 / 3;
            width: 100%;
            object-fit: cover;
            border-radius: 10px;
        }

        /* Botanical Sage Category Pills */
        .category-pill-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin: 6px 0 6px 0;
        }
        .category-pill {
            background-color: #EBF1EC;
            color: #3D5A45;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 999px;
            letter-spacing: 0.02em;
        }

        /* Card Title, Byline & Vector Icon Metadata */
        .recipe-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.24rem;
            font-weight: 700;
            color: #1F2421;
            line-height: 1.25;
            margin-top: 2px;
        }
        .recipe-author {
            font-size: 0.82rem;
            color: #5C665E;
            margin-bottom: 8px;
        }
        .recipe-meta-line {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #F9F8F3;
            border: 1px solid #ECE9DF;
            border-radius: 8px;
            padding: 7px 10px;
            margin: 6px 0 12px 0;
            font-size: 0.81rem;
            font-weight: 500;
            color: #38403A;
        }
        .meta-item {
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        /* Buttons (Deep Basil Primary + Clean Secondary Icon Button) */
        .stButton > button {
            border-radius: 10px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
        }
        .stButton > button[kind="primary"] {
            background-color: #3D5A45 !important;
            border: none !important;
            color: #FFFFFF !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #2E4535 !important;
        }
        .stButton > button[kind="secondary"] {
            background-color: #F9F8F3 !important;
            border: 1px solid #DFDCD2 !important;
            color: #3D5A45 !important;
            min-width: 38px !important;
            padding: 0.25rem 0.4rem !important;
        }
        .stButton > button[kind="secondary"]:hover {
            border-color: #3D5A45 !important;
            background-color: #EBF1EC !important;
        }
        /* Flush Top-Right Corner Garnish Reaching the Very Top Edge */
.corner-garnish {
    position: fixed;
    top: 0px;
    right: 0px;
    width: 640px;
    max-width: 48vw;
    pointer-events: none;
    z-index: 999989; /* Sits right under the transparent header bar, reaching y=0 */
    -webkit-mask-image: radial-gradient(ellipse 85% 85% at 88% 12%, #000 58%, transparent 96%);
    mask-image: radial-gradient(ellipse 85% 85% at 88% 12%, #000 58%, transparent 96%);
}

/* Keep Header Text, Search Bar, Dropdown & Cards Interactive & Above Artwork */
.brand-banner,
div[data-testid="stHorizontalBlock"],
div[data-testid="stSelectbox"],
div[data-testid="stTextInput"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    position: relative;
    z-index: 999990;
}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Inline Vector SVG Icons (Crisp, Monochrome, Cross-Platform)
# -----------------------------------------------------------------------------
ICON_CLOCK = "<svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#3D5A45' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>"
ICON_FLAME = "<svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#D98A2B' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'><path d='M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z'/></svg>"
ICON_CHEF = "<svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#3D5A45' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'><path d='M6 13.87A4 4 0 0 1 7.41 6a5.11 5.11 0 0 1 1.05-1.54 5 5 0 0 1 7.08 0A5.11 5.11 0 0 1 16.59 6 4 4 0 0 1 18 13.87V21H6Z'/><line x1='6' y1='17' x2='18' y2='17'/></svg>"
ICON_STAR = "<svg width='15' height='15' viewBox='0 0 24 24' fill='#D98A2B' stroke='#D98A2B' stroke-width='2'><polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/></svg>"

# -----------------------------------------------------------------------------
# Database Helper Functions
# -----------------------------------------------------------------------------
def run_query(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            return pd.read_sql(query, conn, params=params)
        finally:
            conn.close()
    return pd.DataFrame()

def execute_commit(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    return None

FALLBACK_IMAGES = {
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop",
    "pasta": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=600&auto=format&fit=crop",
    "carbonara": "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=600&auto=format&fit=crop",
    "cake": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop",
    "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop",
    "tea": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop",
    "chai": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop",
    "biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop",
    "tiramisu": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&auto=format&fit=crop",
    "wedge": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=600&auto=format&fit=crop",
    "potato": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=600&auto=format&fit=crop",
    "wrap": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=600&auto=format&fit=crop",
    "salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&auto=format&fit=crop",
    "default": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=600&auto=format&fit=crop"
}

def get_recipe_image(title, custom_url=None):
    if custom_url and pd.notna(custom_url) and str(custom_url).strip():
        return str(custom_url).strip()
    title_lower = title.lower() if title else ""
    for kw, url in FALLBACK_IMAGES.items():
        if kw != "default" and kw in title_lower:
            return url
    return FALLBACK_IMAGES["default"]

# -----------------------------------------------------------------------------
# Recipe Details Dialog (View Only)
# -----------------------------------------------------------------------------
@st.dialog("Recipe Details", width="large")
def show_recipe_modal(recipe_id, title):
    detail_query = """
        SELECT r.instructions, r.image_url, r.prep_time, r.servings, r.difficulty_level,
               n.calories, n.protein, n.carbs, n.fats
        FROM recipes r
        LEFT JOIN nutrition n ON r.recipe_id = n.recipe_id
        WHERE r.recipe_id = %s;
    """
    df = run_query(detail_query, (recipe_id,))
    
    img_url = None
    if not df.empty:
        rec = df.iloc[0]
        img_url = rec.get("image_url")
    
    st.subheader(title)
    st.image(get_recipe_image(title, img_url), use_container_width=True)
    
    if not df.empty:
        rec = df.iloc[0]
        st.markdown(
            f"<div class='recipe-meta-line'>"
            f"<span class='meta-item'>{ICON_CLOCK} <b>{rec['prep_time']}m</b> Prep</span>"
            f"<span>•</span>"
            f"<span><b>{rec['servings']}</b> Servings</span>"
            f"<span>•</span>"
            f"<span class='meta-item'>{ICON_FLAME} <b>{rec['calories'] or 0}</b> kcal</span>"
            f"<span>•</span>"
            f"<span><b>{rec['protein'] or 0}g</b> Protein</span>"
            f"<span>•</span>"
            f"<span class='meta-item'>{ICON_CHEF} <b>{rec['difficulty_level']}</b></span>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("#### Instructions")
        st.write(rec["instructions"])

    st.markdown("#### Ingredients Required")
    ing_query = """
        SELECT i.name, ri.quantity, ri.unit 
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
        WHERE ri.recipe_id = %s;
    """
    ing_df = run_query(ing_query, (recipe_id,))
    if not ing_df.empty:
        for _, row in ing_df.iterrows():
            st.markdown(f"- **{row['quantity']} {row['unit']}** {row['name']}")
    else:
        st.caption("No ingredients specified.")

    st.markdown("#### Reviews & Ratings")
    rev_query = """
        SELECT u.username, r.rating, r.comment, r.review_date
        FROM reviews r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.recipe_id = %s
        ORDER BY r.review_date DESC;
    """
    rev_df = run_query(rev_query, (recipe_id,))
    if not rev_df.empty:
        for _, row in rev_df.iterrows():
            st.markdown(f"{ICON_STAR} **{row['rating']}/5** by *{row['username']}*", unsafe_allow_html=True)
            if row['comment']:
                st.caption(f'"{row["comment"]}"')
    else:
        st.caption("No reviews yet for this recipe.")

# -----------------------------------------------------------------------------
# Recipe Edit Dialog (UPDATE SQL Implementation)
# -----------------------------------------------------------------------------
@st.dialog("Edit Recipe")
def show_edit_modal(recipe_id):
    rec_query = """
        SELECT r.title, r.instructions, r.image_url, r.prep_time, r.servings, r.difficulty_level,
               n.calories, n.protein, n.carbs, n.fats
        FROM recipes r
        LEFT JOIN nutrition n ON r.recipe_id = n.recipe_id
        WHERE r.recipe_id = %s;
    """
    rec_data = run_query(rec_query, (recipe_id,))
    if rec_data.empty:
        st.error("Recipe not found.")
        return
        
    current = rec_data.iloc[0]
    
    with st.form("edit_recipe_form"):
        new_title = st.text_input("Recipe Title", value=current["title"])
        new_img_url = st.text_input("Image URL", value=current["image_url"] if pd.notna(current["image_url"]) else "")
        
        c1, c2, c3 = st.columns(3)
        diff_list = ["Easy", "Medium", "Hard"]
        diff_index = diff_list.index(current["difficulty_level"]) if current["difficulty_level"] in diff_list else 0
        new_diff = c1.selectbox("Difficulty", diff_list, index=diff_index)
        new_prep = c2.number_input("Prep Time (min)", min_value=1, value=int(current["prep_time"]), step=5)
        new_servings = c3.number_input("Servings", min_value=1, value=int(current["servings"]), step=1)
        
        new_instructions = st.text_area("Cooking Instructions", value=current["instructions"], height=140)
        
        st.markdown("##### Nutritional Values")
        n1, n2, n3, n4 = st.columns(4)
        new_cals = n1.number_input("Calories", min_value=0, value=int(current["calories"] or 0))
        new_prot = n2.number_input("Protein (g)", min_value=0.0, value=float(current["protein"] or 0.0))
        new_carbs = n3.number_input("Carbs (g)", min_value=0.0, value=float(current["carbs"] or 0.0))
        new_fats = n4.number_input("Fats (g)", min_value=0.0, value=float(current["fats"] or 0.0))
        
        save_btn = st.form_submit_button("Update Recipe in Database", type="primary", use_container_width=True)
        
        if save_btn:
            upd_recipe = """
                UPDATE recipes 
                SET title = %s, instructions = %s, image_url = %s, prep_time = %s, servings = %s, difficulty_level = %s
                WHERE recipe_id = %s;
            """
            execute_commit(upd_recipe, (new_title, new_instructions, new_img_url.strip() or None, new_prep, new_servings, new_diff, recipe_id))
            
            upd_nutri = """
                UPDATE nutrition 
                SET calories = %s, protein = %s, carbs = %s, fats = %s
                WHERE recipe_id = %s;
            """
            execute_commit(upd_nutri, (new_cals, new_prot, new_carbs, new_fats, recipe_id))
            
            st.success("Recipe updated successfully!")
            st.rerun()

# -----------------------------------------------------------------------------
# Hamburger Menu Sidebar (Custom Monogram Mark, Material Icons & Soft KPIs)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand-row">
            <svg width="26" height="26" viewBox="0 0 64 64">
                <rect width="64" height="64" rx="16" fill="#3D5A45"/>
                <text x="18" y="47" font-family="Georgia, serif" font-size="40" font-weight="bold" fill="#FFFFFF">F</text>
                <path d="M43 22c5-5 11-4 11-4s1 6-4 11c-3 3-7 3-9 1s-1-6 2-8z" fill="#D98A2B"/>
            </svg>
            <span class="sidebar-brand-text">FlavorCraft</span>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Navigation & Kitchen Overview")
    
    nav_pages = [
        ":material/restaurant_menu: Recipe Feed",
        ":material/add_circle: Add Recipe"
    ]
    admin_mode = st.toggle("Developer / Admin Mode", value=False, help="Reveal Database Inspector for SQL evaluation")
    if admin_mode:
        nav_pages.append(":material/database: Database Inspector")
        
    active_page = st.radio("Menu", nav_pages, label_visibility="collapsed")
    
    st.divider()
    st.markdown("##### Community Stats")
    
    total_recipes = run_query("SELECT COUNT(*) AS total FROM recipes;").iloc[0]["total"]
    total_reviews = run_query("SELECT COUNT(*) AS total FROM reviews;").iloc[0]["total"]
    avg_rating = run_query("SELECT ROUND(AVG(rating), 1) AS avg_r FROM reviews;").iloc[0]["avg_r"] or 0.0

    st.markdown(f"""
        <div class="kpi-pill-card">
            <div class="kpi-pill-label">Total Recipes</div>
            <div class="kpi-pill-val">{total_recipes}</div>
        </div>
        <div class="kpi-pill-card">
            <div class="kpi-pill-label">Community Reviews</div>
            <div class="kpi-pill-val">{total_reviews}</div>
        </div>
        <div class="kpi-pill-card">
            <div class="kpi-pill-label">Platform Rating</div>
            <div class="kpi-pill-val-saffron">{ICON_STAR} {avg_rating} / 5.0</div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Botanical Cloche Brand Header (Dome Cloche + Fresh Basil Leaf)
# -----------------------------------------------------------------------------
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

garnish_b64 = get_base64_image("assets/corner_garnish.png")
garnish_html = (
    f'<img src="data:image/png;base64,{garnish_b64}" class="corner-garnish" alt=""/>'
    if garnish_b64 else ""
)

st.markdown(f"""
    {garnish_html}
    <div class="brand-banner">
        <div class="brand-emblem">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="7.5" r="2" fill="#FFFFFF"/>
                <path d="M6 21C6 14.9249 10.4772 10 16 10C21.5228 10 26 14.9249 26 21H6Z" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/>
                <path d="M4 24.5H28" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
                <path d="M22.5 22.5C25.5 19.5 29 20 29 20C29 20 29.5 23.5 26.5 26.5C24.5 28.5 22 28 21 27C20 26 20.5 24.5 22.5 22.5Z" fill="#D98A2B"/>
            </svg>
        </div>
        <div>
            <h1 class="brand-heading">FlavorCraft</h1>
            <p class="brand-sub">Discover, cook, and share community-crafted recipes.</p>
        </div>
    </div>
""", unsafe_allow_html=True)
# -----------------------------------------------------------------------------
# VIEW 1: RECIPE FEED
# -----------------------------------------------------------------------------
if active_page == ":material/restaurant_menu: Recipe Feed":
    c1, c2 = st.columns([3, 1])
    with c1:
        search_kw = st.text_input("Search recipes", placeholder="Search dishes by name (e.g. Pasta, Burger, Cake)...", label_visibility="collapsed")
    with c2:
        cat_df = run_query("SELECT category_id, category_name FROM categories;")
        cat_list = ["All Cuisines"] + list(cat_df["category_name"].unique()) if not cat_df.empty else ["All Cuisines"]
        selected_category = st.selectbox("Filter by Category", cat_list, label_visibility="collapsed")

    feed_query = """
        SELECT r.recipe_id, r.title, r.image_url, r.prep_time, r.difficulty_level,
               u.username AS author, n.calories,
               GROUP_CONCAT(c.category_name SEPARATOR ', ') AS categories
        FROM recipes r
        JOIN users u ON r.user_id = u.user_id
        LEFT JOIN nutrition n ON r.recipe_id = n.recipe_id
        LEFT JOIN recipe_categories rc ON r.recipe_id = rc.recipe_id
        LEFT JOIN categories c ON rc.category_id = c.category_id
        GROUP BY r.recipe_id, r.title, r.image_url, r.prep_time, r.difficulty_level, u.username, n.calories;
    """
    recipes = run_query(feed_query)

    if not recipes.empty:
        if search_kw:
            recipes = recipes[recipes["title"].str.contains(search_kw, case=False, na=False)]
        if selected_category != "All Cuisines":
            recipes = recipes[recipes["categories"].str.contains(selected_category, case=False, na=False)]

        st.caption(f"Displaying {len(recipes)} dish(es) • Open the top-left menu to add a recipe or view stats")

        cols_per_row = 3
        card_cols = st.columns(cols_per_row, gap="large")
        for idx, (_, rec) in enumerate(recipes.iterrows()):
            col = card_cols[idx % cols_per_row]
            with col:
                with st.container(border=True):
                    # 1. Hero 4:3 Food Photo
                    st.image(get_recipe_image(rec['title'], rec.get('image_url')), use_container_width=True)
                    
                    # 2. Botanical Sage Category Pills
                    cat_str = rec['categories'] if pd.notna(rec['categories']) and rec['categories'] else "General"
                    pills_html = "".join([f"<span class='category-pill'>{c.strip()}</span>" for c in cat_str.split(",")])
                    st.markdown(f"<div class='category-pill-wrap'>{pills_html}</div>", unsafe_allow_html=True)

                    # 3. Title + Properly Sized Top-Right Material Edit Icon Button
                    title_col, edit_col = st.columns([4.2, 1])
                    with title_col:
                        st.markdown(f"<div class='recipe-title'>{rec['title']}</div>", unsafe_allow_html=True)
                    with edit_col:
                        if st.button("", icon=":material/edit:", key=f"edit_{rec['recipe_id']}", help="Edit Recipe", type="secondary"):
                            show_edit_modal(rec['recipe_id'])

                    st.markdown(f"<div class='recipe-author'>By Chef <b>{rec['author']}</b></div>", unsafe_allow_html=True)
                    
                    # 4. Single-Line Vector Icon Metadata
                    st.markdown(
                        f"<div class='recipe-meta-line'>"
                        f"<span class='meta-item'>{ICON_CLOCK} {rec['prep_time']}m</span>"
                        f"<span>•</span>"
                        f"<span class='meta-item'>{ICON_FLAME} {rec['calories'] or 0} kcal</span>"
                        f"<span>•</span>"
                        f"<span class='meta-item'>{ICON_CHEF} {rec['difficulty_level']}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    # 5. Primary Deep Basil Action Button
                    if st.button("View Recipe", key=f"view_{rec['recipe_id']}", type="primary", use_container_width=True):
                        show_recipe_modal(rec['recipe_id'], rec['title'])
    else:
        st.info("No recipes found matching your search.")

# -----------------------------------------------------------------------------
# VIEW 2: ADD RECIPE
# -----------------------------------------------------------------------------
elif active_page == ":material/add_circle: Add Recipe":
    st.subheader("Submit a New Recipe to the Database")
    
    users_df = run_query("SELECT user_id, username FROM users;")
    all_categories_df = run_query("SELECT category_id, category_name FROM categories;")
    all_ingredients_df = run_query("SELECT ingredient_id, name FROM ingredients;")
    
    with st.form("add_recipe_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            title = st.text_input("Recipe Title *")
            user_choice = st.selectbox(
                "Author / Chef *", 
                options=users_df["user_id"].tolist() if not users_df.empty else [],
                format_func=lambda x: users_df.loc[users_df["user_id"] == x, "username"].values[0] if not users_df.empty else str(x)
            )
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
        with f_col2:
            prep_time = st.number_input("Preparation Time (minutes) *", min_value=1, value=25, step=5)
            servings = st.number_input("Servings *", min_value=1, value=2, step=1)
            selected_cat_ids = st.multiselect(
                "Existing Categories", 
                options=all_categories_df["category_id"].tolist() if not all_categories_df.empty else [],
                format_func=lambda x: all_categories_df.loc[all_categories_df["category_id"] == x, "category_name"].values[0] if not all_categories_df.empty else str(x)
            )
            new_cats_input = st.text_input("Or add new categories (comma separated)", placeholder="e.g. Mexican, Mediterranean")
            
        instructions = st.text_area("Cooking Instructions *", placeholder="Describe how to prepare this dish step by step...")
        image_url_input = st.text_input("Recipe Image URL (Optional)", placeholder="https://images.unsplash.com/photo-...")

        st.markdown("##### Ingredients Required")
        selected_ing_ids = st.multiselect(
            "Select Existing Ingredients",
            options=all_ingredients_df["ingredient_id"].tolist() if not all_ingredients_df.empty else [],
            format_func=lambda x: all_ingredients_df.loc[all_ingredients_df['ingredient_id'] == x, 'name'].values[0] if not all_ingredients_df.empty else str(x)
        )
        new_ings_input = st.text_input("Or add new ingredients (comma separated)", placeholder="e.g. Cumin, Basil Leaves, Soy Sauce")
        default_unit = st.selectbox("Unit for these ingredients", ["grams", "kg", "can", "pack", "liter", "cloves", "pieces"])

        st.markdown("##### Nutritional Information")
        n1, n2, n3, n4 = st.columns(4)
        cals = n1.number_input("Calories (kcal)", min_value=0, value=350)
        prot = n2.number_input("Protein (g)", min_value=0.0, value=15.0)
        carb = n3.number_input("Carbs (g)", min_value=0.0, value=30.0)
        fats = n4.number_input("Fats (g)", min_value=0.0, value=10.0)

        submitted = st.form_submit_button("Save Recipe to Database", type="primary", use_container_width=True)

        if submitted:
            has_ingredients = bool(selected_ing_ids or new_ings_input.strip())

            if not title or not instructions or not has_ingredients:
                st.error("Please fill in all mandatory fields (*), including at least one ingredient.")
            else:
                new_recipe_id = execute_commit(
                    "INSERT INTO recipes (user_id, title, instructions, image_url, prep_time, servings, difficulty_level) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (user_choice, title, instructions, image_url_input.strip() or None, prep_time, servings, difficulty)
                )

                execute_commit(
                    "INSERT INTO nutrition (recipe_id, calories, protein, carbs, fats) VALUES (%s, %s, %s, %s, %s);",
                    (new_recipe_id, cals, prot, carb, fats)
                )

                final_cat_ids = set(selected_cat_ids)
                if new_cats_input.strip():
                    for c_name in [c.strip() for c in new_cats_input.split(",") if c.strip()]:
                        chk = run_query("SELECT category_id FROM categories WHERE LOWER(category_name) = LOWER(%s);", (c_name,))
                        if not chk.empty:
                            final_cat_ids.add(chk.iloc[0]["category_id"])
                        else:
                            cid = execute_commit("INSERT INTO categories (category_name) VALUES (%s);", (c_name,))
                            if cid:
                                final_cat_ids.add(cid)

                for cid in final_cat_ids:
                    execute_commit("INSERT INTO recipe_categories (recipe_id, category_id) VALUES (%s, %s);", (new_recipe_id, cid))

                final_ing_ids = set(selected_ing_ids)
                if new_ings_input.strip():
                    for i_name in [i.strip() for i in new_ings_input.split(",") if i.strip()]:
                        chk = run_query("SELECT ingredient_id FROM ingredients WHERE LOWER(name) = LOWER(%s);", (i_name,))
                        if not chk.empty:
                            final_ing_ids.add(chk.iloc[0]["ingredient_id"])
                        else:
                            iid = execute_commit("INSERT INTO ingredients (name, cost_per_unit, stock_quantity) VALUES (%s, 0.00, 0.00);", (i_name,))
                            if iid:
                                final_ing_ids.add(iid)

                for iid in final_ing_ids:
                    execute_commit(
                        "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit) VALUES (%s, %s, %s, %s);",
                        (new_recipe_id, iid, 1.00, default_unit)
                    )

                st.success(f"Recipe '{title}' created successfully!")
                st.rerun()

# -----------------------------------------------------------------------------
# VIEW 3: DATABASE INSPECTOR (HIDDEN BEHIND ADMIN TOGGLE)
# -----------------------------------------------------------------------------
elif active_page == ":material/database: Database Inspector":
    st.subheader("Inspect Relational Database Tables")
    table_list = [
        "users", "categories", "recipes", "recipe_categories",
        "ingredients", "recipe_ingredients", "nutrition",
        "reviews", "meal_plans", "audit_logs"
    ]
    inspected_table = st.selectbox("Choose Table:", table_list)
    raw_df = run_query(f"SELECT * FROM {inspected_table};")
    st.dataframe(raw_df, use_container_width=True)
    st.caption(f"Total Rows: {len(raw_df)} | Columns: {len(raw_df.columns)}")