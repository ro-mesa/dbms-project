import streamlit as st
import pandas as pd
from db_connection import get_db_connection

# Page configuration
st.set_page_config(page_title="FlavorCraft Recipe Portal", page_icon="🍳", layout="wide")

# Modern Minimal Styling
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        div[data-testid="stMetricValue"] { font-size: 1.4rem; color: #ff4b4b; }
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

def execute_commit(query, params):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    return None

# -----------------------------------------------------------------------------
# Recipe Details Dialog (Modal Popup)
# -----------------------------------------------------------------------------
@st.dialog("Recipe Details")
def show_recipe_modal(recipe_id, title):
    st.subheader(title)
    
    # Query recipe details, instructions, nutrition
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
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Prep Time", f"{rec['prep_time']}m")
        col2.metric("Servings", rec['servings'])
        col3.metric("Calories", f"{rec['calories']} kcal")
        col4.metric("Protein", f"{rec['protein']}g")
        
        st.markdown("### Instructions")
        st.write(rec["instructions"])

    # Query required ingredients
    st.markdown("### Ingredients Required")
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

    # Query reviews
    st.markdown("### Reviews & Ratings")
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
# Main Application Header & Tabs
# -----------------------------------------------------------------------------
st.title("🍳 FlavorCraft Recipe Portal")
tab1, tab2, tab3 = st.tabs(["🍽️ Recipe Feed", "➕ Add Recipe", "📊 Database Inspector"])

# -----------------------------------------------------------------------------
# TAB 1: RECIPE FEED (CARD UI)
# -----------------------------------------------------------------------------
with tab1:
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
                    st.subheader(rec['title'])
                    st.caption(f"By Chef **{rec['author']}** | Cuisines: *{rec['categories']}*")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Time", f"{rec['prep_time']}m")
                    m2.metric("Level", rec['difficulty_level'])
                    m3.metric("Calories", f"{rec['calories'] or 0}")

                    if st.button("View Full Recipe", key=f"btn_{rec['recipe_id']}", use_container_width=True):
                        show_recipe_modal(rec['recipe_id'], rec['title'])
    else:
        st.info("No recipes found matching your search.")

# -----------------------------------------------------------------------------
# TAB 2: ADD RECIPE (DYNAMIC CATEGORIES & INGREDIENTS)
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
                # 1. Insert into recipes
                ins_recipe = """
                    INSERT INTO recipes (user_id, title, instructions, prep_time, servings, difficulty_level)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                new_recipe_id = execute_commit(ins_recipe, (user_choice, title, instructions, prep_time, servings, difficulty))

                # 2. Insert into nutrition
                ins_nutri = """
                    INSERT INTO nutrition (recipe_id, calories, protein, carbs, fats)
                    VALUES (%s, %s, %s, %s, %s);
                """
                execute_commit(ins_nutri, (new_recipe_id, cals, prot, carb, fats))

                # 3. Process Categories
                final_cat_ids = set(selected_cat_ids)
                if new_cats_input.strip():
                    for c_name in [c.strip() for c in new_cats_input.split(",") if c.strip()]:
                        chk = run_query("SELECT category_id FROM categories WHERE LOWER(category_name) = LOWER(%s);", (c_name,))
                        if not chk.empty:
                            final_cat_ids.add(chk.iloc[0]["category_id"])
                        else:
                            new_cid = execute_commit("INSERT INTO categories (category_name) VALUES (%s);", (c_name,))
                            if new_cid:
                                final_cat_ids.add(new_cid)

                for cid in final_cat_ids:
                    execute_commit("INSERT INTO recipe_categories (recipe_id, category_id) VALUES (%s, %s);", (new_recipe_id, cid))

                # 4. Process Ingredients
                final_ing_ids = set(selected_ing_ids)
                if new_ings_input.strip():
                    for i_name in [i.strip() for i in new_ings_input.split(",") if i.strip()]:
                        chk = run_query("SELECT ingredient_id FROM ingredients WHERE LOWER(name) = LOWER(%s);", (i_name,))
                        if not chk.empty:
                            final_ing_ids.add(chk.iloc[0]["ingredient_id"])
                        else:
                            new_iid = execute_commit("INSERT INTO ingredients (name, cost_per_unit, stock_quantity) VALUES (%s, 0.00, 0.00);", (i_name,))
                            if new_iid:
                                final_ing_ids.add(new_iid)

                for iid in final_ing_ids:
                    ins_ri = """
                        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit)
                        VALUES (%s, %s, %s, %s);
                    """
                    execute_commit(ins_ri, (new_recipe_id, iid, 1.00, default_unit))

                st.success(f"Recipe '{title}' created successfully with ID: {new_recipe_id}!")
                st.rerun()

# -----------------------------------------------------------------------------
# TAB 3: DATABASE INSPECTOR (EVALUATION READY)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Inspect Relational Database Tables")
    st.caption("Direct, unmodified view of tables stored inside MySQL `recipe_portal`.")
    
    table_list = [
        "users", "categories", "recipes", "recipe_categories",
        "ingredients", "recipe_ingredients", "nutrition",
        "reviews", "meal_plans", "audit_logs"
    ]
    inspected_table = st.selectbox("Choose Table:", table_list)
    raw_df = run_query(f"SELECT * FROM {inspected_table};")
    st.dataframe(raw_df, use_container_width=True)
    st.caption(f"Total Rows: {len(raw_df)} | Columns: {len(raw_df.columns)}")