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
# 🔐 AUTHENTICATION & SETTINGS LOAD
# ==========================================
if os.path.exists(AUTH_FILE):
    auth_df = pd.read_csv(AUTH_FILE)
    saved_user = str(auth_df.loc[auth_df['Key'] == 'username', 'Value'].values[0]) if 'username' in auth_df['Key'].values else "admin"
    saved_pass = str(auth_df.loc[auth_df['Key'] == 'password', 'Value'].values[0]) if 'password' in auth_df['Key'].values else "1234"
else:
    saved_user, saved_pass = "admin", "1234"

# Load WhatsApp Settings
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
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if entered_user == saved_user and entered_pass == saved_pass:
                st.session_state.authenticated = True
                st.query_params["logged_in"] = "true"
                st.rerun()
            else:
                st.error("❌ Incorrect Username or Password!")
    st.stop()

# Load prices catalog
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
            "🛍️ Stock Purchases",
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
        if not saved_inv.empty and "Date" in saved_inv.columns:
            latest_date = str(saved_inv["Date"].max())
            st.info(f"📌 Showing latest saved inventory snapshot for date: **{latest_date}**")
            
            latest_df = saved_inv[saved_inv["Date"] == latest_date]
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Items Tracked", len(latest_df))
            
            sales_col = "Sale / Used" if "Sale / Used" in latest_df.columns else "Sale"
            m2.metric("Total Sales Count", float(latest_df[sales_col].sum()) if sales_col in latest_df.columns else 0.0)
            m3.metric("Total Wastage Count", float(latest_df["Wastage"].sum()) if "Wastage" in latest_df.columns else 0.0)
            
            st.dataframe(latest_df, use_container_width=True)
            
            csv_data = latest_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Dashboard Report (CSV)",
                data=csv_data,
                file_name=f"dashboard_inventory_{latest_date}.csv",
                mime="text/csv"
            )
        else:
            st.info("ℹ️ Saved record is empty.")
    else:
        st.info("ℹ️ No inventory records saved yet.")

# ==========================================
# SCREEN 2: 🛍️ STOCK PURCHASES (WITH DELETE OPTION)
# ==========================================
elif nav_option == "🛍️ Stock Purchases":
    st.title("🛍️ Outside Market Purchases Log")
    st.write("Record all items and inventory bought from outside markets:")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        purchase_date = st.date_input("Purchase Date", date.today())
    with col_p2:
        supplier_notes = st.text_input("Vendor / Shop Name (Optional)", placeholder="e.g. Wholesale Market")

    st.markdown("---")
    
    known_items_list = list(st.session_state.prices_data["Item Name"].unique()) if "Item Name" in st.session_state.prices_data.columns else []
    if os.path.exists(INVENTORY_FILE):
        inv_f = pd.read_csv(INVENTORY_FILE)
        if "Item Name" in inv_f.columns:
            known_items_list = list(set(known_items_list + list(inv_f["Item Name"].unique())))

    with st.form("purchase_form", clear_on_submit=True):
        st.subheader("➕ Add New Purchase Entry")
        p_col1, p_col2, p_col3, p_col4 = st.columns([2, 1, 1, 1])
        
        with p_col1:
            item_selected = st.selectbox("Select Item", known_items_list + ["+ Add New Custom Item"])
            if item_selected == "+ Add New Custom Item":
                item_selected = st.text_input("Enter New Item Name")
        with p_col2:
            p_qty = st.number_input("Purchased Quantity", min_value=0.0, step=0.1)
        with p_col3:
            p_unit = st.selectbox("Unit", ["Pieces", "KG", "Grams", "Liters", "Portion"])
        with p_col4:
            p_cost = st.number_input("Total Amount Spent (Rs.)", min_value=0.0, step=10.0)
            
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
        
        if not all_p.empty:
            # Filter rows for selected date
            day_p_indices = all_p[all_p["Date"] == str(purchase_date)].index
            
            if len(day_p_indices) > 0:
                # Display each purchase record with an individual Delete Button
                for idx in day_p_indices:
                    row = all_p.loc[idx]
                    col_d1, col_d2, col_d3, col_d4, col_d5, col_d6 = st.columns([2, 1, 1, 1.5, 2, 1])
                    
                    col_d1.write(f"**{row['Item Name']}**")
                    col_d2.write(f"{row['Quantity']} {row['Unit']}")
                    col_d3.write(f"Rs. {row['Total Purchase Cost']:,.2f}")
                    col_d4.write(f"🏷️ {row['Vendor/Notes'] if pd.notna(row['Vendor/Notes']) else 'N/A'}")
                    col_d5.write(f"📅 {row['Date']}")
                    
                    # Delete Button per row
                    if col_d6.button("🗑️ Delete", key=f"del_purch_{idx}"):
                        all_p = all_p.drop(idx)
                        all_p.to_csv(PURCHASES_FILE, index=False)
                        st.success(f"🗑️ Deleted purchase entry for '{row['Item Name']}'!")
                        st.rerun()
                
                tot_day_spend = all_p.loc[day_p_indices, "Total Purchase Cost"].sum()
                st.markdown("---")
                st.success(f"💰 **Total Expense for Selected Date:** Rs. {tot_day_spend:,.2f}")
            else:
                st.info("No purchases recorded for this date yet.")
        else:
            st.info("No purchases recorded yet.")

