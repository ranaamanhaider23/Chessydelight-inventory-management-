import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

# ==========================================
# 🎨 ULTRA-PRO RESTAURANT UI / THEME
# ==========================================
st.set_page_config(page_title="Cheesy Delights | Pro Restaurant OS", layout="wide", page_icon="🍕")

st.markdown("""
    <style>
        .stApp { background-color: #0B0F19; color: #E2E8F0; }
        
        div[data-testid="stMetric"] {
            background: #1E293B;
            border: 1px solid #334155;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }
        div[data-testid="stMetric"] label { color: #94A3B8 !important; font-size: 13px !important; font-weight: 600; }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #38BDF8 !important; font-size: 22px !important; font-weight: 700; }

        .status-card-danger {
            background-color: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #EF4444;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 8px;
        }

        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            color: white;
            border: none;
            padding: 8px 16px;
        }
        
        section[data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1E293B; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📁 FILE SYSTEM SETUP
# ==========================================
INVENTORY_FILE = "rest_inventory.csv"
PURCHASES_FILE = "rest_purchases.csv"
ITEMS_MASTER_FILE = "rest_items_master.csv"

if not os.path.exists(ITEMS_MASTER_FILE):
    default_items = pd.DataFrame([
        {"Item Name": "Chicken Patty", "Category": "Raw Material", "Unit": "Pieces", "Min Stock Alert": 20, "Cost Price": 120.0},
        {"Item Name": "Burger Buns", "Category": "Raw Material", "Unit": "Pieces", "Min Stock Alert": 30, "Cost Price": 30.0},
        {"Item Name": "Cheddar Cheese Slice", "Category": "Raw Material", "Unit": "Pieces", "Min Stock Alert": 50, "Cost Price": 25.0},
        {"Item Name": "French Fries (Frozen)", "Category": "Raw Material", "Unit": "KG", "Min Stock Alert": 5, "Cost Price": 400.0},
        {"Item Name": "Cooking Oil", "Category": "Raw Material", "Unit": "Liters", "Min Stock Alert": 10, "Cost Price": 550.0},
        {"Item Name": "Burger Packing Box", "Category": "Packaging", "Unit": "Pieces", "Min Stock Alert": 50, "Cost Price": 15.0},
        {"Item Name": "Cold Drink 345ml", "Category": "Beverages", "Unit": "Pieces", "Min Stock Alert": 24, "Cost Price": 60.0}
    ])
    default_items.to_csv(ITEMS_MASTER_FILE, index=False)

master_items_df = pd.read_csv(ITEMS_MASTER_FILE)

# ==========================================
# 🧭 SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color: #F59E0B; text-align: center;'>🍕 Cheesy Delights</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; text-align: center; font-size:12px;'>COMMERCIAL RESTAURANT ENGINE</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    nav = st.radio(
        "MODULES",
        [
            "💬 Chat with AI Manager",
            "📊 Executive Operations Center",
            "📦 Daily Stock & Usage Log",
            "🛍️ Vendor Purchasing Log",
            "🏷️ Master Inventory Items"
        ]
    )

# ==========================================
# MODULE 1: 💬 LIVE CHAT WITH AI MANAGER
# ==========================================
if nav == "💬 Chat with AI Manager":
    st.markdown("<h2 style='color: #38BDF8;'>🤖 AI Restaurant Operations Copilot</h2>", unsafe_allow_html=True)
    st.caption("Aap apne live inventory database se koi bhi sawal Urdu ya English mein pooch sakte hain:")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Salam! Main aapka Cheesy Delights AI Assistant hoon. Stock, Sales, ya Wastage se mutaliq koi bhi sawal poochein!"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_prompt := st.chat_input("Poochein (e.g., 'Kaunsi item khatam hone wali hai?' ya 'Wastage ka batao'):"):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        ai_reply = ""
        prompt_lower = user_prompt.lower()

        if os.path.exists(INVENTORY_FILE):
            inv_data = pd.read_csv(INVENTORY_FILE)
            if not inv_data.empty:
                latest_d = inv_data["Date"].max()
                latest_inv = inv_data[inv_data["Date"] == latest_d]
                merged = pd.merge(latest_inv, master_items_df, on="Item Name", how="left")

                if any(k in prompt_lower for k in ["khatam", "low", "stock", "restock", "order"]):
                    lows = merged[merged["Remaining Stock"] <= merged["Min Stock Alert"]]
                    if not lows.empty:
                        items_str = ", ".join([f"**{r['Item Name']}** ({r['Remaining Stock']} {r['Unit_x']} left)" for _, r in lows.iterrows()])
                        ai_reply = f"🚨 **Low Stock Alert ({latest_d}):** Yeh items minimum level se neeche hain: {items_str}. Inka market order lagayein!"
                    else:
                        ai_reply = f"✅ Sab items ka stock filhal sahi hai! Kisi item ka level critical nahi hai."

                elif any(k in prompt_lower for k in ["zaya", "wastage", "waste", "kharab"]):
                    wasted = latest_inv[latest_inv["Wastage"] > 0]
                    if not wasted.empty:
                        w_str = ", ".join([f"**{r['Item Name']}**: {r['Wastage']} {r['Unit']}" for _, r in wasted.iterrows()])
                        ai_reply = f"🗑️ **Wastage Summary ({latest_d}):** Aaj yeh items zaya hui hain: {w_str}."
                    else:
                        ai_reply = f"✨ Bohot zabardast! {latest_d} ko koi wastage record nahi hui."

                elif any(k in prompt_lower for k in ["sale", "used", "bik", "bika"]):
                    top_item = latest_inv.loc[latest_inv["Used/Sold"].idxmax()]
                    ai_reply = f"🔥 **Top Used Item ({latest_d}):** Aaj sab se ziada **{top_item['Item Name']}** use/sell hui hai ({top_item['Used/Sold']} {top_item['Unit']})."

                else:
                    ai_reply = f"📊 Main aapke **{latest_d}** ke data se connected hoon. Total **{len(latest_inv)} items** track ho rahi hain. Aap specific item ka naam, low stock, ya wastage ka pooch sakte hain!"
            else:
                ai_reply = "System mein abhi koi stock data save nahi hai. Pehle 'Daily Stock & Usage Log' mein entry karein."
        else:
            ai_reply = "Pehle daily stock log add karein taake main aapko sahi figures bata sakoon."

        with st.chat_message("assistant"):
            st.markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# ==========================================
# MODULE 2: 📊 EXECUTIVE OPERATIONS CENTER
# ==========================================
elif nav == "📊 Executive Operations Center":
    st.markdown("<h2 style='color: #38BDF8;'>📊 Real-time Restaurant Stock Dashboard</h2>", unsafe_allow_html=True)
    
    if os.path.exists(INVENTORY_FILE):
        inv_df = pd.read_csv(INVENTORY_FILE)
        if not inv_df.empty:
            latest_date = inv_df["Date"].max()
            curr = inv_df[inv_df["Date"] == latest_date]
            merged = pd.merge(curr, master_items_df, on="Item Name", how="left")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tracked Items", len(curr))
            m2.metric("Total Used Today", f"{curr['Used/Sold'].sum():,.1f}")
            low_stock_count = len(merged[merged["Remaining Stock"] <= merged["Min Stock Alert"]])
            m3.metric("Critical Restock Items", f"{low_stock_count} Items")
            m4.metric("Active Date", latest_date)

            st.markdown("---")
            
            # Built-in Streamlit Bar Chart (No Plotly required)
            st.subheader("📦 Stock Level Overview")
            chart_data = curr.set_index("Item Name")[["Used/Sold", "Remaining Stock"]]
            st.bar_chart(chart_data)

            st.markdown("---")
            st.dataframe(curr, use_container_width=True)
        else:
            st.info("No active stock entries recorded yet.")
    else:
        st.info("Please complete daily stock entry to display analytics.")

# ==========================================
# MODULE 3: 📦 DAILY STOCK & USAGE LOG
# ==========================================
elif nav == "📦 Daily Stock & Usage Log":
    st.markdown("<h2 style='color: #38BDF8;'>📦 Daily Restaurant Inventory Tracking</h2>", unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        entry_date = st.date_input("Entry Date", date.today())
    with col_d2:
        shift = st.selectbox("Shift", ["Evening Shift", "Morning Shift", "Full Operational Day"])

    master = pd.read_csv(ITEMS_MASTER_FILE)
    saved_data = False
    
    if os.path.exists(INVENTORY_FILE):
        all_inv = pd.read_csv(INVENTORY_FILE)
        match = all_inv[(all_inv["Date"] == str(entry_date)) & (all_inv["Shift"] == shift)]
        if not match.empty:
            df_editor = match.copy()
            saved_data = True

    if not saved_data:
        rows = []
        for _, r in master.iterrows():
            rows.append({
                "Item Name": r["Item Name"],
                "Category": r["Category"],
                "Unit": r["Unit"],
                "Opening Stock": 0.0,
                "New Purchased": 0.0,
                "Used/Sold": 0.0,
                "Wastage": 0.0
            })
        df_editor = pd.DataFrame(rows)

    cols = ["Item Name", "Category", "Unit", "Opening Stock", "New Purchased", "Used/Sold", "Wastage"]
    edited = st.data_editor(df_editor[cols], num_rows="dynamic", use_container_width=True, key=f"editor_{entry_date}_{shift}")

    if not edited.empty:
        df_final = edited.copy()
        df_final["Remaining Stock"] = (df_final["Opening Stock"] + df_final["New Purchased"]) - (df_final["Used/Sold"] + df_final["Wastage"])
        df_final["Date"] = str(entry_date)
        df_final["Shift"] = shift

        if st.button("💾 Save Daily Log", type="primary", use_container_width=True):
            existing = pd.read_csv(INVENTORY_FILE) if os.path.exists(INVENTORY_FILE) else pd.DataFrame()
            if not existing.empty:
                existing = existing[~((existing["Date"] == str(entry_date)) & (existing["Shift"] == shift))]
            res = pd.concat([existing, df_final], ignore_index=True)
            res.to_csv(INVENTORY_FILE, index=False)
            st.success("✅ Stock Record Saved!")
            st.rerun()

# ==========================================
# MODULE 4: 🛍️ VENDOR PURCHASING LOG
# ==========================================
elif nav == "🛍️ Vendor Purchasing Log":
    st.markdown("<h2 style='color: #38BDF8;'>🛍️ Market & Vendor Purchases Log</h2>", unsafe_allow_html=True)
    
    with st.form("purchase_form", clear_on_submit=True):
        st.subheader("➕ Log Vendor Bill / Purchase")
        p_date = st.date_input("Purchase Date", date.today())
        p_item = st.selectbox("Select Item", master_items_df["Item Name"].tolist())
        p_qty = st.number_input("Quantity Received", min_value=0.0, step=1.0)
        p_cost = st.number_input("Total Bill Amount (Rs.)", min_value=0.0, step=50.0)
        p_vendor = st.text_input("Vendor Name / Bill No.")
        
        if st.form_submit_button("💾 Save Vendor Invoice"):
            new_p = pd.DataFrame([{
                "Date": str(p_date),
                "Item Name": p_item,
                "Quantity": p_qty,
                "Total Cost": p_cost,
                "Vendor/Bill": p_vendor
            }])
            existing = pd.read_csv(PURCHASES_FILE) if os.path.exists(PURCHASES_FILE) else pd.DataFrame()
            updated = pd.concat([existing, new_p], ignore_index=True)
            updated.to_csv(PURCHASES_FILE, index=False)
            st.success("✅ Purchase Logged!")

# ==========================================
# MODULE 5: 🏷️ MASTER INVENTORY ITEMS
# ==========================================
else:
    st.markdown("<h2 style='color: #38BDF8;'>🏷️ Master Restaurant Items Catalog</h2>", unsafe_allow_html=True)
    
    master_edited = st.data_editor(master_items_df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Update Master Catalog", type="primary"):
        master_edited.to_csv(ITEMS_MASTER_FILE, index=False)
        st.success("✅ Master Catalog Updated!")
