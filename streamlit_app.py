
# streamlit_app.py
import streamlit as st
from snowflake.snowpark.functions import col

st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("🥤🥤🥤 **Choose the fruits you want in your custom Smoothie!** 🥤🥤🥤")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order if name_on_order else "—")

# --- Get a Snowflake session (standalone) ---
try:
    cnx = st.connection("snowflake")           # Needs [connections.snowflake] in secrets
    session = cnx.session()
except Exception as e:
    st.error("❌ Missing or invalid Snowflake connection configuration.")
    with st.expander("First run? How to fix this"):
        st.markdown(
            "Add a `connections.snowflake` block to your Streamlit secrets "
            "(local: `.streamlit/secrets.toml`; Cloud: *Settings → Secrets*)."
        )
        st.code(
            """\
[connections.snowflake]
account   = "xy12345.eu-central-1"
user      = "YOUR_USERNAME"
password  = "YOUR_PASSWORD"
role      = "YOUR_ROLE"
warehouse = "YOUR_WAREHOUSE"
database  = "SMOOTHIES"
schema    = "PUBLIC"
""", language="toml")
    st.stop()

# --- Query available fruits ---
sp_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
st.dataframe(sp_df, use_container_width=True)

fruit_options = sp_df.to_pandas()["FRUIT_NAME"].tolist()

# --- Limit to 5 ingredients ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5,
)

if len(ingredients_list) == 5:
    st.info("You can only select up to 5 options. Remove one to add a different fruit.")

# --- Insert order (assumes ORDERS table has defaults for other NOT NULL cols) ---
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    insert_sql = f"""
        INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write("SQL to be executed:")
    st.code(insert_sql, language="sql")

    if st.button("Submit Order"):
        try:
            session.sql(insert_sql).collect()
            st.success("Your Smoothie is ordered! ✅")
            st.balloons()
        except Exception as e:
            st.error(f"Something went wrong while submitting your order: {e}")
else:
    st.caption("👀 Pick some fruits above to enable submitting your order.")
