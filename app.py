import streamlit as st
import pandas as pd
from db_connection import get_db_connection

# Page configuration
st.set_page_config(page_title="FlavorCraft Recipe Portal", page_icon="🍳", layout="wide")

# Modern Culinary Styling
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        div[data-testid="stMetricValue"] { font-size: 1.3rem; color: #ff5722; }
        .recipe-title { font-size: 1.15rem; font-weight: 700; margin-top: 0.4rem; }
        .recipe-badge { 
            display: inline-block; 
            padding: 2px 8px; 
            font-size: 0.75rem; 
            border-radius: 6px; 
            font-weight: 600; 
            margin-right: 5px;
        }
        .badge-easy { background-color: #d4edda; color: #155724; }
        .badge-medium { background-color: #fff3cd; color: #856404; }
        .badge-hard { background-color: #f8d7da; color: #721c24; }
    </style>
""", unsafe_allow_html=True)

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

# Mapping food keywords to fallback Unsplash food images
FALLBACK_IMAGES = {
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop",
    "pasta": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=600&auto=format&fit=crop",
    "cake": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop",
    "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop",
    "tea": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop",
    "chai": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop",
    "biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop",
    "tiramisu": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&auto=format&fit=crop",
    "default": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=600&auto=format&fit=crop"
}

def get_recipe_image(title):
    for kw, url in FALLBACK_IMAGES.items():
        if kw in title.lower():
            return url
    return FALLBACK_IMAGES["default"]

# -----------------------------------------------------------------------------
# Recipe Details Dialog (View Only)
# -----------------------------------------------------------------------------
@st.dialog("Recipe Details")
def show_recipe_modal(recipe_id, title):
    st.subheader(title)
    st.image(get_recipe_image(title), use_container_width=True)
    
    detail_query = """
        SELECT r.instructions, r.prep_time, r.servings, r.difficulty_level,
               n.calories, n.protein, n.carbs, n.fats
        FROM recipes r
        LEFT JOIN nutrition n ON r.recipe_id = n.recipe_id
        WHERE r.recipe_id = %s;
    """
    df = run_query(detail_query, (recipe_id,))
    
    if not df.empty:
        rec = df.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Prep Time", f"{rec['prep_time']}m")
        c2.metric("Servings", rec['servings'])
        c3.metric("Calories", f"{rec['calories'] or 0} kcal")
        c4.metric("Protein", f"{rec['protein'] or 0}g")
        
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
            st.markdown(f"⭐ **{row['rating']}/5** by *{row['username']}*")
            if row['comment']:
                st.caption(f'"{row["comment"]}"')
    else:
        st.caption("No reviews yet for this recipe.")

# -----------------------------------------------------------------------------
# Recipe Edit Dialog (UPDATE SQL Implementation)
# -----------------------------------------------------------------------------
@st.dialog("✏️ Edit Recipe")
def show_edit_modal(recipe_id):
    rec_query = """
        SELECT r.title, r.instructions, r.prep_time, r.servings, r.difficulty_level,
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
        
        save_btn = st.form_submit_button("Update Recipe in Database", use_container_width=True)
        
        if save_btn:
            # 1. UPDATE recipes table
            upd_recipe = """
                UPDATE recipes 
                SET title = %s, instructions = %s, prep_time = %s, servings = %s, difficulty_level = %s
                WHERE recipe_id = %s;
            """
            execute_commit(upd_recipe, (new_title, new_instructions, new_prep, new_servings, new_diff, recipe_id))
            
            # 2. UPDATE nutrition table
            upd_nutri = """
                UPDATE nutrition 
                SET calories = %s, protein = %s, carbs = %s, fats = %s
                WHERE recipe_id = %s;
            """
            execute_commit(upd_nutri, (new_cals, new_prot, new_carbs, new_fats, recipe_id))
            
            st.success("Recipe updated successfully!")
            st.rerun()

# -----------------------------------------------------------------------------
# Main Application Header & Tabs
# -----------------------------------------------------------------------------
st.title("🍳 FlavorCraft Recipe Portal")
tab1, tab2, tab3 = st.tabs(["🍽️ Recipe Feed", "➕ Add Recipe", "📊 Database Inspector"])

# -----------------------------------------------------------------------------
# TAB 1: RECIPE FEED (ENHANCED CARD UI WITH EDIT)
# -----------------------------------------------------------------------------
with tab1:
    # Top Stats Row
    total_recipes = run_query("SELECT COUNT(*) AS total FROM recipes;").iloc[0]["total"]
    total_reviews = run_query("SELECT COUNT(*) AS total FROM reviews;").iloc[0]["total"]
    avg_rating = run_query("SELECT ROUND(AVG(rating), 1) AS avg_r FROM reviews;").iloc[0]["avg_r"] or 0.0
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Total Recipes", total_recipes)
    m_col2.metric("Total Community Reviews", total_reviews)
    m_col3.metric("Platform Rating", f"⭐ {avg_rating} / 5.0")
    st.divider()

    # Filter Bar
    c1, c2 = st.columns([3, 1])
    with c1:
        search_kw = st.text_input("🔍 Search recipes by keyword:", placeholder="e.g. Pasta, Burger, Cake...")
    with c2:
        cat_df = run_query("SELECT category_id, category_name FROM categories;")
        cat_list = ["All Cuisines"] + list(cat_df["category_name"].unique()) if not cat_df.empty else ["All Cuisines"]
        selected_category = st.selectbox("Filter by Category", cat_list)

    feed_query = """
        SELECT r.recipe_id, r.title, r.prep_time, r.difficulty_level,
               u.username AS author, n.calories,
               GROUP_CONCAT(c.category_name SEPARATOR ', ') AS categories
        FROM recipes r
        JOIN users u ON r.user_id = u.user_id
        LEFT JOIN nutrition n ON r.recipe_id = n.recipe_id
        LEFT JOIN recipe_categories rc ON r.recipe_id = rc.recipe_id
        LEFT JOIN categories c ON rc.category_id = c.category_id
        GROUP BY r.recipe_id, r.title, r.prep_time, r.difficulty_level, u.username, n.calories;
    """
    recipes = run_query(feed_query)

    if not recipes.empty:
        if search_kw:
            recipes = recipes[recipes["title"].str.contains(search_kw, case=False, na=False)]
        if selected_category != "All Cuisines":
            recipes = recipes[recipes["categories"].str.contains(selected_category, case=False, na=False)]

        st.caption(f"Displaying {len(recipes)} dish(es)")

        cols_per_row = 3
        card_cols = st.columns(cols_per_row)
        for idx, (_, rec) in enumerate(recipes.iterrows()):
            col = card_cols[idx % cols_per_row]
            with col:
                with st.container(border=True):
                    st.image(get_recipe_image(rec['title']), use_container_width=True)
                    st.markdown(f"<div class='recipe-title'>{rec['title']}</div>", unsafe_allow_html=True)
                    st.caption(f"By Chef **{rec['author']}** | *{rec['categories'] or 'General'}*")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Time", f"{rec['prep_time']}m")
                    m2.metric("Level", rec['difficulty_level'])
                    m3.metric("Calories", f"{rec['calories'] or 0}")

                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("View", key=f"view_{rec['recipe_id']}", use_container_width=True):
                            show_recipe_modal(rec['recipe_id'], rec['title'])
                    with b2:
                        if st.button("✏️ Edit", key=f"edit_{rec['recipe_id']}", use_container_width=True):
                            show_edit_modal(rec['recipe_id'])
    else:
        st.info("No recipes found matching your search.")

# -----------------------------------------------------------------------------
# TAB 2: ADD RECIPE (DYNAMIC FORM)
# -----------------------------------------------------------------------------
with tab2:
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

        submitted = st.form_submit_button("Save Recipe to Database", use_container_width=True)

        if submitted:
            has_ingredients = bool(selected_ing_ids or new_ings_input.strip())

            if not title or not instructions or not has_ingredients:
                st.error("Please fill in all mandatory fields (*), including at least one ingredient.")
            else:
                new_recipe_id = execute_commit(
                    "INSERT INTO recipes (user_id, title, instructions, prep_time, servings, difficulty_level) VALUES (%s, %s, %s, %s, %s, %s);",
                    (user_choice, title, instructions, prep_time, servings, difficulty)
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
# TAB 3: DATABASE INSPECTOR (EVALUATION READY)
# -----------------------------------------------------------------------------
with tab3:
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