# ==========================================
# SCREEN 3: 📦 DAILY INVENTORY & STOCK
# ==========================================
elif nav_option == "📦 Daily Inventory & Stock":
    st.title("📦 Daily Inventory & Stock Tracker")
    
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
        all_known_items = []
        if os.path.exists(INVENTORY_FILE):
            inv_f = pd.read_csv(INVENTORY_FILE)
            if not inv_f.empty and "Item Name" in inv_f.columns:
                all_known_items = inv_f[["Item Name", "Unit"]].drop_duplicates().to_dict('records')
                
        if not all_known_items:
            price_df = st.session_state.prices_data.copy()
            all_known_items = price_df[["Item Name", "Unit"]].to_dict('records') if "Unit" in price_df.columns else [{"Item Name": name, "Unit": "Pieces"} for name in price_df["Item Name"]]

        today_purchases = {}
        if os.path.exists(PURCHASES_FILE):
            purch_df = pd.read_csv(PURCHASES_FILE)
            purch_df_today = purch_df[purch_df["Date"] == str(selected_date)]
            if not purch_df_today.empty:
                today_purchases = purch_df_today.groupby("Item Name")["Quantity"].sum().to_dict()

        yesterday_date = str(selected_date - timedelta(days=1))
        yesterday_stock = {}
        if not existing_df.empty and "Date" in existing_df.columns:
            yest_df = existing_df[existing_df["Date"] == yesterday_date]
            if not yest_df.empty:
                for idx, r in yest_df.iterrows():
                    val = r.get("Remaining Stock (Actual)", r.get("Actual", 0.0))
                    yesterday_stock[r["Item Name"]] = float(val)

        rows = []
        for item in all_known_items:
            item_name = item["Item Name"]
            unit_val = item.get("Unit", "Pieces")
            op_val = yesterday_stock.get(item_name, 0.0)
            add_val = today_purchases.get(item_name, 0.0)
            
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

    st.subheader("📝 Edit Inventory Sheet")
    
    column_config = {
        "Unit": st.column_config.SelectboxColumn("Unit", options=["Pieces", "KG", "Grams", "Liters", "Portion"], required=True),
        "Opening Stock": st.column_config.NumberColumn("Opening Stock", step=0.1, format="%.2f"),
        "New Purchased": st.column_config.NumberColumn("New Purchased", step=0.1, format="%.2f"),
        "Sale / Used": st.column_config.NumberColumn("Sale / Used", step=0.1, format="%.2f"),
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
        
        df["Total Available Stock"] = df["Opening Stock"] + df["New Purchased"]
        df["Total Consumed/Used"] = df["Sale / Used"] + df["Wastage"]
        df["Remaining Stock (Actual)"] = df["Total Available Stock"] - df["Total Consumed/Used"] + df["Return"]
        
        df["Date"] = str(selected_date)
        df["Shift"] = shift
        df["Sale"] = df["Sale / Used"]
        df["Actual"] = df["Remaining Stock (Actual)"]

        st.markdown("### 📊 Auto-Calculated Final Summary")
        summary_cols = ["Item Name", "Unit", "Opening Stock", "New Purchased", "Total Available Stock", "Sale / Used", "Wastage", "Remaining Stock (Actual)"]
        st.dataframe(df[summary_cols], use_container_width=True)

        st.markdown("---")

        col_sv1, col_sv2, col_sv3 = st.columns([1.5, 1.5, 1.5])
        
        with col_sv1:
            if st.button("💾 Save Inventory Record", type="primary"):
                if os.path.exists(INVENTORY_FILE):
                    full_df = pd.read_csv(INVENTORY_FILE)
                    full_df = full_df[~((full_df["Date"] == str(selected_date)) & (full_df["Shift"] == shift))]
                    updated_df = pd.concat([full_df, df], ignore_index=True)
                else:
                    updated_df = df
                
                updated_df.to_csv(INVENTORY_FILE, index=False)
                st.success("✅ Inventory record saved successfully!")
                st.rerun()

        with col_sv2:
            whatsapp_msg = f"*🍕 Cheesy Delights Inventory Summary ({selected_date} - {shift})*\n\n"
            for _, row in df.iterrows():
                if row['Sale / Used'] > 0 or row['Remaining Stock (Actual)'] > 0:
                    whatsapp_msg += f"• *{row['Item Name']}*: Used = {row['Sale / Used']} {row['Unit']}, Remaining = {row['Remaining Stock (Actual)']}\n"
            
            encoded_msg = urllib.parse.quote(whatsapp_msg)
            clean_phone = phone_1.replace("+", "").replace("-", "").strip()
            whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
            
            st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:9px 16px; border-radius:8px; font-weight:bold; cursor:pointer; width:100%;">📲 Share via WhatsApp</button></a>', unsafe_allow_html=True)

        with col_sv3:
            if saved_data_found:
                if st.button("🗑️ Delete Saved Record", type="secondary"):
                    full_df = pd.read_csv(INVENTORY_FILE)
                    full_df = full_df[~((full_df["Date"] == str(selected_date)) & (full_df["Shift"] == shift))]
                    full_df.to_csv(INVENTORY_FILE, index=False)
                    st.success(f"🗑️ Deleted inventory record for {selected_date}")
                    st.rerun()

        st.markdown("---")
        st.download_button(
            label="📥 Download Today's Inventory Sheet (CSV)",
            data=df[summary_cols].to_csv(index=False).encode('utf-8'),
            file_name=f"inventory_{selected_date}_{shift}.csv",
            mime="text/csv"
        )

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
        
        sale_col_rep = "Sale" if "Sale" in merged_rep.columns else "Sale / Used"
        
        merged_rep["Revenue"] = merged_rep[sale_col_rep] * merged_rep[s_price_col]
        merged_rep["Cost"] = merged_rep[sale_col_rep] * merged_rep[p_price_col]
        merged_rep["Gross Profit"] = merged_rep["Revenue"] - merged_rep["Cost"]
        merged_rep["Date_dt"] = pd.to_datetime(merged_rep["Date"], errors='coerce')

        report_type = st.tabs(["📅 Daily Report", "🗓️ Monthly Report", "📆 Yearly Report"])

        # DAILY REPORT TAB
        with report_type[0]:
            all_available_dates = sorted(merged_rep["Date"].dropna().unique(), reverse=True)
            if len(all_available_dates) > 0:
                col_d1, col_d2 = st.columns([3, 1])
                with col_d1:
                    selected_daily_date = st.selectbox("Select Date", all_available_dates)
                
                daily_data = merged_rep[merged_rep["Date"] == str(selected_daily_date)]
                
                d_rev = daily_data["Revenue"].sum()
                d_cost = daily_data["Cost"].sum()
                d_profit = daily_data["Gross Profit"].sum()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Daily Revenue", f"Rs. {d_rev:,.2f}")
                m2.metric("Daily Cost", f"Rs. {d_cost:,.2f}")
                m3.metric("Daily Gross Profit", f"Rs. {d_profit:,.2f}")
                
                st.dataframe(daily_data[["Date", "Shift", "Item Name", "Unit", sale_col_rep, "Revenue", "Cost", "Gross Profit"]], use_container_width=True)
                
                col_dl, col_del = st.columns([2, 1])
                with col_dl:
                    st.download_button(
                        label="📥 Save Daily Report (CSV)",
                        data=daily_data.to_csv(index=False).encode('utf-8'),
                        file_name=f"profit_loss_daily_{selected_daily_date}.csv",
                        mime="text/csv"
                    )
                with col_del:
                    if st.button("🗑️ Delete Record for Selected Date", type="primary"):
                        full_df = pd.read_csv(INVENTORY_FILE)
                        updated_df = full_df[full_df["Date"] != str(selected_daily_date)]
                        updated_df.to_csv(INVENTORY_FILE, index=False)
                        st.success(f"🗑️ Record deleted for {selected_daily_date}")
                        st.rerun()

        # MONTHLY REPORT TAB
        with report_type[1]:
            merged_rep["Month_Year"] = merged_rep["Date_dt"].dt.strftime('%Y-%m')
            all_months = sorted(merged_rep["Month_Year"].dropna().unique(), reverse=True)
            if len(all_months) > 0:
                selected_month = st.selectbox("Select Month", all_months)
                monthly_data = merged_rep[merged_rep["Month_Year"] == selected_month]
                
                m_rev = monthly_data["Revenue"].sum()
                m_cost = monthly_data["Cost"].sum()
                m_profit = monthly_data["Gross Profit"].sum()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Monthly Revenue", f"Rs. {m_rev:,.2f}")
                m2.metric("Monthly Cost", f"Rs. {m_cost:,.2f}")
                m3.metric("Monthly Gross Profit", f"Rs. {m_profit:,.2f}")
                
                st.dataframe(monthly_data[["Date", "Shift", "Item Name", "Unit", sale_col_rep, "Revenue", "Cost", "Gross Profit"]], use_container_width=True)
                
                st.download_button(
                    label="📥 Save Monthly Report (CSV)",
                    data=monthly_data.to_csv(index=False).encode('utf-8'),
                    file_name=f"profit_loss_monthly_{selected_month}.csv",
                    mime="text/csv"
                )

        # YEARLY REPORT TAB
        with report_type[2]:
            merged_rep["Year"] = merged_rep["Date_dt"].dt.strftime('%Y')
            all_years = sorted(merged_rep["Year"].dropna().unique(), reverse=True)
            if len(all_years) > 0:
                selected_year = st.selectbox("Select Year", all_years)
                yearly_data = merged_rep[merged_rep["Year"] == selected_year]
                
                y_rev = yearly_data["Revenue"].sum()
                y_cost = yearly_data["Cost"].sum()
                y_profit = yearly_data["Gross Profit"].sum()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Yearly Revenue", f"Rs. {y_rev:,.2f}")
                m2.metric("Yearly Cost", f"Rs. {y_cost:,.2f}")
                m3.metric("Yearly Gross Profit", f"Rs. {y_profit:,.2f}")
                
                st.dataframe(yearly_data[["Date", "Shift", "Item Name", "Unit", sale_col_rep, "Revenue", "Cost", "Gross Profit"]], use_container_width=True)
                
                st.download_button(
                    label="📥 Save Yearly Report (CSV)",
                    data=yearly_data.to_csv(index=False).encode('utf-8'),
                    file_name=f"profit_loss_yearly_{selected_year}.csv",
                    mime="text/csv"
                )
    else:
        st.info("ℹ️ No inventory records saved yet to calculate Profit & Loss.")

# ==========================================
# SCREEN 6: ⚙️ SETTINGS
# ==========================================
else:
    st.title("⚙️ System Settings")
    
    st.subheader("📱 WhatsApp Phone Number Setup")
    with st.form("whatsapp_form"):
        new_phone_1 = st.text_input("WhatsApp Number (e.g., 923001234567)", value=phone_1)
        save_wa_btn = st.form_submit_button("💾 Save WhatsApp Number")
        if save_wa_btn:
            pd.DataFrame({"Key": ["phone_1"], "Value": [new_phone_1]}).to_csv(SETTINGS_FILE, index=False)
            st.success("✅ WhatsApp phone number updated successfully!")
            st.rerun()

    st.markdown("---")
    
    st.subheader("🔒 Change Password")
    with st.form("auth_form"):
        new_username = st.text_input("New Username", value=saved_user)
        new_password = st.text_input("New Password", value=saved_pass, type="password")
        if st.form_submit_button("Update Password"):
            pd.DataFrame({"Key": ["username", "password"], "Value": [new_username, new_password]}).to_csv(AUTH_FILE, index=False)
            st.success("✅ Password updated successfully!")
            st.rerun()
