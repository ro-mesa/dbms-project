import streamlit as st
import pandas as pd
from db_connection import get_db_connection

st.set_page_config(page_title="Recipe Management Portal", layout="wide")

st.title("🍳 Recipe Management Portal")

conn = get_db_connection()

if conn:
    try:
        # Fetch recipes with category information
        query = """
            SELECT 
                r.recipe_id,
                r.title,
                r.cooking_time,
                r.servings,
                r.difficulty_level,
                c.category_name
            FROM Recipes r
            LEFT JOIN Categories c ON r.category_id = c.category_id;
        """
        df = pd.read_sql(query, conn)

        st.subheader("Browse Recipes")
        st.dataframe(df,width="stretch")

    except Exception as e:
        st.error(f"Error executing query: {e}")
    finally:
        conn.close()
else:
    st.error("Failed to connect to the database. Check your configuration.")