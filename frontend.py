import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Office Stock Manager", page_icon="📦", layout="wide")

# Initialize session state
if "stocks" not in st.session_state: 
    st.session_state.stocks = {}
if "history" not in st.session_state: 
    st.session_state.history = []

st.title("📦 Office Stock Manager")
st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# === DOWNLOAD/UPLOAD BUTTONS (TOP) ===
col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Download Stock Data"):
        df_stocks = pd.DataFrame(list(st.session_state.stocks.items()), 
                               columns=['Item', 'Quantity'])
        csv = df_stocks.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Stocks CSV", csv, "stock_data.csv", "text/csv")
with col2:
    uploaded_stocks = st.file_uploader("📤 Upload Stock CSV", type="csv")
    if uploaded_stocks:
        new_stocks = dict(pd.read_csv(uploaded_stocks).values)
        st.session_state.stocks.update(new_stocks)
        st.success("✅ Stocks updated!")

# === STOCK MANAGEMENT ===
st.header("➕ Manage Stock")
col1, col2 = st.columns([3,1])
item_name = col1.text_input("Item Name:")
quantity = col2.number_input("Quantity:", min_value=0, step=1)

if st.button("➕ Add to Stock") and item_name:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.stocks[item_name] = quantity
    st.session_state.history.append({
        'Date': timestamp,
        'Action': 'Added', 
        'Item': item_name,
        'Quantity': quantity
    })
    st.success(f"✅ Added {quantity} {item_name}")
    st.rerun()

if st.button("🔄 Clear All Stock"):
    st.session_state.stocks.clear()
    st.session_state.history.append({
        'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Action': 'Cleared All',
        'Item': 'ALL',
        'Quantity': 0
    })
    st.rerun()

# === CURRENT STOCK ===
st.header("📊 Current Stock")
if st.session_state.stocks:
    df_stocks = pd.DataFrame([
        {'Item': item, 'Quantity': qty} 
        for item, qty in st.session_state.stocks.items()
    ])
    st.dataframe(df_stocks, use_container_width=True)
else:
    st.info("👆 Add items above to see stock")

# === TRANSACTION HISTORY ===
st.header("📈 Transaction History")
if st.session_state.history:
    df_history = pd.DataFrame(st.session_state.history)
    st.dataframe(df_history, use_container_width=True)
    
    # Download history
    col1, col2 = st.columns(2)
    with col1:
        csv_history = df_history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download History", csv_history, "stock_history.csv", "text/csv")
else:
    st.info("👆 Transactions appear here after adding stock")

# === SUMMARY ===
col1, col2, col3 = st.columns(3)
total_items = len(st.session_state.stocks)
total_quantity = sum(st.session_state.stocks.values())
col1.metric("Items", total_items)
col2.metric("Total Quantity", total_quantity)
col3.metric("Transactions", len(st.session_state.history))
