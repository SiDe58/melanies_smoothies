# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write(
    "🥤🥤🥤 **Choose the fruits you want in your custom Smoothie!** 🥤🥤🥤"
)

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

# Get Snowflake session
session = get_active_session()

# Load available fruits
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)
st.dataframe(data=my_dataframe, use_container_width=True)

# --- MINIMAL CHANGE #1: limit to 5 using max_selections, and pass plain list of options ---
fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5,
)

# --- MINIMAL CHANGE #2: show a friendly hint when exactly 5 are selected ---
if len(ingredients_list) == 5:
    st.info("You can only select up to 5 options. Remove one to add a different fruit.")

# Only run insertion logic if ingredients selected
if ingredients_list:
    # Join ingredients into a single string
    ingredients_string = " ".join(ingredients_list)

    # Construct SQL safely (same approach you used)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write("SQL to be executed:")
    st.code(my_insert_stmt)

    # Submit button
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")
