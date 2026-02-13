# streamlit_app.py (Snowsight version)
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("🥤🥤🥤 **Choose the fruits you want in your custom Smoothie!** 🥤🥤🥤")

# ✅ Get the session directly from Snowflake
session = get_active_session()

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
st.dataframe(data=my_dataframe, use_container_width=True)

# Multiselect with a hard cap at 5
fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()
ingredients_list = st.multiselect("Choose up to 5 ingredients:", options=fruit_options, max_selections=5)

if len(ingredients_list) == 5:
    st.info("You can only select up to 5 options. Remove one to add a different fruit.")

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    # NOTE: This simple 2-column INSERT only works if your table has defaults for other required cols.
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write("SQL to be executed:")
    st.code(my_insert_stmt)

    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt).collect()
            st.success("Your Smoothie is ordered! ✅")
        except Exception as e:
            st.error(f"Something went wrong while submitting your order: {e}")
else:
    st.caption("👀 Pick some fruits above to enable submitting your order.")
