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
EXPENSES_FILE = "expenses_records.csv"
SETTINGS_FILE = "settings.csv"
AUTH_FILE = "auth_settings.csv"
PRICES_FILE = "prices_settings.csv"

# ==========================================
# 🔐 PERSISTENT AUTHENTICATION SYSTEM
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

# ==========================================
# ⚙️ LOAD SETTINGS & PRICES
# ==========================================
if os.path.exists(SETTINGS_FILE):
    settings_df = pd.read_csv(SETTINGS_FILE)
    b1_name_def = settings_df.loc[settings_df['Key'] == 'b1_name', 'Value'].values[0] if 'b1_name' in settings_df['Key'].values else "Brother 1"
    b1_phone_def = settings_df.loc[settings_df['Key'] == 'b1_phone', 'Value'].values[0] if 'b1_phone' in settings_df['Key'].values else ""
    b2_name_def = settings_df.loc[settings_df['Key'] == 'b2_name', 'Value'].values[0] if 'b2_name' in settings_df['Key'].values else "Brother 2"
    b2_phone_def = settings_df.loc[settings_df['Key'] == 'b2_phone', 'Value'].values[0] if 'b2_phone' in settings_df['Key'].values else ""
else:
    b1_name_def, b1_phone_def, b2_name_def, b2_phone_def = "Brother 1", "", "Brother 2", ""

if 'brother_1_name' not in st.session_state: st.session_state.brother_1_name = b1_name_def
if 'brother_1_phone' not in st.session_state: st.session_state.brother_1_phone = str(b1_phone_def)
if 'brother_2_name' not in st.session_state: st.session_state.brother_2_name = b2_name_def
if 'brother_2_phone' not in st.session_state: st.session_state.brother_2_phone = str(b2_phone_def)

if os.path.exists(PRICES_FILE):
    st.session_state.prices_data = pd.read_csv(PRICES_FILE)
    if "Unit" not in st.session_state.prices_data.columns:
        st.session_state.prices_data["Unit"] = "Pieces"
else:
    st.session_state.prices_data = pd.DataFrame([
        {"Item Name": "Zinger Burger", "Unit": "Pieces", "Purchase Price": 0.0, "Selling Price": 0.0},
        {"Item Name": "French Fries (Large)", "Unit": "Portion", "Purchase Price": 0.0, "Selling Price": 0.0},
        {"Item Name": "Mozzarella Cheese", "Unit": "KG", "Purchase Price": 0.0, "Selling Price": 0.0},
        {"Item Name": "Chicken Meat", "Unit": "KG", "Purchase Price": 0.0, "Selling Price": 0.0}
    ])

