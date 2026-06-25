import streamlit as st

st.set_page_config(
    page_title="Inventory System",
    layout="wide"
)

# Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

EMAIL = "swammarn30@gmail.com"
PASSWORD = "200323"

if not st.session_state.logged_in:

    st.title("Inventory Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email == EMAIL and password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong Email or Password")

    st.stop()

# Dashboard
st.title("Inventory Management System")

page = st.sidebar.selectbox(
    "Department",
    ["Production", "Packaging"]
)

date = st.date_input("Select Date")

st.subheader(f"{page} Inventory")

columns = [
    "Name",
    "Opening",
    "In",
    "Issued",
    "Return",
    "Damage",
    "Used",
    "Stock",
    "Note"
]

data = []

for i in range(20):
    data.append({
        "Name": "",
        "Opening": 0,
        "In": 0,
        "Issued": 0,
        "Return": 0,
        "Damage": 0,
        "Used": 0,
        "Stock": 0,
        "Note": ""
    })

st.data_editor(
    data,
    use_container_width=True,
    num_rows="dynamic"
)
