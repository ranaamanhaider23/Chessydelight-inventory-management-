import streamlit as st
import pandas as pd
from datetime import date
import os

# ==========================================
# 🎨 UI & THEME SETUP
# ==========================================
st.set_page_config(page_title="Cheesy Delights | Fast Inventory OS", layout="wide", page_icon="🍕")

st.markdown("""
    <style>
        .stApp { background-color: #0F172A; color: #F8FAFC; }
        
        div[data-testid="stMetric"] {
            background: #1E293B;
            border: 1px solid #334155;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        div[data-testid="stMetric"] label { color: #94A3B8 !important; font-size: 14px !important; font-weight: 600; }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #38BDF8 !important; font-size: 24px !important; font-weight: 700; }

        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            width: 100%;
        }
        
        section[data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1E293B; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📁 DATA INITIALIZATION
# ==========================================
INVENTORY_FILE = "stock_balance.csv"
PURCHASES_FILE = "invoice_history.csv"

# Pre-populating default master items based on your invoice
if not os.path.exists(INVENTORY_FILE):
    df_init = pd.DataFrame([
        {"Item Name": "Dawn Burger Bun (2 pcs pack)", "Category": "Dry / B B", "Current Stock": 2.0, "Unit": "Pcs", "Min Alert": 5},
        {"Item Name": "Arfa Yellow Cheese (2kg pack)", "Category": "Cheese", "Current Stock": 1.0, "Unit": "Pcs", "Min Alert": 2},
        {"Item Name": "Karachi Fajita Topping", "Category": "Topping", "Current Stock": 2.0, "Unit": "Pcs", "Min Alert": 3}
    ])
    df_init.to_csv(INVENTORY_FILE, index=False)

stock_df = pd.read_csv(INVENTORY_FILE)

# ==========================================
# 🧭 SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color: #F59E0B; text-align: center;'>🍕 Cheesy Delights</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; text-align: center; font-size:12px;'>Satyana Road Branch</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    nav = st.radio(
        "MENU",
        [
            "📊 Live Stock Balance",
            "🧾 Quick Invoice Entry",
            "🔥 Record Usage / Sales",
            "🤖 AI Inventory Assistant"
        ]
    )

# ==========================================
# MODULE 1: LIVE STOCK BALANCE
# ==========================================
if nav == "📊 Live Stock Balance":
    st.markdown("<h2 style='color: #38BDF8;'>📦 Live Kitchen Stock Balance</h2>", unsafe_allow_html=True)
    st.caption("Aapke paas kitchen mein is waqt kitna maal bacha hua hai:")
    
    cols = st.columns(3)
    for idx, row in stock_df.iterrows():
        col = cols[idx % 3]
        col.metric(
            label=row["Item Name"], 
            value=f"{row['Current Stock']} {row['Unit']}",
            delta="Low Stock!" if row['Current Stock'] <= row['Min Alert'] else "Sufficient",
            delta_color="inverse" if row['Current Stock'] <= row['Min Alert'] else "normal"
        )

    st.markdown("---")
    st.subheader("📋 Complete Stock Sheet")
    st.dataframe(stock_df, use_container_width=True)

# ==========================================
# MODULE 2: QUICK INVOICE ENTRY
# ==========================================
elif nav == "🧾 Quick Invoice Entry":
    st.markdown("<h2 style='color: #38BDF8;'>🧾 Fast Purchase / Invoice Logging</h2>", unsafe_allow_html=True)
    st.caption("Jab bhi vendor se raw material ka bill aaye, yahan se 2 clicks mein add karein:")
    
    with st.form("invoice_form"):
        c1, c2 = st.columns(2)
        with c1:
            inv_no = st.text_input("Invoice No.", value="608547")
        with c2:
            inv_date = st.date_input("Date", date.today())
        
        st.markdown("---")
        item_selected = st.selectbox("Select Item Received", stock_df["Item Name"].tolist())
        
        c3, c4 = st.columns(2)
        with c3:
            qty_added = st.number_input("Quantity Received (Pcs/Packs)", min_value=1.0, step=1.0, value=1.0)
        with c4:
            rate = st.number_input("Rate per Unit (Rs.)", min_value=0.0, step=10.0, value=100.0)
            
        submit_inv = st.form_submit_button("➕ Save Invoice & Update Stock")
        
        if submit_inv:
            stock_df.loc[stock_df["Item Name"] == item_selected, "Current Stock"] += qty_added
            stock_df.to_csv(INVENTORY_FILE, index=False)
            
            new_purchase = pd.DataFrame([{
                "Invoice No": inv_no,
                "Date": str(inv_date),
                "Item": item_selected,
                "Qty": qty_added,
                "Rate": rate,
                "Total Amount": qty_added * rate
            }])
            
            hist = pd.read_csv(PURCHASES_FILE) if os.path.exists(PURCHASES_FILE) else pd.DataFrame()
            updated_hist = pd.concat([hist, new_purchase], ignore_index=True)
            updated_hist.to_csv(PURCHASES_FILE, index=False)
            
            st.success(f"✅ Added {qty_added} x '{item_selected}' to Stock!")
            st.rerun()

# ==========================================
# MODULE 3: RECORD USAGE / SALES
# ==========================================
elif nav == "🔥 Record Usage / Sales":
    st.markdown("<h2 style='color: #38BDF8;'>🔥 Deduct Used Items From Kitchen</h2>", unsafe_allow_html=True)
    st.caption("Jab items istemal ho jayein toh stock minus karein:")
    
    use_item = st.selectbox("Which item was used?", stock_df["Item Name"].tolist())
    use_qty = st.number_input("How much quantity was used?", min_value=0.1, step=0.5, value=1.0)
    
    if st.button("🔴 Deduct From Stock"):
        curr_val = stock_df.loc[stock_df["Item Name"] == use_item, "Current Stock"].values[0]
        if curr_val >= use_qty:
            stock_df.loc[stock_df["Item Name"] == use_item, "Current Stock"] -= use_qty
            stock_df.to_csv(INVENTORY_FILE, index=False)
            st.success(f"✅ Deducted {use_qty} from {use_item}. Remaining Stock: {curr_val - use_qty}")
            st.rerun()
        else:
            st.error("❌ Stock mein itni quantity nahi hai!")

# ==========================================
# MODULE 4: AI INVENTORY ASSISTANT
# ==========================================
else:
    st.markdown("<h2 style='color: #38BDF8;'>🤖 AI Restaurant Assistant</h2>", unsafe_allow_html=True)
    st.caption("Apne inventory data se mutaliq koi bhi sawal Urdu ya English mein poochein:")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Salam! Main Cheesy Delights ka AI Copilot hoon. Stock balance, low stock, ya purchases ke baray mein poochein!"}
        ]

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_prompt := st.chat_input("Poochein (e.g., 'Cheese kitni bachi hai?' ya 'Kya stock low hai?'):"):
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        prompt_lower = user_prompt.lower()
        ai_reply = ""

        # AI Logic based on current CSV
        if any(k in prompt_lower for k in ["khatam", "low", "kam", "restock"]):
            lows = stock_df[stock_df["Current Stock"] <= stock_df["Min Alert"]]
            if not lows.empty:
                items_list = ", ".join([f"**{r['Item Name']}** ({r['Current Stock']} {r['Unit']} left)" for _, r in lows.iterrows()])
                ai_reply = f"🚨 **Low Stock Alert:** Yeh items minimum level se neeche hain: {items_list}. Inko re-order karein!"
            else:
                ai_reply = "✅ Sab items ka stock behtareen hai! Filhal koi cheez khatam nahi hone wali."

        elif any(k in prompt_lower for k in ["cheese", "fajita", "bun", "stock", "kitna"]):
            matched = False
            for _, r in stock_df.iterrows():
                if any(word in r["Item Name"].lower() for word in prompt_lower.split()):
                    ai_reply += f"📦 **{r['Item Name']}**: {r['Current Stock']} {r['Unit']} bacha hua hai.\n\n"
                    matched = True
            if not matched:
                summary = "\n".join([f"- **{r['Item Name']}**: {r['Current Stock']} {r['Unit']}" for _, r in stock_df.iterrows()])
                ai_reply = f"📊 **Current Balance:**\n{summary}"

        else:
            ai_reply = "Main aapke live stock database se connected hoon. Aap kisi specific item ka balance ya low-stock alerts pooch sakte hain!"

        with st.chat_message("assistant"):
            st.markdown(ai_reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