# ==========================================
# 🧭 SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("## 🍕 Cheesy Delights")
    nav_option = st.radio(
        "Select Section", 
        [
            "🏠 Dashboard Overview", 
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
    st.write("Live Stock Summary & Quick View:")
    
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
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Items Tracked", 0)
            m2.metric("Total Sales Count", "0.00")
            m3.metric("Total Wastage Count", "0.00")
            st.info("ℹ️ Saved record is empty.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Items Tracked", 0)
        m2.metric("Total Sales Count", "0.00")
        m3.metric("Total Wastage Count", "0.00")
        st.info("ℹ️ No inventory records saved yet. Start entering stock from the Daily Inventory tab!")

# ==========================================
# SCREEN 2: 📦 DAILY INVENTORY & STOCK
# ==========================================
elif nav_option == "📦 Daily Inventory & Stock":
    st.title("📦 Easy Daily Inventory Record")
    
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
        price_df = st.session_state.prices_data.copy()
        
        yesterday_date = str(selected_date - timedelta(days=1))
        yesterday_stock = {}
        if not existing_df.empty and "Date" in existing_df.columns:
            yest_df = existing_df[existing_df["Date"] == yesterday_date]
            if not yest_df.empty:
                for idx, r in yest_df.iterrows():
                    yesterday_stock[r["Item Name"]] = float(r.get("Actual", 0.0))

        rows = []
        for idx, row in price_df.iterrows():
            item_name = row["Item Name"]
            unit_val = row.get("Unit", "Pieces")
            op_val = yesterday_stock.get(item_name, 0.0)
            
            rows.append({
                "Item Name": item_name, 
                "Unit": unit_val, 
                "Opening": float(op_val), 
                "Additional": 0.0, 
                "Sale": 0.0, 
                "Discount": 0.0, 
                "Return": 0.0, 
                "Wastage": 0.0,
                "Min Stock Limit": 0.0
            })
        default_inv = pd.DataFrame(rows)

    col_order = ["Item Name", "Unit", "Opening", "Additional", "Sale", "Discount", "Return", "Wastage", "Min Stock Limit"]
    for col in col_order:
        if col not in default_inv.columns:
            default_inv[col] = 0.0

    st.subheader("📝 Edit Inventory Sheet")
    
    column_config = {
        "Unit": st.column_config.SelectboxColumn("Unit", options=["Pieces", "KG", "Grams", "Liters", "Portion"], required=True),
        "Opening": st.column_config.NumberColumn("Opening", step=0.1, format="%.2f"),
        "Additional": st.column_config.NumberColumn("Additional", step=0.1, format="%.2f"),
        "Sale": st.column_config.NumberColumn("Sale", step=0.1, format="%.2f"),
        "Discount": st.column_config.NumberColumn("Discount", step=0.1, format="%.2f"),
        "Return": st.column_config.NumberColumn("Return", step=0.1, format="%.2f"),
        "Wastage": st.column_config.NumberColumn("Wastage", step=0.1, format="%.2f"),
        "Min Stock Limit": st.column_config.NumberColumn("Min Stock Limit", step=0.1, format="%.2f"),
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
        
        df["Total Stock"] = df["Opening"] + df["Additional"]
        df["Net Sold"] = df["Sale"] - df["Discount"]
        df["Actual"] = df["Total Stock"] - df["Net Sold"] + df["Return"] - df["Wastage"]
        
        df["Date"] = str(selected_date)
        df["Shift"] = shift

        st.markdown("### 📊 Auto-Calculated Final Summary")
        summary_cols = ["Item Name", "Unit", "Opening", "Additional", "Sale", "Return", "Wastage", "Actual", "Min Stock Limit"]
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
                st.success("✅ Today's inventory saved successfully!")
                st.rerun()

        with col_sv2:
            if saved_data_found:
                if st.button("🗑️ Delete Today's Saved Record", type="secondary"):
                    full_df = pd.read_csv(INVENTORY_FILE)
                    full_df = full_df[~((full_df["Date"] == str(selected_date)) & (full_df["Shift"] == shift))]
                    full_df.to_csv(INVENTORY_FILE, index=False)
                    st.success(f"🗑️ Deleted inventory record for {selected_date} ({shift})")
                    st.rerun()

# ==========================================
# SCREEN 3: 🏷️ PRICING & ITEMS MASTER
# ==========================================
elif nav_option == "🏷️ Pricing & Items Master":
    st.title("🏷️ Item Pricing & Master Catalog")
    st.write("Manage menu items, set prices, and view stock/sales totals:")

    price_column_config = {
        "Item Name": st.column_config.TextColumn("Item Name", required=True),
        "Purchase Price": st.column_config.NumberColumn("Purchase Price (Rs.)", format="Rs. %.2f", min_value=0.0),
        "Selling Price": st.column_config.NumberColumn("Selling Price (Rs.)", format="Rs. %.2f", min_value=0.0),
    }

    sold_dict = {}
    total_stock_dict = {}
    if os.path.exists(INVENTORY_FILE):
        inv_df = pd.read_csv(INVENTORY_FILE)
        if not inv_df.empty and "Item Name" in inv_df.columns:
            if "Sale" in inv_df.columns:
                sold_dict = inv_df.groupby("Item Name")["Sale"].sum().to_dict()
            if "Total Stock" in inv_df.columns:
                total_stock_dict = inv_df.groupby("Item Name")["Total Stock"].sum().to_dict()

    master_df = st.session_state.prices_data.copy()
    master_df["Sold Item"] = master_df["Item Name"].map(sold_dict).fillna(0.0)
    master_df["Total Item"] = master_df["Item Name"].map(total_stock_dict).fillna(0.0)

    display_cols = ["Item Name", "Sold Item", "Total Item", "Purchase Price", "Selling Price"]
    
    for c in display_cols:
        if c not in master_df.columns:
            master_df[c] = 0.0

    edited_prices = st.data_editor(
        master_df[display_cols],
        column_config={
            **price_column_config,
            "Sold Item": st.column_config.NumberColumn("Sold Item", disabled=True, format="%.2f"),
            "Total Item": st.column_config.NumberColumn("Total Item", disabled=True, format="%.2f")
        },
        num_rows="dynamic",
        key="price_box_custom",
        use_container_width=True
    )

    if not edited_prices.empty:
        tot_sold = edited_prices["Sold Item"].sum()
        tot_items = edited_prices["Total Item"].sum()
        tot_purchase = edited_prices["Purchase Price"].sum()
        tot_selling = edited_prices["Selling Price"].sum()

        st.markdown("---")
        st.subheader("📊 Totals Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Sold Items", f"{tot_sold:,.2f}")
        m2.metric("Total Stock Items", f"{tot_items:,.2f}")
        m3.metric("Total Purchase Rate", f"Rs. {tot_purchase:,.2f}")
        m4.metric("Total Selling Rate", f"Rs. {tot_selling:,.2f}")

    # Save and Reset Prices to Zero Buttons (Side-by-Side)
    col_pr1, col_pr2 = st.columns([2, 1])
    
    with col_pr1:
        if st.button("💾 Save Item Pricing", type="primary"):
            st.session_state.prices_data = edited_prices[["Item Name", "Purchase Price", "Selling Price"]].dropna(subset=["Item Name"])
            st.session_state.prices_data.to_csv(PRICES_FILE, index=False)
            st.success("✅ Pricing saved successfully!")

    with col_pr2:
        if st.button("🗑️ Reset All Prices to Zero", type="secondary"):
            if not st.session_state.prices_data.empty:
                st.session_state.prices_data["Purchase Price"] = 0.0
                st.session_state.prices_data["Selling Price"] = 0.0
                st.session_state.prices_data.to_csv(PRICES_FILE, index=False)
                st.success("🗑️ All item prices set to 0.00!")
                st.rerun()

# ==========================================
# SCREEN 4: 📈 PROFIT & LOSS REPORTS
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
        
        merged_rep["Date_Parsed"] = pd.to_datetime(merged_rep["Date"], errors='coerce')
        merged_rep["Year"] = merged_rep["Date_Parsed"].dt.year
        merged_rep["Month"] = merged_rep["Date_Parsed"].dt.strftime("%Y-%m")
        
        tab_daily, tab_m, tab_y, tab_d = st.tabs(["📅 Daily Report", "📆 Monthly Report", "📊 Yearly Report", "🗑️ Manage Records"])
        
        # 1. DAILY PROFIT & LOSS REPORT
        with tab_daily:
            st.subheader("Daily Profit & Loss Summary")
            all_available_dates = sorted(merged_rep["Date"].dropna().unique(), reverse=True)
            
            if len(all_available_dates) > 0:
                selected_daily_date = st.selectbox("Select Date for Daily Report", all_available_dates, key="daily_rep_date")
                daily_data = merged_rep[merged_rep["Date"] == str(selected_daily_date)]
                
                d_rev = daily_data["Revenue"].sum()
                d_cost = daily_data["Cost"].sum()
                d_profit = daily_data["Gross Profit"].sum()
                
                d1, d2, d3 = st.columns(3)
                d1.metric("Daily Revenue", f"Rs. {d_rev:,.2f}")
                d2.metric("Daily Cost", f"Rs. {d_cost:,.2f}")
                d3.metric("Daily Gross Profit / Loss", f"Rs. {d_profit:,.2f}", delta=f"{d_profit:,.2f}")
                
                st.dataframe(daily_data[["Date", "Shift", "Item Name", "Unit", "Sale", "Revenue", "Cost", "Gross Profit"]], use_container_width=True)
                
                d_csv = daily_data.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Save/Download Daily Report (CSV)", data=d_csv, file_name=f"Daily_Report_{selected_daily_date}.csv", mime="text/csv")
            else:
                st.info("No daily records found.")

        # 2. MONTHLY REPORT & EXPORT
        with tab_m:
            st.subheader("Monthly Profit & Loss Summary")
            valid_months = merged_rep["Month"].dropna().unique()
            if len(valid_months) > 0:
                selected_month = st.selectbox("Select Month", sorted(valid_months, reverse=True))
                month_data = merged_rep[merged_rep["Month"] == selected_month]
                
                m_rev = month_data["Revenue"].sum()
                m_cost = month_data["Cost"].sum()
                m_profit = month_data["Gross Profit"].sum()
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Monthly Revenue", f"Rs. {m_rev:,.2f}")
                c2.metric("Total Monthly Cost", f"Rs. {m_cost:,.2f}")
                c3.metric("Monthly Gross Profit", f"Rs. {m_profit:,.2f}")
                
                st.dataframe(month_data[["Date", "Shift", "Item Name", "Unit", "Sale", "Revenue", "Gross Profit"]], use_container_width=True)
                
                m_csv = month_data.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Save/Download Monthly Report (CSV)", data=m_csv, file_name=f"Monthly_Report_{selected_month}.csv", mime="text/csv")
            else:
                st.info("No monthly records found.")
                
        # 3. YEARLY REPORT & EXPORT
        with tab_y:
            st.subheader("Yearly Profit & Loss Summary")
            valid_years = merged_rep["Year"].dropna().unique()
            if len(valid_years) > 0:
                selected_year = st.selectbox("Select Year", sorted(valid_years, reverse=True))
                year_data = merged_rep[merged_rep["Year"] == selected_year]
                
                y_rev = year_data["Revenue"].sum()
                y_cost = year_data["Cost"].sum()
                y_profit = year_data["Gross Profit"].sum()
                
                y1, y2, y3 = st.columns(3)
                y1.metric("Total Yearly Revenue", f"Rs. {y_rev:,.2f}")
                y2.metric("Total Yearly Cost", f"Rs. {y_cost:,.2f}")
                y3.metric("Yearly Gross Profit", f"Rs. {y_profit:,.2f}")
                
                st.dataframe(year_data[["Month", "Date", "Item Name", "Unit", "Sale", "Revenue", "Gross Profit"]], use_container_width=True)
                
                y_csv = year_data.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Save/Download Yearly Report (CSV)", data=y_csv, file_name=f"Yearly_Report_{selected_year}.csv", mime="text/csv")
            else:
                st.info("No yearly records found.")
                
        # 4. DELETE RECORDS
        with tab_d:
            st.subheader("🗑️ Delete Specific Daily Inventory Entry")
            all_dates = sorted(inv_records["Date"].dropna().unique(), reverse=True)
            if len(all_dates) > 0:
                del_date = st.selectbox("Select Date to Delete Record", all_dates)
                if st.button(f"🚨 Confirm Delete Record for {del_date}", type="primary"):
                    inv_records = inv_records[inv_records["Date"] != str(del_date)]
                    inv_records.to_csv(INVENTORY_FILE, index=False)
                    st.success(f"✅ Record for date {del_date} deleted successfully!")
                    st.rerun()
            else:
                st.info("No records available to delete.")
    else:
        st.info("ℹ️ Save daily inventory records first to view profit/loss analytics.")

# ==========================================
# SCREEN 5: ⚙️ SETTINGS
# ==========================================
else:
    st.title("⚙️ System Settings")
    
    st.subheader("🔑 Change Login Password")
    with st.form("auth_form"):
        new_username = st.text_input("New Username", value=saved_user)
        new_password = st.text_input("New Password", value=saved_pass, type="password")
        
        if st.form_submit_button("Update Password"):
            auth_save = pd.DataFrame({"Key": ["username", "password"], "Value": [new_username, new_password]})
            auth_save.to_csv(AUTH_FILE, index=False)
            st.success("✅ Password updated successfully!")

    st.markdown("---")
    st.subheader("💬 WhatsApp Contacts Configuration")
    with st.form("settings_form"):
        b1_name_in = st.text_input("Brother 1 Name", value=st.session_state.brother_1_name)
        b1_phone_in = st.text_input("Brother 1 Phone (e.g. 923001234567)", value=st.session_state.brother_1_phone)
        
        b2_name_in = st.text_input("Brother 2 Name", value=st.session_state.brother_2_name)
        b2_phone_in = st.text_input("Brother 2 Phone (e.g. 923001234567)", value=st.session_state.brother_2_phone)
        
        if st.form_submit_button("Save WhatsApp Settings"):
            st.session_state.brother_1_name = b1_name_in
            st.session_state.brother_1_phone = b1_phone_in
            st.session_state.brother_2_name = b2_name_in
            st.session_state.brother_2_phone = b2_phone_in
            
            settings_save = pd.DataFrame({"Key": ["b1_name", "b1_phone", "b2_name", "b2_phone"], "Value": [b1_name_in, b1_phone_in, b2_name_in, b2_phone_in]})
            settings_save.to_csv(SETTINGS_FILE, index=False)
            st.success("✅ Contacts Saved!")
