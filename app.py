import streamlit as st
import pandas as pd
from datetime import date, timedelta
import urllib.parse
import os

# Page Config
st.set_page_config(page_title="Cheesy Delights | Pro Manager", layout="wide", page_icon="🍕")

# ==========================================
# 🎨 CUSTOM PROFESSIONAL STYLING
# ==========================================
st.markdown("""
    <style>
        /* Main Theme Adjustments */
        .main {
            background-color: #F8F9FA;
        }
        /* Custom Cards */
        .metric-card {
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border-left: 5px solid #FF4B4B;
        }
        /* AI Assistant Box */
        .ai-box {
            background-color: #1E1E2E;
            color: #E0E0E0;
            padding: 15px;
            border-radius: 10px;
            font-size: 14px;
            border: 1px solid #313244;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📁 FILE STORAGE
# ==========================================
INVENTORY_FILE = "inventory_records.csv"
PURCHASES_FILE = "purchases_records.csv"
SETTINGS_FILE = "settings.csv"
AUTH_FILE = "auth_settings.csv"
PRICES_FILE = "prices_settings.csv"

# ==========================================
# 🔐 AUTHENTICATION
# ==========================================
if os.path.exists(AUTH_FILE):
    auth_df = pd.read_csv(AUTH_FILE)
    saved_user = str(auth_df.loc[auth_df['Key'] == 'username', 'Value'].values[0]) if 'username' in auth_df['Key'].values else "admin"
    saved_pass = str(auth_df.loc[auth_df['Key'] == 'password', 'Value'].values[0]) if 'password' in auth_df['Key'].values else "1234"
else:
    saved_user, saved_pass = "admin", "1234"

if os.path.exists(SETTINGS_FILE):
    sett_df = pd.read_csv(SETTINGS_FILE)
    phone_1 = str(sett_df.loc[sett_df['Key'] == 'phone_1', 'Value'].values[0]) if 'phone_1' in sett_df['Key'].values else "923001234567"
else:
    phone_1 = "923001234567"

query_params = st.query_params
if "authenticated" not in st.session_state:
    st.session_state.authenticated = (query_params.get("logged_in") == "true")

if not st.session_state.authenticated:
    st.title("🔒 Cheesy Delights - Login")
    with st.form("login_form"):
        entered_user = st.text_input("Username")
        entered_pass = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if entered_user == saved_user and entered_pass == saved_pass:
                st.session_state.authenticated = True
                st.query_params["logged_in"] = "true"
                st.rerun()
            else:
                st.error("❌ Incorrect Credentials")
    st.stop()

# Master Prices Setup
if os.path.exists(PRICES_FILE):
    st.session_state.prices_data = pd.read_csv(PRICES_FILE)
    if "Unit" not in st.session_state.prices_data.columns:
        st.session_state.prices_data["Unit"] = "Pieces"
else:
    st.session_state.prices_data = pd.DataFrame([
        {"Item Name": "Zinger Burger", "Unit": "Pieces", "Purchase Price": 250.0, "Selling Price": 400.0},
        {"Item Name": "Fries (Large)", "Unit": "Portion", "Purchase Price": 100.0, "Selling Price": 200.0}
    ])

# ==========================================
# 🤖 AI ASSISTANT FUNCTION
# ==========================================
def generate_ai_insights():
    if not os.path.exists(INVENTORY_FILE):
        return "👋 **AI Assistant**: Abhi tak koi inventory record nahi mila. Record add karein taake main insights share kar sakoon!"
    
    inv_df = pd.read_csv(INVENTORY_FILE)
    if inv_df.empty:
        return "👋 **AI Assistant**: Inventory list khali hai."

    latest_date = inv_df["Date"].max()
    latest_data = inv_df[inv_df["Date"] == latest_date]
    
    sale_col = "Sale / Used" if "Sale / Used" in latest_data.columns else "Sale"
    rem_col = "Remaining Stock (Actual)" if "Remaining Stock (Actual)" in latest_data.columns else "Actual"

    # Insights logic
    top_selling = latest_data.loc[latest_data[sale_col].idxmax()][
        "Item Name"] if not latest_data.empty and latest_data[sale_col].sum() > 0 else "N/A"
    
    low_stock_items = latest_data[latest_data[rem_col] <= 2]["Item Name"].tolist()
    high_wastage = latest_data[latest_data["Wastage"] > 0]["Item Name"].tolist()

    msg = f"📅 **Insights for {latest_date}:**\n\n"
    msg += f"🔥 **Top Seller:** `{top_selling}`\n\n"
    
    if low_stock_items:
        msg += f"⚠️ **Low Stock Alert:** {', '.join([f'`{i}`' for i in low_stock_items])}\n\n"
    else:
        msg += "✅ Stock levels satisfactory hain.\n\n"
        
    if high_wastage:
        msg += f"🗑️ **Wastage Recorded:** {', '.join([f'`{i}`' for i in high_wastage])}"
    else:
        msg += "✨ Superb! Kisi item ki wastage nahi hui."
        
    return msg

# ==========================================
# 🧭 SIDEBAR NAVIGATION & AI ASSISTANT
# ==========================================
with st.sidebar:
    st.markdown("# 🍕 Cheesy Delights")
    st.caption("Pro Restaurant Control Center")
    
    nav_option = st.radio(
        "Navigation", 
        [
            "🏠 Dashboard Overview", 
            "🛍️ Stock Purchases",
            "📦 Daily Inventory Tracker", 
            "🏷️ Master Prices & Items", 
            "📈 Financial P&L Reports",
            "⚙️ Settings"
        ]
    )
    
    st.markdown("---")
    
    # Embedded AI Assistant Box
    st.subheader("🤖 AI Smart Assistant")
    st.markdown(f'<div class="ai-box">{generate_ai_insights()}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.query_params.clear()
        st.rerun()

# ==========================================
# SCREEN 1: 🏠 DASHBOARD OVERVIEW
# ==========================================
if nav_option == "🏠 Dashboard Overview":
    st.title("📊 Executive Dashboard")
    
    if os.path.exists(INVENTORY_FILE):
        saved_inv = pd.read_csv(INVENTORY_FILE)
        if not saved_inv.empty and "Date" in saved_inv.columns:
            latest_date = str(saved_inv["Date"].max())
            latest_df = saved_inv[saved_inv["Date"] == latest_date]
            
            # Top Stats Row
            col1, col2, col3, col4 = st.columns(4)
            sales_col = "Sale / Used" if "Sale / Used" in latest_df.columns else "Sale"
            
            col1.metric("Tracked Items", len(latest_df))
            col2.metric("Total Usage/Sale", f"{latest_df[sales_col].sum():,.1f}")
            col3.metric("Wastage Units", f"{latest_df['Wastage'].sum():,.1f}")
            col4.metric("Active Date", latest_date)
            
            st.markdown("---")
            st.subheader(f"📌 Complete Inventory Snapshot ({latest_date})")
            st.dataframe(latest_df, use_container_width=True, height=400)
            
            st.download_button(
                label="📥 Download Snapshot (CSV)",
                data=latest_df.to_csv(index=False).encode('utf-8'),
                file_name=f"dashboard_summary_{latest_date}.csv",
                mime="text/csv"
            )
        else:
            st.info("ℹ️ Records file is empty.")
    else:
        st.info("ℹ️ No saved records found. Start by filling the inventory!")

# ==========================================
# SCREEN 2: 🛍️ STOCK PURCHASES
# ==========================================
elif nav_option == "🛍️ Stock Purchases":
    st.title("🛍️ Outside Stock Purchases")
    st.caption("Record new inventory bought from market:")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        purchase_date = st.date_input("Purchase Date", date.today())
    with col_p2:
        supplier_notes = st.text_input("Vendor/Notes", placeholder="e.g., Wholesale Market")

    known_items = list(st.session_state.prices_data["Item Name"].unique()) if "Item Name" in st.session_state.prices_data.columns else []

    with st.form("p_form", clear_on_submit=True):
        st.subheader("➕ Quick Add Purchase")
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
            item_sel = st.selectbox("Select Item", known_items + ["+ Add Custom Item"])
            if item_sel == "+ Add Custom Item":
                item_sel = st.text_input("Custom Item Name")
        with c2:
            p_qty = st.number_input("Qty", min_value=0.0, step=0.5)
        with c3:
            p_unit = st.selectbox("Unit", ["Pieces", "KG", "Grams", "Liters", "Portion"])
        with c4:
            p_cost = st.number_input("Total Cost (Rs.)", min_value=0.0, step=50.0)
            
        if st.form_submit_button("💾 Save Purchase Record", type="primary") and item_sel and p_qty > 0:
            new_p = pd.DataFrame([{
                "Date": str(purchase_date),
                "Item Name": item_sel,
                "Quantity": p_qty,
                "Unit": p_unit,
                "Total Purchase Cost": p_cost,
                "Vendor/Notes": supplier_notes
            }])
            
            existing = pd.read_csv(PURCHASES_FILE) if os.path.exists(PURCHASES_FILE) else pd.DataFrame()
            updated = pd.concat([existing, new_p], ignore_index=True)
            updated.to_csv(PURCHASES_FILE, index=False)
            st.success("✅ Purchase Logged Successfully!")
            st.rerun()

    st.markdown("---")
    st.subheader(f"📋 Purchases History ({purchase_date})")
    
    if os.path.exists(PURCHASES_FILE):
        all_p = pd.read_csv(PURCHASES_FILE)
        day_p = all_p[all_p["Date"] == str(purchase_date)]
        
        if not day_p.empty:
            for idx, r in day_p.iterrows():
                rc1, rc2, rc3, rc4, rc5 = st.columns([2, 1, 1, 2, 1])
                rc1.write(f"**{r['Item Name']}**")
                rc2.write(f"{r['Quantity']} {r['Unit']}")
                rc3.write(f"Rs. {r['Total Purchase Cost']:,.2f}")
                rc4.write(f"🏷️ {r['Vendor/Notes'] if pd.notna(r['Vendor/Notes']) else 'N/A'}")
                if rc5.button("🗑️ Delete", key=f"del_{idx}"):
                    all_p = all_p.drop(idx)
                    all_p.to_csv(PURCHASES_FILE, index=False)
                    st.rerun()
        else:
            st.info("No purchases recorded for this date.")

# ==========================================
# SCREEN 3: 📦 DAILY INVENTORY TRACKER
# ==========================================
elif nav_option == "📦 Daily Inventory Tracker":
    st.title("📦 Daily Stock Tracker")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("Select Date", date.today())
    with col2:
        shift = st.selectbox("Select Shift", ["Evening", "Morning", "Full Day"])

    saved_data_found = False
    existing_df = pd.DataFrame()
    
    if os.path.exists(INVENTORY_FILE):
        existing_df = pd.read_csv(INVENTORY_FILE)
        date_shift = existing_df[(existing_df["Date"] == str(selected_date)) & (existing_df["Shift"] == shift)]
        if not date_shift.empty:
            default_inv = date_shift.copy()
            saved_data_found = True

    if not saved_data_found:
        price_df = st.session_state.prices_data
        known_items = price_df[["Item Name", "Unit"]].to_dict('records') if "Unit" in price_df.columns else [{"Item Name": n, "Unit": "Pieces"} for n in price_df["Item Name"]]

        # Auto fetch Purchases for Today
        purchases_map = {}
        if os.path.exists(PURCHASES_FILE):
            p_df = pd.read_csv(PURCHASES_FILE)
            p_today = p_df[p_df["Date"] == str(selected_date)]
            if not p_today.empty:
                purchases_map = p_today.groupby("Item Name")["Quantity"].sum().to_dict()

        # Auto fetch Yesterday's Closing Stock
        yest_date = str(selected_date - timedelta(days=1))
        yest_map = {}
        if not existing_df.empty and "Date" in existing_df.columns:
            yest_df = existing_df[existing_df["Date"] == yest_date]
            if not yest_df.empty:
                for _, r in yest_df.iterrows():
                    yest_map[r["Item Name"]] = float(r.get("Remaining Stock (Actual)", r.get("Actual", 0.0)))

        rows = []
        for item in known_items:
            name = item["Item Name"]
            rows.append({
                "Item Name": name,
                "Unit": item.get("Unit", "Pieces"),
                "Opening Stock": yest_map.get(name, 0.0),
                "New Purchased": purchases_map.get(name, 0.0),
                "Sale / Used": 0.0,
                "Wastage": 0.0,
                "Return": 0.0
            })
        default_inv = pd.DataFrame(rows)

    cols = ["Item Name", "Unit", "Opening Stock", "New Purchased", "Sale / Used", "Wastage", "Return"]
    for c in cols:
        if c not in default_inv.columns:
            default_inv[c] = 0.0

    st.subheader("📝 Edit Inventory Sheet")
    
    cfg = {
        "Unit": st.column_config.SelectboxColumn("Unit", options=["Pieces", "KG", "Grams", "Liters", "Portion"]),
        "Opening Stock": st.column_config.NumberColumn("Opening Stock", format="%.2f"),
        "New Purchased": st.column_config.NumberColumn("New Purchased (Auto)", format="%.2f"),
        "Sale / Used": st.column_config.NumberColumn("Sale / Used", format="%.2f"),
        "Wastage": st.column_config.NumberColumn("Wastage", format="%.2f"),
        "Return": st.column_config.NumberColumn("Return", format="%.2f")
    }

    edited = st.data_editor(default_inv[cols], num_rows="dynamic", column_config=cfg, use_container_width=True, key=f"inv_{selected_date}_{shift}")

    if not edited.empty:
        df = edited.copy()
        df["Total Available Stock"] = df["Opening Stock"] + df["New Purchased"]
        df["Remaining Stock (Actual)"] = df["Total Available Stock"] - (df["Sale / Used"] + df["Wastage"]) + df["Return"]
        df["Date"] = str(selected_date)
        df["Shift"] = shift
        df["Sale"] = df["Sale / Used"]
        df["Actual"] = df["Remaining Stock (Actual)"]

        st.markdown("---")
        b1, b2, b3 = st.columns(3)
        
        with b1:
            if st.button("💾 Save Inventory", type="primary", use_container_width=True):
                full = pd.read_csv(INVENTORY_FILE) if os.path.exists(INVENTORY_FILE) else pd.DataFrame()
                if not full.empty:
                    full = full[~((full["Date"] == str(selected_date)) & (full["Shift"] == shift))]
                res = pd.concat([full, df], ignore_index=True)
                res.to_csv(INVENTORY_FILE, index=False)
                st.success("✅ Stock Record Saved!")
                st.rerun()

        with b2:
            msg = f"*🍕 Cheesy Delights Stock Update ({selected_date})*\n\n"
            for _, r in df.iterrows():
                if r["Sale / Used"] > 0 or r["Remaining Stock (Actual)"] > 0:
                    msg += f"• *{r['Item Name']}*: Sale={r['Sale / Used']} {r['Unit']} | Stock Left={r['Remaining Stock (Actual)']}\n"
            url = f"https://wa.me/{phone_1.replace('+','')}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{url}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 Share WhatsApp Summary</button></a>', unsafe_allow_html=True)

        with b3:
            if saved_data_found and st.button("🗑️ Clear This Sheet", use_container_width=True):
                full = pd.read_csv(INVENTORY_FILE)
                full = full[~((full["Date"] == str(selected_date)) & (full["Shift"] == shift))]
                full.to_csv(INVENTORY_FILE, index=False)
                st.rerun()

# ==========================================
# SCREEN 4: 🏷️ MASTER PRICES & ITEMS
# ==========================================
elif nav_option == "🏷️ Master Prices & Items":
    st.title("🏷️ Items Catalog & Price Setup")
    
    master_df = st.session_state.prices_data.copy()
    edited = st.data_editor(master_df[["Item Name", "Unit", "Purchase Price", "Selling Price"]], num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 Save Price List", type="primary"):
        st.session_state.prices_data = edited
        st.session_state.prices_data.to_csv(PRICES_FILE, index=False)
        st.success("✅ Catalog Updated!")

# ==========================================
# SCREEN 5: 📈 FINANCIAL P&L REPORTS
# ==========================================
elif nav_option == "📈 Financial P&L Reports":
    st.title("📈 Profit & Loss Statement")
    
    if os.path.exists(INVENTORY_FILE):
        inv = pd.read_csv(INVENTORY_FILE)
        prices = st.session_state.prices_data
        
        merged = pd.merge(inv, prices, on="Item Name", how="left").fillna(0)
        
        s_col = "Sale / Used" if "Sale / Used" in merged.columns else "Sale"
        p_price = "Purchase Price_y" if "Purchase Price_y" in merged.columns else "Purchase Price"
        s_price = "Selling Price_y" if "Selling Price_y" in merged.columns else "Selling Price"

        merged["Revenue"] = merged[s_col] * merged[s_price]
        merged["Cost"] = merged[s_col] * merged[p_price]
        merged["Profit"] = merged["Revenue"] - merged["Cost"]

        t1, t2 = st.tabs(["📅 Daily P&L", "🗓️ Monthly Summary"])
        
        with t1:
            avail_dates = sorted(merged["Date"].dropna().unique(), reverse=True)
            if avail_dates:
                sel_d = st.selectbox("Date", avail_dates)
                sub = merged[merged["Date"] == str(sel_d)]
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Revenue", f"Rs. {sub['Revenue'].sum():,.2f}")
                m2.metric("Cost of Sales", f"Rs. {sub['Cost'].sum():,.2f}")
                m3.metric("Gross Profit", f"Rs. {sub['Profit'].sum():,.2f}")
                
                st.dataframe(sub[["Item Name", s_col, "Revenue", "Cost", "Profit"]], use_container_width=True)
        
        with t2:
            merged["Month"] = pd.to_datetime(merged["Date"], errors='coerce').dt.strftime('%Y-%m')
            avail_m = sorted(merged["Month"].dropna().unique(), reverse=True)
            if avail_m:
                sel_m = st.selectbox("Month", avail_m)
                sub_m = merged[merged["Month"] == sel_m]
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Monthly Revenue", f"Rs. {sub_m['Revenue'].sum():,.2f}")
                m2.metric("Monthly Cost", f"Rs. {sub_m['Cost'].sum():,.2f}")
                m3.metric("Monthly Profit", f"Rs. {sub_m['Profit'].sum():,.2f}")
                
                st.dataframe(sub_m[["Date", "Item Name", s_col, "Revenue", "Cost", "Profit"]], use_container_width=True)
    else:
        st.info("No records available to calculate financials.")

# ==========================================
# SCREEN 6: ⚙️ SETTINGS
# ==========================================
else:
    st.title("⚙️ System Preferences")
    
    with st.form("set_form"):
        st.subheader("📱 WhatsApp Config")
        wa_num = st.text_input("WhatsApp Number", value=phone_1)
        if st.form_submit_button("Save Phone Number"):
            pd.DataFrame({"Key": ["phone_1"], "Value": [wa_num]}).to_csv(SETTINGS_FILE, index=False)
            st.success("Updated!")
            st.rerun()

    with st.form("pwd_form"):
        st.subheader("🔒 Update Credentials")
        u = st.text_input("Username", value=saved_user)
        p = st.text_input("Password", value=saved_pass, type="password")
        if st.form_submit_button("Update Password"):
            pd.DataFrame({"Key": ["username", "password"], "Value": [u, p]}).to_csv(AUTH_FILE, index=False)
            st.success("Updated!")
            st.rerun()
