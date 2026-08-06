import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import os

st.set_page_config(page_title="Cheesy Delights | Restaurant Manager", layout="wide", page_icon="🍕")

# ==========================================
# 🎨 CUSTOM CSS FOR UI & SCROLLING
# ==========================================
st.markdown("""
    <style>
        .stDataFrame, .stDataEditor {
            overflow-x: auto;
        }
        .stButton>button {
            width: 100%;
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
SALES_FILE = "daily_sales_records.csv"

# ==========================================
# 🔐 PERSISTENT AUTHENTICATION SYSTEM
# ==========================================
if os.path.exists(AUTH_FILE):
    auth_df = pd.read_csv(AUTH_FILE)
    saved_user = str(auth_df.loc[auth_df['Key'] == 'username', 'Value'].values[0]) if 'username' in auth_df['Key'].values else "admin"
    saved_pass = str(auth_df.loc[auth_df['Key'] == 'password', 'Value'].values[0]) if 'password' in auth_df['Key'].values else "1234"
else:
    saved_user, saved_pass = "admin", "1234"

# Maintain login state across refreshes
query_params = st.query_params
if "authenticated" not in st.session_state:
    st.session_state.authenticated = (query_params.get("logged_in") == "true")

if not st.session_state.authenticated:
    st.title("🔒 Cheesy Delights - Login")
    st.write("Please enter your username and password to access the application:")
    
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
                st.error("❌ Incorrect Username or Password! Please try again.")
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

# Load Pricing List
if os.path.exists(PRICES_FILE):
    st.session_state.prices_data = pd.read_csv(PRICES_FILE)
else:
    st.session_state.prices_data = pd.DataFrame([
        {"Item Name": "Zinger Burger", "Purchase Price": 250.0, "Selling Price": 450.0},
        {"Item Name": "French Fries (Large)", "Purchase Price": 80.0, "Selling Price": 180.0}
    ])

# ==========================================
# 🧭 SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("## 🍕 Cheesy Delights")
    nav_option = st.radio(
        "Select Section", 
        [
            "🏠 Home Screen", 
            "📦 Daily Inventory & Sales", 
            "🏷️ Pricing & Sold Items", 
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
# SCREEN 1: 🏠 HOME SCREEN
# ==========================================
if nav_option == "🏠 Home Screen":
    st.title("🍕 Cheesy Delights - Dashboard")
    st.write("Live status of stock and quick overview:")
    
    if os.path.exists(INVENTORY_FILE):
        saved_inv = pd.read_csv(INVENTORY_FILE)
        latest_date = saved_inv["Date"].max() if "Date" in saved_inv.columns else None
        if latest_date:
            st.info(f"📌 Showing latest saved inventory for: **{latest_date}**")
            latest_df = saved_inv[saved_inv["Date"] == latest_date]
            st.dataframe(latest_df, use_container_width=True)
        else:
            st.dataframe(saved_inv, use_container_width=True)
    else:
        st.info("ℹ️ No saved inventory records found yet.")

# ==========================================
# SCREEN 2: 📦 DAILY INVENTORY & SALES ENTRY
# ==========================================
elif nav_option == "📦 Daily Inventory & Sales":
    st.title("📦 Daily Inventory Record")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("Select Entry Date", date.today())
    with col2:
        shift = st.selectbox("Select Shift", ["Evening", "Morning", "Full Day"])

    st.markdown("---")
    
    default_inv = pd.DataFrame([
        {"Item Name": "Zinger Burger", "Unit": "Pieces", "Opening": 50, "Additional": 10, "Sale": 20, "Discount": 2, "Return": 1, "Wastage": 1, "Actual": 5, "Min Stock Limit": 10},
        {"Item Name": "French Fries (Large)", "Unit": "Portion", "Opening": 40, "Additional": 5, "Sale": 25, "Discount": 0, "Return": 0, "Wastage": 2, "Actual": 18, "Min Stock Limit": 15}
    ])
    
    edited_inventory = st.data_editor(default_inv, num_rows="dynamic", key="all_inv_box", use_container_width=True)

    if not edited_inventory.empty:
        df = edited_inventory.copy()
        df["Date"] = str(selected_date)
        df["Shift"] = shift
        df["Total"] = df["Opening"] + df["Additional"]
        df["Balance"] = df["Total"] - (df["Sale"] - df["Discount"]) + df["Return"] - df["Wastage"]
        df["Variance"] = df["Actual"] - df["Balance"]
        
        if st.button("💾 Save Today's Inventory Record"):
            if os.path.exists(INVENTORY_FILE):
                existing_df = pd.read_csv(INVENTORY_FILE)
                existing_df = existing_df[~((existing_df["Date"] == str(selected_date)) & (existing_df["Shift"] == shift))]
                updated_df = pd.concat([existing_df, df], ignore_index=True)
            else:
                updated_df = df
            updated_df.to_csv(INVENTORY_FILE, index=False)
            st.success("✅ Today's inventory record saved successfully!")

        st.markdown("#### 📊 Calculated Entry Summary")
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📦 Low Stock Alert & Demand Box (WhatsApp)")
    
    if not edited_inventory.empty:
        demand_df = edited_inventory[edited_inventory["Actual"] <= edited_inventory["Min Stock Limit"]]
        
        if not demand_df.empty:
            demand_text = f"--- CHEESY DELIGHTS STOCK DEMAND ({selected_date}) ---\n"
            for index, row in demand_df.iterrows():
                required_qty = (row["Min Stock Limit"] - row["Actual"]) + 10
                demand_text += f"• {row['Item Name']} ({row['Unit']}) | Current: {row['Actual']} | Order: {required_qty}\n"
            
            final_demand_text = st.text_area("Review Order Text:", value=demand_text, height=140)
            encoded_text = urllib.parse.quote(final_demand_text)
            
            st.markdown("### 🟢 Send via WhatsApp")
            w_col1, w_col2 = st.columns(2)
            
            clean_p1 = str(st.session_state.brother_1_phone).replace('+', '').replace(' ', '').replace('-', '')
            clean_p2 = str(st.session_state.brother_2_phone).replace('+', '').replace(' ', '').replace('-', '')

            with w_col1:
                if clean_p1:
                    wa_link_1 = f"https://wa.me/{clean_p1}?text={encoded_text}"
                    st.markdown(f'<a href="{wa_link_1}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">💬 Send to {st.session_state.brother_1_name}</button></a>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Add Brother 1 phone number in Settings.")
                    
            with w_col2:
                if clean_p2:
                    wa_link_2 = f"https://wa.me/{clean_p2}?text={encoded_text}"
                    st.markdown(f'<a href="{wa_link_2}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">💬 Send to {st.session_state.brother_2_name}</button></a>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Add Brother 2 phone number in Settings.")
        else:
            st.success("✅ All item stock levels are optimal.")

# ==========================================
# SCREEN 3: 🏷️ PRICING & SOLD ITEMS
# ==========================================
elif nav_option == "🏷️ Pricing & Sold Items":
    st.title("🏷️ Item Pricing & Daily Sold Items Entry")
    
    # Section 1: Pricing Table Management
    st.subheader("📋 Price List Management")
    edited_prices = st.data_editor(st.session_state.prices_data, num_rows="dynamic", key="price_box", use_container_width=True)
    if st.button("💾 Save Pricing List"):
        st.session_state.prices_data = edited_prices
        edited_prices.to_csv(PRICES_FILE, index=False)
        st.success("✅ Price list saved successfully!")

    st.markdown("---")

    # Section 2: Daily Sold Items Entry
    st.subheader("🛒 Daily Sold Items Entry")
    sale_date = st.date_input("Select Sales Date", date.today(), key="sold_date")
    
    # Sync prices table with sold quantity column
    pricing_df = st.session_state.prices_data.copy()
    if "Sold Quantity" not in pricing_df.columns:
        pricing_df["Sold Quantity"] = 0

    edited_sales = st.data_editor(pricing_df, key="sold_items_box", use_container_width=True)
    
    if st.button("💾 Save Daily Sold Items"):
        edited_sales["Date"] = str(sale_date)
        
        if os.path.exists(SALES_FILE):
            existing_sales = pd.read_csv(SALES_FILE)
            existing_sales = existing_sales[existing_sales["Date"] != str(sale_date)]
            updated_sales = pd.concat([existing_sales, edited_sales], ignore_index=True)
        else:
            updated_sales = edited_sales
            
        updated_sales.to_csv(SALES_FILE, index=False)
        st.success(f"✅ Sold items data saved for date {sale_date}!")

    st.markdown("---")

    # Section 3: Daily Expenses
    st.subheader("💸 Daily Expenses Entry")
    exp_date = st.date_input("Expense Date", date.today(), key="exp_date_pricing")
    default_expenses = pd.DataFrame([{"Expense Reason": "Gas / Electricity", "Amount": 1500.0}, {"Expense Reason": "Raw Material Cash", "Amount": 2000.0}])
    edited_expenses = st.data_editor(default_expenses, num_rows="dynamic", key="exp_box", use_container_width=True)

    if st.button("💾 Save Today's Expenses"):
        edited_expenses["Date"] = str(exp_date)
        if os.path.exists(EXPENSES_FILE):
            exp_df = pd.read_csv(EXPENSES_FILE)
            exp_df = exp_df[exp_df["Date"] != str(exp_date)]
            exp_updated = pd.concat([exp_df, edited_expenses], ignore_index=True)
        else:
            exp_updated = edited_expenses
        exp_updated.to_csv(EXPENSES_FILE, index=False)
        st.success(f"✅ Expenses saved for date {exp_date}!")

# ==========================================
# SCREEN 4: 📈 PROFIT & LOSS REPORTS
# ==========================================
elif nav_option == "📈 Profit & Loss Reports":
    st.title("📈 Monthly & Yearly Profit Reports")
    st.write("Complete breakdown based on sales revenue, raw material cost, and daily expenses:")
    
    # Priority check for sales file or inventory file
    sales_file_to_use = SALES_FILE if os.path.exists(SALES_FILE) else (INVENTORY_FILE if os.path.exists(INVENTORY_FILE) else None)
    
    if sales_file_to_use:
        inv_records = pd.read_csv(sales_file_to_use)
        
        # If using inventory file, map 'Sale' column to 'Sold Quantity'
        if "Sold Quantity" not in inv_records.columns and "Sale" in inv_records.columns:
            inv_records["Sold Quantity"] = inv_records["Sale"]
            
        prices_df = st.session_state.prices_data
        
        merged_rep = pd.merge(inv_records, prices_df, on="Item Name", how="left", suffixes=('', '_y')).fillna(0)
        
        # Priority check for prices
        purchase_price_col = "Purchase Price" if "Purchase Price" in merged_rep.columns else "Purchase Price_y"
        selling_price_col = "Selling Price" if "Selling Price" in merged_rep.columns else "Selling Price_y"
        
        merged_rep["Revenue"] = merged_rep["Sold Quantity"] * merged_rep[selling_price_col]
        merged_rep["Cost"] = merged_rep["Sold Quantity"] * merged_rep[purchase_price_col]
        merged_rep["Gross_Profit"] = merged_rep["Revenue"] - merged_rep["Cost"]
        
        merged_rep["Date_Parsed"] = pd.to_datetime(merged_rep["Date"], errors='coerce')
        merged_rep["Year"] = merged_rep["Date_Parsed"].dt.year
        merged_rep["Month"] = merged_rep["Date_Parsed"].dt.strftime("%Y-%m")
        
        expenses_records = pd.read_csv(EXPENSES_FILE) if os.path.exists(EXPENSES_FILE) else pd.DataFrame(columns=["Date", "Amount"])
        if not expenses_records.empty:
            expenses_records["Date_Parsed"] = pd.to_datetime(expenses_records["Date"], errors='coerce')
            expenses_records["Year"] = expenses_records["Date_Parsed"].dt.year
            expenses_records["Month"] = expenses_records["Date_Parsed"].dt.strftime("%Y-%m")
        
        tab1, tab2 = st.tabs(["📅 Monthly Report", "📊 Yearly Report"])
        
        with tab1:
            st.subheader("Monthly Financial Performance")
            valid_months = merged_rep["Month"].dropna().unique()
            if len(valid_months) > 0:
                selected_month = st.selectbox("Select Month", sorted(valid_months, reverse=True))
                month_data = merged_rep[merged_rep["Month"] == selected_month]
                
                m_revenue = month_data["Revenue"].sum()
                m_gross_profit = month_data["Gross_Profit"].sum()
                
                m_expenses = expenses_records[expenses_records["Month"] == selected_month]["Amount"].sum() if not expenses_records.empty else 0.0
                m_net_profit = m_gross_profit - m_expenses
                
                c1, c2, c3 = st.columns(3)
                c1.metric(label="Total Sales Revenue", value=f"Rs. {m_revenue:,.2f}")
                c2.metric(label="Total Expenses", value=f"Rs. {m_expenses:,.2f}")
                c3.metric(label="Net Profit (Clear)", value=f"Rs. {m_net_profit:,.2f}")
                
                st.dataframe(month_data[["Date", "Item Name", "Sold Quantity", "Revenue", "Gross_Profit"]], use_container_width=True)
            else:
                st.info("No valid month data available.")
            
        with tab2:
            st.subheader("Yearly Financial Performance")
            valid_years = merged_rep["Year"].dropna().unique()
            if len(valid_years) > 0:
                selected_year = st.selectbox("Select Year", sorted(valid_years, reverse=True))
                year_data = merged_rep[merged_rep["Year"] == selected_year]
                
                y_revenue = year_data["Revenue"].sum()
                y_gross_profit = year_data["Gross_Profit"].sum()
                
                y_expenses = expenses_records[expenses_records["Year"] == selected_year]["Amount"].sum() if not expenses_records.empty else 0.0
                y_net_profit = y_gross_profit - y_expenses
                
                y1, y2, y3 = st.columns(3)
                y1.metric(label="Total Sales Revenue", value=f"Rs. {y_revenue:,.2f}")
                y2.metric(label="Total Expenses", value=f"Rs. {y_expenses:,.2f}")
                y3.metric(label="Net Profit (Clear)", value=f"Rs. {y_net_profit:,.2f}")
                
                st.dataframe(year_data[["Month", "Item Name", "Sold Quantity", "Revenue", "Gross_Profit"]], use_container_width=True)
            else:
                st.info("No valid year data available.")
    else:
        st.warning("⚠️ No saved sales or inventory records found yet!")

# ==========================================
# SCREEN 5: ⚙️ SETTINGS
# ==========================================
else:
    st.title("⚙️ System Settings")
    
    st.subheader("🔑 Change Login Credentials")
    with st.form("auth_form"):
        new_username = st.text_input("New Username", value=saved_user)
        new_password = st.text_input("New Password", value=saved_pass, type="password")
        
        if st.form_submit_button("Update Credentials"):
            auth_save = pd.DataFrame({
                "Key": ["username", "password"],
                "Value": [new_username, new_password]
            })
            auth_save.to_csv(AUTH_FILE, index=False)
            st.success("✅ Credentials updated successfully!")

    st.markdown("---")
    st.subheader("💬 WhatsApp Contacts Configuration")
    with st.form("settings_form"):
        b1_name_in = st.text_input("Brother 1 Name", value=st.session_state.brother_1_name)
        b1_phone_in = st.text_input("Brother 1 WhatsApp (With country code e.g. 923001234567)", value=st.session_state.brother_1_phone)
        
        st.markdown("---")
        
        b2_name_in = st.text_input("Brother 2 Name", value=st.session_state.brother_2_name)
        b2_phone_in = st.text_input("Brother 2 WhatsApp (With country code e.g. 923001234567)", value=st.session_state.brother_2_phone)
        
        if st.form_submit_button("Save WhatsApp Settings"):
            st.session_state.brother_1_name = b1_name_in
            st.session_state.brother_1_phone = b1_phone_in
            st.session_state.brother_2_name = b2_name_in
            st.session_state.brother_2_phone = b2_phone_in
            
            settings_save = pd.DataFrame({
                "Key": ["b1_name", "b1_phone", "b2_name", "b2_phone"],
                "Value": [b1_name_in, b1_phone_in, b2_name_in, b2_phone_in]
            })
            settings_save.to_csv(SETTINGS_FILE, index=False)
            st.success("✅ WhatsApp details saved!")
