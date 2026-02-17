import streamlit as st
import pandas as pd
from datetime import datetime
import json

# 🌐 ONLINE-READY SINGLE FILE APP
st.set_page_config(page_title="Office Stock List", page_icon="📦", layout="wide")

# 📊 IN-MEMORY STORAGE (resets on restart - perfect for demo)
if "stocks" not in st.session_state:
    st.session_state.stocks = {}
if "history" not in st.session_state:
    st.session_state.history = []

def save_stock(name, quantity):
    name = name.strip()
    if name in st.session_state.stocks:
        st.session_state.stocks[name] += quantity
        action = "UPDATE"
    else:
        st.session_state.stocks[name] = quantity
        action = "ADD"
    
    # Log to history
    st.session_state.history.append({
        "date_time": datetime.now().isoformat(),
        "stock_name": name,
        "quantity": quantity,
        "person": "Silver Spring",
        "action": action
    })
    st.rerun()

def take_out_stock(stock_name, quantity, person):
    if stock_name in st.session_state.stocks and st.session_state.stocks[stock_name] >= quantity:
        st.session_state.stocks[stock_name] -= quantity
        st.session_state.history.append({
            "date_time": datetime.now().isoformat(),
            "stock_name": stock_name,
            "quantity": quantity,
            "person": person,
            "action": "REMOVE"
        })
        st.rerun()
        return True
    return False

def clear_all():
    st.session_state.stocks = {}
    st.session_state.history = []
    st.rerun()

# HEADER
st.title("🏢 **Silver Spring Stock Manager**")
st.caption("📦 Live Stock | ➕ Add | ➖ Take Out | 📋 History | 🌐 LIVE ON WEB!")

# STATS
col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total Items", len(st.session_state.stocks))
col2.metric("🟢 In Stock", len([v for v in st.session_state.stocks.values() if v > 0]))
col3.metric("📈 Transactions", len(st.session_state.history))
col4.metric("👥 People", len(set([h['person'] for h in st.session_state.history if h['person'] != 'Silver Spring'])))

st.markdown("---")

# MAIN DASHBOARD
col_left, col_right = st.columns([2, 1.5])

with col_left:
    st.subheader("📦 **Current Stock**")
    if not st.session_state.stocks:
        st.info("🎉 Empty! Add stock below 👇")
    else:
        search_term = st.text_input("🔍 Search:", placeholder="Pens...")
        
        for name, qty in st.session_state.stocks.items():
            if search_term.lower() in name.lower():
                if qty > 10:
                    bg_color, text_color, emoji, status = "#d4edda", "#155724", "🟢", "PLENTY"
                elif qty > 0:
                    bg_color, text_color, emoji, status = "#fff3cd", "#856404", "🟡", "LOW"
                else:
                    bg_color, text_color, emoji, status = "#f8d7da", "#721c24", "🔴", "OUT"
                
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {bg_color}, #f8f9fa); 
                               padding: 20px; border-radius: 15px; margin: 10px 0; 
                               border-left: 6px solid {text_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h3 style="margin: 0; font-size: 1.4em; color: {text_color};">{name}</h3>
                            <span style="font-size: 2em; font-weight: bold;">{emoji}</span>
                        </div>
                        <div style="font-size: 2.2em; font-weight: bold; color: {text_color}; margin: 10px 0;">
                            **{qty}**
                        </div>
                        <div style="color: {text_color}; font-size: 0.9em; opacity: 0.8;">
                            💾 {status}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

with col_right:
    st.subheader("📋 **Transaction History**")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        df_history['date_time'] = pd.to_datetime(df_history['date_time']).dt.strftime('%H:%M')
        df_history = df_history.sort_values('date_time', ascending=False)
        
        st.dataframe(df_history[['date_time', 'stock_name', 'quantity', 'person', 'action']],
                    use_container_width=True, height=400)
    else:
        st.info("No transactions yet!")

# ACTIONS
st.markdown("---")
tab1, tab2 = st.tabs(["➕ Add Stock", "➖ Take Out"])

with tab1:
    col1, col2 = st.columns(2)
    name = col1.text_input("📝 Product Name")
    qty = col2.number_input("➕ Quantity", min_value=1, value=1)
    if st.button("➕ Add Stock", use_container_width=True):
        save_stock(name, qty)
        st.success(f"✅ {name} (+{qty}) added!")

with tab2:
    col1, col2, col3 = st.columns(3)
    stock_list = list(st.session_state.stocks.keys())
    stock_name = col1.selectbox("📦 Stock:", ["-- Select --"] + stock_list)
    person = col2.selectbox("👤 Person:", ["Abul", "Balaji", "Vibin"])
    qty_out = col3.number_input("📤 Qty Out", min_value=1, value=1)
    
    if stock_name != "-- Select --" and st.button("➖ Take Out", use_container_width=True):
        if take_out_stock(stock_name, qty_out, person):
            st.success(f"✅ {qty_out} {stock_name} → {person}!")
        else:
            st.error("❌ Not enough stock!")

# RESET
st.markdown("---")
if st.button("🗑️ CLEAR ALL DATA", type="primary"):
    clear_all()
    st.success("✅ Reset complete!")
