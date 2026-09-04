import streamlit as st
import pandas as pd
from db_connection import get_db_connection

st.set_page_config(page_title="Recipe Management Portal", layout="wide", page_icon="🍳")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["📊 Database Viewer (Stage 1)", "🍳 User Interface (Stage 2)"]
)

conn = get_db_connection()

if not conn:
    st.error("Could not establish a connection to the MySQL database. Ensure your server is running.")
    st.stop()

# =========================================================================
# PAGE 1: STAGE 1 - DATABASE VIEWER (RAW TABLES & STRUCTURE)
# =========================================================================
if page == "📊 Database Viewer (Stage 1)":
    st.title("📊 Database Table Inspector")
    st.write("Inspect live data across all entities in the `recipe_portal` database.")

    table_list = [
        "Recipe Overview (Joined View)",
        "users",
        "categories",
        "recipes",
        "recipe_categories",
        "ingredients",
        "recipe_ingredients",
        "nutrition",
        "reviews",
        "meal_plans",
        "audit_logs"
    ]
    
    selected_table = st.selectbox("Select a table to inspect:", table_list)

    try:
        if selected_table == "Recipe Overview (Joined View)":
            st.subheader("Joined Recipe View")
            query = """
            SELECT 
                r.recipe_id,
                r.title,
                r.prep_time,
                r.servings,
                r.difficulty_level,
                u.username AS author,
                n.calories,
                GROUP_CONCAT(c.category_name SEPARATOR ', ') AS categories
            FROM recipes r
            JOIN users u ON r.user_id = u.user_id
            LEFT JOIN nutrition n ON r.recipe_id = n.recipe_id
            LEFT JOIN recipe_categories rc ON r.recipe_id = rc.recipe_id
            LEFT JOIN categories c ON rc.category_id = c.category_id
            GROUP BY r.recipe_id, r.title, r.prep_time, r.servings, r.difficulty_level, u.username, n.calories;
            """
        else:
            st.subheader(f"Table: `{selected_table}`")
            query = f"SELECT * FROM {selected_table};"

        df = pd.read_sql(query, conn)
        st.dataframe(df, use_container_width=True)
        st.caption(f"Total Rows: {len(df)} | Columns: {len(df.columns)}")

    except Exception as e:
        st.error(f"Error reading table '{selected_table}': {e}")
    finally:
        conn.close()

# =========================================================================
# PAGE 2: STAGE 2 - USER INTERFACE (SEARCH, FILTER & EXPLORE)
# =========================================================================
elif page == "🍳 User Interface (Stage 2)":
    st.title("🍳 Recipe Explorer & Management")
    st.write("Browse, search, and filter recipes interactively.")

    try:
        cat_df = pd.read_sql("SELECT category_id, category_name FROM categories;", conn)
        category_options = ["All"] + list(cat_df["category_name"].unique())

        col1, col2 = st.columns([2, 1])
        with col1:
            search_query = st.text_input("🔍 Search recipe by title:")
        with col2:
            selected_cat = st.selectbox("Filter by Category:", category_options)

        base_query = """
        SELECT 
            r.recipe_id,
            r.title,
            r.prep_time,
            r.servings,
            r.difficulty_level,
            u.username AS author,
            n.calories,
            GROUP_CONCAT(c.category_name SEPARATOR ', ') AS categories
        FROM recipes r
        JOIN users u ON r.user_id = u.user_id
        LEFT JOIN nutrition n ON r.recipe_id = n.recipe_id
        LEFT JOIN recipe_categories rc ON r.recipe_id = rc.recipe_id
        LEFT JOIN categories c ON rc.category_id = c.category_id
        GROUP BY r.recipe_id, r.title, r.prep_time, r.servings, r.difficulty_level, u.username, n.calories;
        """
        recipes_df = pd.read_sql(base_query, conn)

        if search_query:
            recipes_df = recipes_df[recipes_df["title"].str.contains(search_query, case=False, na=False)]
        if selected_cat != "All":
            recipes_df = recipes_df[recipes_df["categories"].str.contains(selected_cat, case=False, na=False)]

        st.subheader(f"Showing {len(recipes_df)} Recipe(s)")
        st.dataframe(recipes_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading UI data: {e}")
    finally:
        conn.close()