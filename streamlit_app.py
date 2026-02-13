
# streamlit_app.py
import streamlit as st
from snowflake.snowpark.functions import col

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("🥤🥤🥤 **Choose the fruits you want in your custom Smoothie!** 🥤🥤🥤")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

# ✅ Snowflake session via Streamlit connection named "snowflake"
#    Requires [connections.snowflake] block in secrets (see templates above)
cnx = st.connection("snowflake")
session = cnx.session()

# Load available fruits
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)
st.dataframe(data=my_dataframe, use_container_width=True)

# Limit to 5
fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5,
)

# Friendly hint at cap
if len(ingredients_list) == 5:
    st.info("You can only select up to 5 options. Remove one to add a different fruit.")

# Only run insertion logic if ingredients selected
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    # ⚠️ This assumes your ORDERS table has defaults for any other required columns.
    # If you see "expecting 5 but got 2", we must include the other columns explicitly.
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
