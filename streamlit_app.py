
# streamlit_app.py
# NOTE: First run will fail if you haven't configured the Snowflake connection in secrets.
# See "Setup: add your Snowflake connection" below.

import streamlit as st
from snowflake.snowpark.functions import col

st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤", layout="centered")

# Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("🥤🥤🥤 **Choose the fruits you want in your custom Smoothie!** 🥤🥤🥤")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order if name_on_order else "—")

# --- Try to connect to Snowflake via Streamlit connection ---
session = None
conn_error = None
with st.spinner("Connecting to Snowflake…"):
    try:
        # Requires a [connections.snowflake] block in secrets
        cnx = st.connection("snowflake")
        session = cnx.session()
    except Exception as e:
        conn_error = e

# If connection failed, show friendly guidance and stop
if conn_error or session is None:
    st.error("❌ Missing or invalid Snowflake connection configuration.")
    with st.expander("Why this fails on first run (click to expand)"):
        st.write(
            """
            This app is running on Streamlit Cloud/local, so it needs a named connection
            called **`snowflake`** in your Streamlit **secrets**.

            **Rinse & Repeat Workflow**
            1. Open your GitHub repo → `.streamlit/secrets.toml` (create if it doesn't exist).
            2. Paste the connection settings (see template below) and **Commit**.
            3. Switch to your Streamlit tab and **rerun** the app (the deployment auto-picks changes).

            You can also add secrets in Streamlit Cloud: *Manage app → Settings → Secrets*.
            """
        )
        st.markdown("**Template for `.streamlit/secrets.toml`:**")
        st.code(
            """\
[connections.snowflake]
account   = "your_account_identifier"   # e.g., xy12345.eu-central-1
user      = "YOUR_USERNAME"
password  = "YOUR_PASSWORD"             # or use private_key + private_key_password
role      = "YOUR_ROLE"
warehouse = "YOUR_WAREHOUSE"
database  = "SMOOTHIES"
schema    = "PUBLIC"
""",
            language="toml",
        )
    st.stop()

# --- Load available fruits ---
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)
st.dataframe(data=my_dataframe, use_container_width=True)

# --- Limit to 5 using max_selections ---
fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5,
)

# Helpful hint at the cap
if len(ingredients_list) == 5:
    st.info("You can only select up to 5 options. Remove one to add a different fruit.")

# --- Only run insertion logic if ingredients are selected ---
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    # NOTE:
    # This relies on your ORDERS table having defaults for any other NOT NULL columns.
    # If you later see "expecting N values but got 2", extend this INSERT to include
    # those required columns explicitly (e.g., ORDER_UID, ORDER_FILLED, CREATED_AT).
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write("SQL to be executed:")
    st.code(my_insert_stmt, language="sql")

    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt).collect()
            st.success("Your Smoothie is ordered! ✅")
            st.balloons()
        except Exception as e:
            st.error(f"Something went wrong while submitting your order: {e}")
else:
    st.caption("👀 Pick some fruits above to enable submitting your order.")
