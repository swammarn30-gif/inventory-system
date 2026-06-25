import streamlit as st
import pandas as pd
import sqlite3
import datetime
from datetime import timedelta

# ==================== App Setup ====================
st.set_page_config(layout="wide", page_title="Inventory System")

# ==================== Database Setup ====================
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, name TEXT, opening INTEGER, qty_in INTEGER, issued INTEGER, returned INTEGER, damage INTEGER, used INTEGER, stock INTEGER, note TEXT)''')
    conn.commit()
    conn.close()

def get_daily_records(date_str, category):
    conn = sqlite3.connect('inventory.db')
    df = pd.read_sql_query("SELECT * FROM inventory WHERE date = ? AND category = ?", conn, params=(date_str, category))
    conn.close()
    return df

def save_daily_records(df, date_str, category):
    conn = sqlite3.connect('inventory.db')
    conn.execute("DELETE FROM inventory WHERE date = ? AND category = ?", (date_str, category))
    for _, row in df.iterrows():
        used = row['issued'] - row['returned']
        stock = row['opening'] + row['qty_in'] - used - row['damage']
        conn.execute('INSERT INTO inventory (date, category, name, opening, qty_in, issued, returned, damage, used, stock, note) VALUES (?,?,?,?,?,?,?,?,?,?,?)', (date_str, category, row['name'], row['opening'], row['qty_in'], row['issued'], row['returned'], row['damage'], used, stock, row['note']))
    conn.commit()
    conn.close()

# ==================== အဓိက Logic (အရင်နေ့ပြင်ရင် နောက်နေ့တွေလိုက်ပြောင်း) ====================
def cascade_update_to_future(start_date, item_name, new_opening):
    current_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    conn = sqlite3.connect('inventory.db')
    while True:
        next_date_str = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
        c = conn.cursor()
        c.execute("SELECT id, opening, qty_in, issued, returned, damage FROM inventory WHERE date = ? AND name = ?", (next_date_str, item_name))
        row = c.fetchone()
        if not row: break
        # Re-calculate and update the next day
        new_stock = new_opening + row[2] - (row[3] - row[4]) - row[5]
        conn.execute('UPDATE inventory SET opening = ?, used = ?, stock = ? WHERE id = ?', (new_opening, row[3] - row[4], new_stock, row[0]))
        new_opening = new_stock
        current_date = current_date + timedelta(days=1)
    conn.commit()
    conn.close()

# ==================== UI / Dashboard ====================
init_db()

# Sidebar
with st.sidebar:
    st.header("📦 Inventory System")
    st.write("👤 swarnmam30@gmail.com")
    st.divider()
    st.subheader("MAIN")
    st.button("🏠 Dashboard", disabled=True)
    st.divider()
    st.write("REPORTS")
    st.button("📊 Production Report")
    st.button("📦 Packaging Report")

# Top Header
st.title("📋 Production & Packaging Inventory System")
selected_date = st.date_input("Select Date", value=datetime.date.today())

# Summary Cards (Metric နဲ့ ရိုးရှင်းအောင်လုပ်ထားပါတယ်)
st.subheader("Summary Metrics")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📦 Total Production Stock", "15,420")
c2.metric("📦 Total Packaging Stock", "8,630")
c3.metric("⬇️ Total Used (Today)", "5,210")
c4.metric("⚠️ Total Damage (Today)", "125")
c5.metric("📋 Total Items", "12")

# Production / Packaging Tabs
tab1, tab2 = st.tabs(["📊 Production", "📦 Packaging"])

def render_table(category):
    date_str = selected_date.strftime("%Y-%m-%d")
    df = get_daily_records(date_str, category)
    if df.empty:
        df = pd.DataFrame(columns=["name", "opening", "qty_in", "issued", "returned", "damage", "note"])
    st.subheader(f"{category} Inventory")
    
    # ⚠️ Error မတက်အောင် တစ်ကြောင်းတည်း ရေးထားပါတယ် (Copy ကူးလို့ အလွယ်) ⚠️
    edited_df = st.data_editor(df, column_config={"opening": st.column_config.NumberColumn("Opening", disabled=True), "used": st.column_config.NumberColumn("Used", disabled=True), "stock": st.column_config.NumberColumn("Stock", disabled=True)}, disabled=["opening", "used", "stock"], num_rows="dynamic", use_container_width=True, hide_index=True, key=f"editor_{category}")
    
    if st.button(f"💾 Save {category} Changes", key=f"save_{category}"):
        save_daily_records(edited_df, date_str, category)
        for _, row in edited_df.iterrows():
            if pd.notna(row['name']) and row['name'] != "":
                closing_stock = row['opening'] + row['qty_in'] - (row['issued'] - row['returned']) - row['damage']
                cascade_update_to_future(date_str, row['name'], closing_stock)
        st.success("✅ Saved! Future dates updated automatically!")
        st.rerun()

with tab1:
    render_table("Production")

with tab2:
    render_table("Packaging")

st.caption("📌 Used = Issued - Return | Stock = Opening + In - Used - Damage")
