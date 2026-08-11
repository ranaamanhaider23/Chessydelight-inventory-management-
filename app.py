import streamlit as st
import pandas as pd
from datetime import date, timedelta
import urllib.parse
import os

st.set_page_config(page_title="Cheesy Delights | Restaurant Manager", layout="wide", page_icon="🍕")

# ==========================================
# 🎨 CUSTOM CSS
# ==========================================
st.markdown("""
    <style>
        .stDataFrame, .stDataEditor {
            font-size: 16px;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📁 DATA STORAGE FILES (CSV)
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

query_params = st.query_params
if "authenticated" not in st.session_state:
    st.session_state.authenticated = (query_params.get("logged_in") == "true")

if not st.session_state.authenticated:
    st.title("🔒 Cheesy Delights - Login")
    with st.form("login_form"):
        entered_user = st.text_input("Username")
        entered_pass = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if entered_user == saved_user and entered_pass == saved_pass:
                st.session_state.authenticated = True
                st.query_params["logged_in"] = "true"
                st.rerun()
            else:
                st.error("❌ Incorrect Username or Password!")
    st.stop()

# Load prices
if os.path.exists(PRICES_FILE):
    st.session_state.prices_data = pd.read_csv(PRICES_FILE)
    if "Unit" not in st.session_state.prices_data.columns:
        st.session_state.prices_data["Unit"] = "Pieces"
else:
    st.session_state.prices_data = pd.DataFrame([
        {"Item Name": "Zinger Burger", "Unit": "Pieces", "Purchase Price": 0.0, "Selling Price": 0.0},
        {"Item Name": "French Fries (Large)", "Unit": "Portion", "Purchase Price": 0.0, "Selling Price": 0.0}
    ])

# ==========================================
# 🧭 NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("## 🍕 Cheesy Delights")
    nav_option = st.radio(
        "Select Section", 
        [
            "🏠 Dashboard Overview", 
            "🛍️ Baahir Ki Khareedari (Purchases)",
            "📦 Daily Inventory & Stock", 
            "🏷️ Pricing & Items Master", 
            "📈 Profit & Loss Reports",
            "⚙️ Settings"
        ]
    )
    st.markdown("---")
    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.query_params.clear()
        st.rerun()

# ==========================================
# SCREEN 1: 🏠 DASHBOARD OVERVIEW
# ==========================================
if nav_option == "🏠 Dashboard Overview":
    st.title("🍕 Cheesy Delights - Dashboard")
    
    if os.path.exists(INVENTORY_FILE):
        saved_inv = pd.read_csv(INVENTORY_FILE)
        latest_date = saved_inv["Date"].max() if "Date" in saved_inv.columns else None
        if latest_date:
            st.info(f"📌 Showing latest saved inventory for date: **{latest_date}**")
            latest_df = saved_inv[saved_inv["Date"] == latest_date]
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Items Tracked", len(latest_df))
            m2.metric("Total Sales Count", float(latest_df["Sale"].sum()) if "Sale" in latest_df.columns else 0.0)
            m3.metric("Total Wastage Count", float(latest_df["Wastage"].sum()) if "Wastage" in latest_df.columns else 0.0)
            
            st.dataframe(latest_df, use_container_width=True)
        else:
            st.info("ℹ️ Saved record is empty.")
    else:
        st.info("ℹ️ No inventory records saved yet.")

# ==========================================
# SCREEN 2: 🛍️ BAAHIR KI KHAREEDARI (PURCHASES)
# ==========================================
elif nav_option == "🛍️ Baahir Ki Khareedari (Purchases)":
    st.title("🛍️ Market Se Saman Ki Khareedari (Purchases)")
    st.write("Jo saman aap baahir se le kar aaye hain uski entry yahan karein:")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        purchase_date = st.date_input("Purchase Date", date.today())
    with col_p2:
        supplier_notes = st.text_input("Vendor / Shop Name (Optional)", placeholder="e.g. Wholesale Market")

    st.markdown("---")
    
    # Existing Items Dropdown / Custom Item Entry
    known_items_list = list(st.session_state.prices_data["Item Name"].unique()) if "Item Name" in st.session_state.prices_data.columns else []
    
    with st.form("purchase_form", clear_on_submit=True):
        st.subheader("➕ Nayi Khareedari Add Karein")
        p_col1, p_col2, p_col3, p_col4 = st.columns([2, 1, 1, 1])
        
        with p_col1:
            item_selected = st.selectbox("Item Select Karein", known_items_list + ["+ Naya Item Add Karein"])
            if item_selected == "+ Naya Item Add Karein":
                item_selected = st.text_input("Enter New Item Name")
        with p_col2:
            p_qty = st.number_input("Khareedi Gai Qty", min_value=0.0, step=0.1)
        with p_col3:
            p_unit = st.selectbox("Unit", ["Pieces", "KG", "Grams", "Liters", "Portion"])
        with p_col4:
            p_cost = st.number_input("Total Amount (Rs.)", min_value=0.0, step=10.0)
            
        submit_purchase = st.form_submit_button("💾 Save Purchase Record")

        if submit_purchase and item_selected and p_qty > 0:
            new_p_data = pd.DataFrame([{
                "Date": str(purchase_date),
                "Item Name": item_selected,
                "Quantity": p_qty,
                "Unit": p_unit,
                "Total Purchase Cost": p_cost,
                "Vendor/Notes": supplier_notes
            }])
            
            if os.path.exists(PURCHASES_FILE):
                existing_p = pd.read_csv(PURCHASES_FILE)
                updated_p = pd.concat([existing_p, new_p_data], ignore_index=True)
            else:
                updated_p = new_p_data
                
            updated_p.to_csv(PURCHASES_FILE, index=False)
            st.success(f"✅ Saved Purchase: {p_qty} {p_unit} of '{item_selected}' for Rs. {p_cost:,.2f}")
            st.rerun()

    st.markdown("---")
    st.subheader(f"📋 Purchases History for {purchase_date}")
    
    if os.path.exists(PURCHASES_FILE):
        all_p = pd.read_csv(PURCHASES_FILE)
        day_p = all_p[all_p["Date"] == str(purchase_date)]
        
        if not day_p.empty:
            st.dataframe(day_p[["Item Name", "Quantity", "Unit", "Total Purchase Cost", "Vendor/Notes"]], use_container_width=True)
            tot_day_spend = day_p["Total Purchase Cost"].sum()
            st.success(f"💰 **Aaj Ka Total Khareedari Bill:** Rs. {tot_day_spend:,.2f}")
        else:
            st.info("Iss date par abhi koi purchase add nahi hui.")

# ==========================================
# SCREEN 3: 📦 DAILY INVENTORY & STOCK
# ==========================================
elif nav_option == "📦 Daily Inventory & Stock":
    st.title("📦 Easy Daily Inventory & Stock Usage")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("Select Date", date.today())
    with col2:
        shift = st.selectbox("Select Shift", ["Evening", "Morning", "Full Day"])

    st.markdown("---")
    
    saved_data_found = False
    existing_df = pd.DataFrame()
    
    if os.path.exists(INVENTORY_FILE):
        existing_df = pd.read_csv(INVENTORY_FILE)
        date_shift_data = existing_df[(existing_df["Date"] == str(selected_date)) & (existing_df["Shift"] == shift)]
        if not date_shift_data.empty:
            default_inv = date_shift_data.copy()
            saved_data_found = True

    if not saved_data_found:
        # Load items list
        all_known_items = []
        if os.path.exists(INVENTORY_FILE):
            inv_f = pd.read_csv(INVENTORY_FILE)
            if not inv_f.empty and "Item Name" in inv_f.columns:
                all_known_items = inv_f[["Item Name", "Unit"]].drop_duplicates().to_dict('records')
                
        if not all_known_items:
            price_df = st.session_state.prices_data.copy()
            all_known_items = price_df[["Item Name", "Unit"]].to_dict('records') if "Unit" in price_df.columns else [{"Item Name": name, "Unit": "Pieces"} for name in price_df["Item Name"]]

        # Auto fetch Purchases for selected date
        today_purchases = {}
        if os.path.exists(PURCHASES_FILE):
            purch_df = pd.read_csv(PURCHASES_FILE)
            purch_df_today = purch_df[purch_df["Date"] == str(selected_date)]
            if not purch_df_today.empty:
                today_purchases = purch_df_today.groupby("Item Name")["Quantity"].sum().to_dict()

        # Kal ka closing stock
        yesterday_date = str(selected_date - timedelta(days=1))
        yesterday_stock = {}
        if not existing_df.empty and "Date" in existing_df.columns:
            yest_df = existing_df[existing_df["Date"] == yesterday_date]
            if not yest_df.empty:
                for idx, r in yest_df.iterrows():
                    yesterday_stock[r["Item Name"]] = float(r.get("Actual", 0.0))

        rows = []
        for item in all_known_items:
            item_name = item["Item Name"]
            unit_val = item.get("Unit", "Pieces")
            op_val = yesterday_stock.get(item_name, 0.0)
            add_val = today_purchases.get(item_name, 0.0) # Auto fill from Purchases module
            
            rows.append({
                "Item Name": item_name, 
                "Unit": unit_val, 
                "Opening Stock": float(op_val), 
                "New Purchased": float(add_val), 
                "Sale / Used": 0.0, 
                "Wastage": 0.0,
                "Return": 0.0
            })
        default_inv = pd.DataFrame(rows)

    col_order = ["Item Name", "Unit", "Opening Stock", "New Purchased", "Sale / Used", "Wastage", "Return"]
    for col in col_order:
        if col not in default_inv.columns:
            default_inv[col] = 0.0

    st.subheader("📝 Daily Stock & Usage Data Sheet")
    
    column_config = {
        "Unit": st.column_config.SelectboxColumn("Unit", options=["Pieces", "KG", "Grams", "Liters", "Portion"], required=True),
        "Opening Stock": st.column_config.NumberColumn("Opening Stock", step=0.1, format="%.2f"),
        "New Purchased": st.column_config.NumberColumn("New Purchased Stock", step=0.1, format="%.2f"),
        "Sale / Used": st.column_config.NumberColumn("Sale / Used Qty", step=0.1, format="%.2f"),
        "Wastage": st.column_config.NumberColumn("Wastage", step=0.1, format="%.2f"),
        "Return": st.column_config.NumberColumn("Return", step=0.1, format="%.2f"),
    }

    edited_inventory = st.data_editor(
        default_inv[col_order], 
        num_rows="dynamic", 
        column_config=column_config,
        key=f"inv_box_{selected_date}_{shift}", 
        use_container_width=True
    )

    if not edited_inventory.empty:
        df = edited_inventory.copy()
        
        # Explicit calculations for total stock, used stock, and remaining balance
        df["Total Available Stock"] = df["Opening Stock"] + df["New Purchased"]
        df["Total Consumed/Used"] = df["Sale / Used"] + df["Wastage"]
        df["Remaining Stock (Actual)"] = df["Total Available Stock"] - df["Total Consumed/Used"] + df["Return"]
        
        df["Date"] = str(selected_date)
        df["Shift"] = shift
        df["Sale"] = df["Sale / Used"] # Internal map for profit report compatibility
        df["Actual"] = df["Remaining Stock (Actual)"]

        st.markdown("### 📊 Calculated Stock Usage Summary")
        summary_cols = ["Item Name", "Unit", "Opening Stock", "New Purchased", "Total Available Stock", "Sale / Used", "Wastage", "Remaining Stock (Actual)"]
        st.dataframe(df[summary_cols], use_container_width=True)

        col_sv1, col_sv2 = st.columns([2, 1])
        with col_sv1:
            if st.button("💾 Save Inventory Record", type="primary"):
                if os.path.exists(INVENTORY_FILE):
                    full_df = pd.read_csv(INVENTORY_FILE)
                    full_df = full_df[~((full_df["Date"] == str(selected_date)) & (full_df["Shift"] == shift))]
                    updated_df = pd.concat([full_df, df], ignore_index=True)
                else:
                    updated_df = df
                
                updated_df.to_csv(INVENTORY_FILE, index=False)
                st.success("✅ Daily inventory and stock usage saved successfully!")
                st.rerun()

        with col_sv2:
            if saved_data_found:
                if st.button("🗑️ Delete Saved Record", type="secondary"):
                    full_df = pd.read_csv(INVENTORY_FILE)
                    full_df = full_df[~((full_df["Date"] == str(selected_date)) & (full_df["Shift"] == shift))]
                    full_df.to_csv(INVENTORY_FILE, index=False)
                    st.success(f"🗑️ Deleted inventory record for {selected_date}")
                    st.rerun()

# ==========================================
# SCREEN 4: 🏷️ PRICING & ITEMS MASTER
# ==========================================
elif nav_option == "🏷️ Pricing & Items Master":
    st.title("🏷️ Item Pricing & Master Catalog")
    
    master_df = st.session_state.prices_data.copy()
    display_cols = ["Item Name", "Purchase Price", "Selling Price"]
    
    edited_prices = st.data_editor(
        master_df[display_cols],
        num_rows="dynamic",
        key="price_box_custom",
        use_container_width=True
    )

    col_pr1, col_pr2 = st.columns([2, 1])
    with col_pr1:
        if st.button("💾 Save Pricing", type="primary"):
            st.session_state.prices_data = edited_prices
            st.session_state.prices_data.to_csv(PRICES_FILE, index=False)
            st.success("✅ Pricing saved!")

    with col_pr2:
        if st.button("🗑️ Reset All Prices to Zero", type="secondary"):
            st.session_state.prices_data["Purchase Price"] = 0.0
            st.session_state.prices_data["Selling Price"] = 0.0
            st.session_state.prices_data.to_csv(PRICES_FILE, index=False)
            st.success("🗑️ All item prices reset to 0.00!")
            st.rerun()

# ==========================================
# SCREEN 5: 📈 PROFIT & LOSS REPORTS
# ==========================================
elif nav_option == "📈 Profit & Loss Reports":
    st.title("📈 Profit & Loss Financial Reports")
    
    if os.path.exists(INVENTORY_FILE):
        inv_records = pd.read_csv(INVENTORY_FILE)
        prices_df = st.session_state.prices_data
        
        merged_rep = pd.merge(inv_records, prices_df, on="Item Name", how="left", suffixes=('', '_m')).fillna(0)
        
        p_price_col = "Purchase Price" if "Purchase Price" in merged_rep.columns else "Purchase Price_m"
        s_price_col = "Selling Price" if "Selling Price" in merged_rep.columns else "Selling Price_m"
        
        merged_rep["Revenue"] = merged_rep["Sale"] * merged_rep[s_price_col]
        merged_rep["Cost"] = merged_rep["Sale"] * merged_rep[p_price_col]
        merged_rep["Gross Profit"] = merged_rep["Revenue"] - merged_rep["Cost"]
        
        all_available_dates = sorted(merged_rep["Date"].dropna().unique(), reverse=True)
        if len(all_available_dates) > 0:
            selected_daily_date = st.selectbox("Select Date", all_available_dates)
            daily_data = merged_rep[merged_rep["Date"] == str(selected_daily_date)]
            
            d_rev = daily_data["Revenue"].sum()
            d_cost = daily_data["Cost"].sum()
            d_profit = daily_data["Gross Profit"].sum()
            
            d1, d2, d3 = st.columns(3)
            d1.metric("Daily Revenue", f"Rs. {d_rev:,.2f}")
            d2.metric("Daily Cost", f"Rs. {d_cost:,.2f}")
            d3.metric("Daily Gross Profit", f"Rs. {d_profit:,.2f}")
            
            st.dataframe(daily_data[["Date", "Shift", "Item Name", "Unit", "Sale", "Revenue", "Cost", "Gross Profit"]], use_container_width=True)

# ==========================================
# SCREEN 6: ⚙️ SETTINGS
# ==========================================
else:
    st.title("⚙️ System Settings")
    with st.form("auth_form"):
        new_username = st.text_input("New Username", value=saved_user)
        new_password = st.text_input("New Password", value=saved_pass, type="password")
        if st.form_submit_button("Update Password"):
            pd.DataFrame({"Key": ["username", "password"], "Value": [new_username, new_password]}).to_csv(AUTH_FILE, index=False)
            st.success("✅ Password updated!")
