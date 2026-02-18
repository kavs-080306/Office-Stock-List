import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_BASE = "http://localhost:5001/api"

st.set_page_config(page_title="Office Stock Manager", page_icon="📦", layout="wide")

def get_stocks():
    try:
        resp = requests.get(f"{API_BASE}/stocks")
        return resp.json() if resp.status_code == 200 else []
    except:
        return []

def get_history():
    try:
        resp = requests.get(f"{API_BASE}/history")
        return resp.json() if resp.status_code == 200 else []
    except:
        return []

def update_stock(stock_id, quantity):
    resp = requests.put(f"{API_BASE}/stocks/{stock_id}", json={"quantity": int(quantity)})
    return resp.status_code == 200

def add_stock(name, quantity, category):
    try:
        resp = requests.post(f"{API_BASE}/stocks", json={"name": name, "quantity": int(quantity), "category": category})
        return resp.status_code in [200, 201]
    except:
        return False

def remove_stock(name, quantity, person):
    try:
        resp = requests.post(f"{API_BASE}/stocks/remove", json={"name": name, "quantity": int(quantity), "person": person})
        return resp.status_code in [200, 201]
    except:
        return False

# HEADER
st.title("🏢 **Office Stock Manager**")
st.caption("📦 Current Stock | ➕ Add Stock | ➖ Take Out | 📋 History - ALL IN ONE PAGE!")

# DASHBOARD ROW 1: Current Stocks + Quick Stats
col1, col2, col3, col4 = st.columns(4)
stocks = get_stocks()
history = get_history()

col1.metric("📦 Total Items", len(stocks))
col2.metric("📊 In Stock", len([s for s in stocks if s['quantity'] > 0]))
col3.metric("📈 Total History", len(history))
col4.metric("👥 People", len(set([h['person'] for h in history if h['person'] != 'Stock Manager'])))

st.markdown("---")

# ROW 2: Current Stock List (Left) + History (Right) 
col_left, col_right = st.columns([2, 1.5])

with col_left:
    st.subheader("📦 **Current Stock**")
    
    if not stocks:
        st.info("🎉 Empty! Add stock below 👇")
    else:
        df_stocks = pd.DataFrame(stocks)
        
        # Filters
        search_term = st.text_input("🔍 Search:", placeholder="Pens...")
        sort_option = st.selectbox("Sort:", ["Name", "Quantity Low-High", "Quantity High-Low"])
        
        # Filter & Sort
        df_filtered = df_stocks
        if search_term:
            df_filtered = df_filtered[df_filtered['name'].str.contains(search_term, case=False)]
        
        if sort_option == "Name":
            df_display = df_filtered.sort_values('name')
        elif sort_option == "Quantity Low-High":
            df_display = df_filtered.sort_values('quantity')
        else:
            df_display = df_filtered.sort_values('quantity', ascending=False)
        
        # Stock Cards
        for _, row in df_display.iterrows():
            color = "🟢" if row['quantity'] > 0 else "🔴"
            st.markdown(f"""
                <div style="background: linear-gradient(90deg, {'#d4edda' if row['quantity']>0 else '#f8d7da'}, white); 
                           padding: 15px; border-radius: 10px; margin: 5px 0; border-left: 5px solid {'green' if row['quantity']>0 else 'red'};">
                    <h3 style="margin: 0;">{row['name']}</h3>
                    <p style="font-size: 24px; margin: 5px 0; color: {'green' if row['quantity']>0 else 'red'};">
                        **{color} {row['quantity']}**
                    </p>
                    <small>{row['category']} | {row.get('updatedAt', 'Recent')}</small>
                </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("📋 **Transaction History** 📋")
    
    if history:
        # ✅ SHOW ALL TRANSACTIONS (NO LIMIT!)
        df_history = pd.DataFrame(history)
        df_history['date_time'] = pd.to_datetime(df_history['date_time']).dt.strftime('%d/%m %H:%M')
        
        # Add search filter for history
        history_search = st.text_input("🔍 Search history:", placeholder="Balaji, Pens...")
        if history_search:
            df_history = df_history[df_history.apply(lambda row: history_search.lower() in str(row).lower(), axis=1)]
        
        # Sort by date (newest first)
        df_history = df_history.sort_values('date_time', ascending=False)
        
        # Full history table - Scrollable
        st.dataframe(
            df_history[['date_time', 'stock_name', 'quantity', 'person', 'action']],
            column_config={
                "date_time": "Date",
                "stock_name": "Item", 
                "quantity": st.column_config.NumberColumn("Qty", format="%.0f"),
                "person": "Person",
                "action": st.column_config.SelectboxColumn("Action")
            },
            use_container_width=True,
            height=400  # Scrollable full height
        )
        
        # Summary stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Total Records", len(df_history))
        col2.metric("➕ Added", len(df_history[df_history['action'] == 'ADD']))
        col3.metric("➖ Taken Out", len(df_history[df_history['action'] == 'REMOVE']))
        
    else:
        st.info("📝 No transactions yet! Add or take out stock to see history.")

# ROW 3: Action Buttons
st.markdown("---")
tab1, tab2 = st.tabs(["➕ Add Stock", "➖ Take Out Stock"])

with tab1:
    with st.form("add_form"):
        col1, col2, col3 = st.columns(3)
        with col1: name = st.text_input("Product Name", placeholder="Pens...")
        with col2: quantity = st.number_input("Qty", min_value=1, value=1)
        with col3: category = st.selectbox("Category", ["General", "Electronics", "Office Supplies", "Stationery"])
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.form_submit_button("➕ Add Stock", use_container_width=True):
            if add_stock(name.strip(), quantity, category):
                st.success(f"✅ **{name}** ({quantity}) added/updated!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed!")
        col_btn2.form_submit_button("🔄 Refresh")

with tab2:
    with st.form("remove_form"):
        col1, col2, col3 = st.columns(3)
        with col1: person = st.selectbox("👤 Given to:", ["Abul", "Balaji", "Vibin"])
        with col2: 
            stock_names = [s['name'] for s in stocks]
            selected_stock = st.selectbox("📦 Stock:", stock_names if stock_names else ["No stock"])
        with col3: quantity_out = st.number_input("Qty Out", min_value=1, value=1)
        
        if selected_stock != "No stock":
            current_stock = next((s for s in stocks if s['name'] == selected_stock), None)
            if current_stock:
                st.info(f"📊 **Available:** {current_stock['quantity']} | Max: {current_stock['quantity']}")
                quantity_out = st.number_input("Qty Out", min_value=1, value=1, 
                                             max_value=current_stock['quantity'], key="qty_out2")
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.form_submit_button("➖ Take Out", use_container_width=True):
            if remove_stock(selected_stock, quantity_out, person):
                st.success(f"✅ **{quantity_out}** {selected_stock} → **{person}**!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed!")
        col_btn2.form_submit_button("🔄 Refresh")

# FOOTER
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    ✅ **Live Data** | 🔄 **Auto Refresh** | 💾 **Permanent Storage** | 🌐 **Network Ready**
</div>
""", unsafe_allow_html=True)
