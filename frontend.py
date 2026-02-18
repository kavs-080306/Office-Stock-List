import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Backend API URL - YOUR IP!
API_BASE = "http://10.80.121.67:5000/api"
st.set_page_config(page_title="Office Stock Manager", page_icon="📦", layout="wide")

# 🔍 BACKEND STATUS CHECK (TOP!)
def test_backend():
    try:
        resp = requests.get(f"{API_BASE}/stocks", timeout=3)
        if resp.status_code == 200:
            return True, "🟢 Backend LIVE!"
        else:
            return False, f"🔴 Backend Error {resp.status_code}"
    except Exception as e:
        return False, f"🔴 Backend OFFLINE: {str(e)[:50]}..."

backend_ok, backend_status = test_backend()
st.sidebar.success(backend_status)
if not backend_ok:
    st.sidebar.error("💡 Fix: Check backend terminal + `host='0.0.0.0'`")

# API Functions with DEBUG
def get_stocks():
    try:
        resp = requests.get(f"{API_BASE}/stocks", timeout=5)
        if resp.status_code == 200:
            return resp.json().get('stocks', [])
        st.error(f"❌ Stocks API: {resp.status_code}")
        return []
    except Exception as e:
        st.error(f"❌ Stocks connection: {str(e)}")
        return []

def get_history():
    try:
        resp = requests.get(f"{API_BASE}/history", timeout=5)
        if resp.status_code == 200:
            return resp.json()
        st.error(f"❌ History API: {resp.status_code}")
        return []
    except Exception as e:
        st.error(f"❌ History connection: {str(e)}")
        return []

def add_stock(name, quantity, category):
    try:
        resp = requests.post(f"{API_BASE}/stocks", json={
            "name": name.strip(), "quantity": int(quantity), "category": category
        }, timeout=5)
        if resp.status_code in [200, 201]:
            return True
        st.error(f"❌ Add failed: {resp.status_code} - {resp.text[:100]}")
        return False
    except Exception as e:
        st.error(f"❌ Add error: {str(e)}")
        return False

def remove_stock(name, quantity, person):
    try:
        resp = requests.post(f"{API_BASE}/stocks/remove", json={
            "name": name, "quantity": int(quantity), "person": person
        }, timeout=5)
        if resp.status_code in [200, 201]:
            return True
        st.error(f"❌ Remove failed: {resp.status_code} - {resp.text[:100]}")
        return False
    except Exception as e:
        st.error(f"❌ Remove error: {str(e)}")
        return False

# HEADER
st.title("🏢 **Office Stock Manager**")
st.caption(f"🔄 Backend: {backend_status}")

# DASHBOARD ROW 1: Stats
col1, col2, col3, col4 = st.columns(4)
stocks = get_stocks()
history = get_history()

col1.metric("📦 Total Items", len(stocks))
col2.metric("📊 In Stock", len([s for s in stocks if s.get('quantity', 0) > 0]))
col3.metric("📈 Total History", len(history))
col4.metric("👥 People", len(set([h.get('person', 'Unknown') for h in history])))

st.markdown("---")

# ROW 2: Current Stock + History
col_left, col_right = st.columns([2, 1.5])

with col_left:
    st.subheader("📦 **Current Stock**")
    if not stocks:
        st.info("🎉 Empty! Add stock using ➕ tab 👇")
    else:
        df_stocks = pd.DataFrame(stocks)
        search_term = st.text_input("🔍 Search:", placeholder="Pens...")
        
        df_filtered = df_stocks
        if search_term:
            df_filtered = df_filtered[df_filtered['name'].str.contains(search_term, case=False, na=False)]
        
        for _, row in df_filtered.iterrows():
            color = "🟢" if row['quantity'] > 0 else "🔴"
            st.markdown(f"""
                <div style="background: linear-gradient(90deg, {'#d4edda' if row['quantity']>0 else '#f8d7da'}, white); 
                           padding: 15px; border-radius: 10px; margin: 5px 0; border-left: 5px solid {'green' if row['quantity']>0 else 'red'};">
                <h3 style="margin: 0;">{row['name']}</h3>
                <p style="font-size: 24px; margin: 5px 0; color: {'green' if row['quantity']>0 else 'red'};">
                    **{color} {row['quantity']}**
                </p>
                <small>{row.get('category', 'General')}</small>
                </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("📋 **Transaction History**")
    if history:
        df_history = pd.DataFrame(history)
        if 'date_time' in df_history.columns:
            df_history['date_time'] = pd.to_datetime(df_history['date_time'], errors='coerce').dt.strftime('%d/%m %H:%M')
        df_history = df_history.sort_values('date_time', ascending=False)
        
        # ✅ FIXED: use_container_height → height
        st.dataframe(df_history[['date_time', 'stock_name', 'quantity', 'person', 'action']], 
                    height=400,  # ← Scrollable 400px height
                    use_container_width=True)
    else:
        st.info("📝 No transactions yet!")


# TABS
tab1, tab2 = st.tabs(["➕ Add Stock", "➖ Take Out Stock"])

with tab1:
    with st.form("add_form"):
        col1, col2, col3 = st.columns(3)
        with col1: name = st.text_input("Product Name", placeholder="Pens...")
        with col2: quantity = st.number_input("Qty", min_value=1, value=1)
        with col3: category = st.selectbox("Category", ["General", "Electronics", "Office Supplies", "Stationery"])
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.form_submit_button("➕ Add Stock", use_container_width=True):
            if name.strip():
                if add_stock(name, quantity, category):
                    st.success(f"✅ **{name}** ({quantity}) added!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Backend rejected!")
            else:
                st.error("❌ Enter product name!")
        col_btn2.form_submit_button("🔄 Refresh")

with tab2:
    with st.form("remove_form"):
        col1, col2, col3 = st.columns(3)
        with col1: person = st.selectbox("👤 Given to:", ["Abul", "Balaji", "Vibin", "Stock Manager"])
        with col2: 
            stock_names = [s['name'] for s in stocks]
            selected_stock = st.selectbox("📦 Stock:", [""] + stock_names)
        with col3: quantity_out = st.number_input("Qty Out", min_value=1, value=1)
        
        if selected_stock:
            current_stock = next((s for s in stocks if s['name'] == selected_stock), None)
            if current_stock:
                st.info(f"📊 Available: {current_stock['quantity']}")
                quantity_out = st.number_input("Qty Out", min_value=1, value=1, 
                                             max_value=current_stock['quantity'], key="qty_out_key")
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.form_submit_button("➖ Take Out", use_container_width=True) and selected_stock:
            if remove_stock(selected_stock, quantity_out, person):
                st.success(f"✅ {quantity_out} {selected_stock} → **{person}**!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Remove failed - check backend!")
        col_btn2.form_submit_button("🔄 Refresh")

# FOOTER
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 10px;'>
    🔄 Backend: <strong>{API_BASE}</strong> | {backend_status} | 
    💾 Data saved forever | 👥 Team tracking enabled
</div>
""", unsafe_allow_html=True)
