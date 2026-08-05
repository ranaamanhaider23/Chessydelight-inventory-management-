from datetime import date, timedelta
import os
import urllib.parse
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Cheesy Delights | Complete Manager", layout="wide"
)

# ==========================================
# 🎨 CUSTOM CSS TO FIX SCROLLING & UI FOCUS
# ==========================================
st.markdown(
    """
    <style>
        .stDataFrame, .stDataEditor {
            overflow-x: auto;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 📁 DATA STORAGE FILES (CSV)
# ==========================================
INVENTORY_FILE = "inventory_records.csv"
EXPENSES_FILE = "expenses_records.csv"
POS_FILE = "pos_sales_records.csv"
SETTINGS_FILE = "settings.csv"
AUTH_FILE = "auth_settings.csv"

# ==========================================
# 🔐 AUTHENTICATION & PERSISTENT LOGIN SYSTEM
# ==========================================
if os.path.exists(AUTH_FILE):
  auth_df = pd.read_csv(AUTH_FILE)
  saved_admin_name = (
      auth_df.loc[auth_df["Key"] == "admin_name", "Value"].values[0]
      if "admin_name" in auth_df["Key"].values
      else "Admin"
  )
  saved_user = (
      auth_df.loc[auth_df["Key"] == "username", "Value"].values[0]
      if "username" in auth_df["Key"].values
      else "admin"
  )
  saved_pass = (
      auth_df.loc[auth_df["Key"] == "password", "Value"].values[0]
      if "password" in auth_df["Key"].values
      else "1234"
  )
else:
  saved_admin_name, saved_user, saved_pass = "Admin", "admin", "1234"

# Use st.query_params to persist login across page refreshes
query_params = st.query_params
if "logged_in" in query_params and query_params["logged_in"] == "true":
  st.session_state.authenticated = True

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

if not st.session_state.authenticated:
  st.title("🔒 Cheesy Delights - Login")
  st.write("Please enter your username and password to access the application:")

  with st.form("login_form"):
    entered_user = st.text_input("Username")
    entered_pass = st.text_input("Password", type="password")
    login_btn = st.form_submit_button("Login")

    if login_btn:
      if entered_user == str(saved_user) and entered_pass == str(saved_pass):
        st.session_state.authenticated = True
        st.query_params["logged_in"] = "true"
        st.rerun()
      else:
        st.error("❌ Incorrect Username or Password! Please try again.")
  st.stop()

# Load or Initialize Settings
if os.path.exists(SETTINGS_FILE):
  settings_df = pd.read_csv(SETTINGS_FILE)
  b1_name_def = (
      settings_df.loc[settings_df["Key"] == "b1_name", "Value"].values[0]
      if "b1_name" in settings_df["Key"].values
      else "Brother 1"
  )
  b1_phone_def = (
      settings_df.loc[settings_df["Key"] == "b1_phone", "Value"].values[0]
      if "b1_phone" in settings_df["Key"].values
      else ""
  )
  b2_name_def = (
      settings_df.loc[settings_df["Key"] == "b2_name", "Value"].values[0]
      if "b2_name" in settings_df["Key"].values
      else "Brother 2"
  )
  b2_phone_def = (
      settings_df.loc[settings_df["Key"] == "b2_phone", "Value"].values[0]
      if "b2_phone" in settings_df["Key"].values
      else ""
  )
else:
  b1_name_def, b1_phone_def, b2_name_def, b2_phone_def = (
      "Brother 1",
      "",
      "Brother 2",
      "",
  )

if "brother_1_name" not in st.session_state:
  st.session_state.brother_1_name = b1_name_def
if "brother_1_phone" not in st.session_state:
  st.session_state.brother_1_phone = str(b1_phone_def)
if "brother_2_name" not in st.session_state:
  st.session_state.brother_2_name = b2_name_def
if "brother_2_phone" not in st.session_state:
  st.session_state.brother_2_phone = str(b2_phone_def)

# ==========================================
# 🧭 SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
  st.markdown(f"### 👤 Welcome, {saved_admin_name}")
  st.markdown("---")
  st.markdown("## 🧭 Navigation Menu")
  nav_option = st.radio(
      "Select Section",
      [
          "🏠 Home Screen",
          "📦 All Inventory & Daily Entry",
          "🏷️ Pricing & Expenses",
          "⚡ Quick Sales (POS)",
          "📈 Monthly & Yearly Reports",
          "⚙️ Settings",
      ],
  )

  st.markdown("---")
  if st.button("🔒 Logout"):
    st.session_state.authenticated = False
    if "logged_in" in st.query_params:
      del st.query_params["logged_in"]
    st.rerun()

# ==========================================
# DATA FRAMES INITIALIZATION (Independent)
# ==========================================
if "prices_data" not in st.session_state:
  st.session_state.prices_data = pd.DataFrame([
      {
          "Item Name": "Zinger Burger",
          "Category": "Burgers",
          "Purchase Price": 250.0,
          "Selling Price": 450.0,
      },
      {
          "Item Name": "French Fries (Large)",
          "Category": "Fries",
          "Purchase Price": 80.0,
          "Selling Price": 180.0,
      },
  ])

if "inventory_master_data" not in st.session_state:
  st.session_state.inventory_master_data = pd.DataFrame([
      {
          "Item Name": "Zinger Burger",
          "Category": "Burgers",
          "Unit": "Pieces",
          "Min Stock Limit": 10,
      },
      {
          "Item Name": "French Fries (Large)",
          "Category": "Fries",
          "Unit": "Portion",
          "Min Stock Limit": 15,
      },
      {
          "Item Name": "Onion",
          "Category": "Vegetables",
          "Unit": "Kg",
          "Min Stock Limit": 5,
      },
  ])

# ==========================================
# SCREEN 1: 🏠 HOME SCREEN
# ==========================================
if nav_option == "🏠 Home Screen":
  st.title("🍕 Cheesy Delights - Home Dashboard")
  st.write(f"Welcome back, **{saved_admin_name}**! Here is your business overview:")

  total_rev = 0.0
  total_cost = 0.0
  total_exp = 0.0

  if os.path.exists(INVENTORY_FILE):
    inv_records = pd.read_csv(INVENTORY_FILE)
    prices_df = st.session_state.prices_data
    merged_home = pd.merge(
        inv_records, prices_df, on="Item Name", how="left"
    ).fillna(0)
    merged_home["Revenue"] = merged_home["Sale"] * merged_home["Selling Price"]
    merged_home["Cost"] = merged_home["Sale"] * merged_home["Purchase Price"]
    total_rev = merged_home["Revenue"].sum()
    total_cost = merged_home["Cost"].sum()

  if os.path.exists(POS_FILE):
    pos_records = pd.read_csv(POS_FILE)
    if "Total Amount" in pos_records.columns:
      total_rev += pos_records["Total Amount"].sum()

  if os.path.exists(EXPENSES_FILE):
    exp_df = pd.read_csv(EXPENSES_FILE)
    if "Amount" in exp_df.columns:
      total_exp = exp_df["Amount"].sum()

  gross_profit = total_rev - total_cost
  net_profit_loss = gross_profit - total_exp

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Total Revenue", f"Rs. {total_rev:,.2f}")
  m2.metric("Gross Profit", f"Rs. {gross_profit:,.2f}")
  m3.metric("Total Expenses", f"Rs. {total_exp:,.2f}")

  if net_profit_loss >= 0:
    m4.metric(
        "Net Profit",
        f"Rs. {net_profit_loss:,.2f}",
        delta="Profit",
        delta_color="normal",
    )
  else:
    m4.metric(
        "Net Loss",
        f"Rs. {net_profit_loss:,.2f}",
        delta="Loss",
        delta_color="inverse",
    )

  st.markdown("---")

  if os.path.exists(INVENTORY_FILE):
    saved_inv = pd.read_csv(INVENTORY_FILE)
    latest_date = (
        saved_inv["Date"].max() if "Date" in saved_inv.columns else None
    )
    if latest_date:
      latest_df = saved_inv[saved_inv["Date"] == latest_date]
      if (
          "Actual" in latest_df.columns
          and "Min Stock Limit" in latest_df.columns
      ):
        low_stock_items = latest_df[
            latest_df["Actual"] <= latest_df["Min Stock Limit"]
        ]
        if not low_stock_items.empty:
          st.error(
              "⚠️ **Low Stock Alert!** Following items are running low and"
              " need reordering:"
          )
          for _, row in low_stock_items.iterrows():
            st.markdown(
                f"- **{row['Item Name']}**: Current Stock = {row['Actual']}"
                f" (Limit: {row['Min Stock Limit']})"
            )
        else:
          st.success("✅ All live stock items have sufficient levels.")

  st.markdown("---")
  st.subheader("📦 Live Stock Overview (Latest Saved Record)")

  if os.path.exists(INVENTORY_FILE):
    if latest_date:
      st.info(f"Showing latest saved stock for date: {latest_date}")
      st.dataframe(latest_df, use_container_width=True)
    else:
      st.dataframe(saved_inv, use_container_width=True)
  else:
    st.info("No saved inventory data found yet.")

# ==========================================
# SCREEN 2: 📦 ALL INVENTORY & DAILY ENTRY
# ==========================================
elif nav_option == "📦 All Inventory & Daily Entry":
  st.title("📦 Daily Inventory & Sales Entry")

  with st.form("inventory_date_form"):
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
      selected_date = st.date_input("Select Date", date.today())
    with col_f2:
      shift = st.selectbox("Select Shift", ["Morning", "Evening", "Full Day"])
    with col_f3:
      st.write("")
      st.write("")
      load_form_btn = st.form_submit_button("Load Date Entry Form")

  st.markdown("---")
  st.subheader("🛠️ Manage Inventory Item Master List")
  with st.expander("Click here to add/edit items appearing in Daily Entry"):
    edited_inv_master = st.data_editor(
        st.session_state.inventory_master_data,
        num_rows="dynamic",
        key="inv_master_box",
        use_container_width=True,
    )
    st.session_state.inventory_master_data = edited_inv_master

  st.markdown("---")

  # Check if record already exists for selected date and shift
  existing_record_found = False
  matched_existing_df = pd.DataFrame()

  if os.path.exists(INVENTORY_FILE):
    all_past_inv = pd.read_csv(INVENTORY_FILE)
    if not all_past_inv.empty and "Date" in all_past_inv.columns:
      if "Shift" in all_past_inv.columns:
        matched_existing_df = all_past_inv[
            (all_past_inv["Date"] == str(selected_date))
            & (all_past_inv["Shift"] == shift)
        ]
      else:
        matched_existing_df = all_past_inv[
            all_past_inv["Date"] == str(selected_date)
        ]

      if not matched_existing_df.empty:
        existing_record_found = True

  if existing_record_found:
    st.success(
        f"💡 Loaded previously saved record for date: {selected_date} ({shift})"
    )
    default_inv = matched_existing_df
  else:
    default_rows = []
    prev_date_str = str(selected_date - timedelta(days=1))
    has_prev_data = False
    if os.path.exists(INVENTORY_FILE):
      past_inv = pd.read_csv(INVENTORY_FILE)
      if not past_inv.empty and "Date" in past_inv.columns:
        prev_day_records = past_inv[past_inv["Date"] == prev_date_str]
        if not prev_day_records.empty:
          has_prev_data = True

    inv_master = st.session_state.inventory_master_data

    for _, p_row in inv_master.iterrows():
      i_name = p_row["Item Name"]
      i_cat = p_row.get("Category", "General")
      i_unit = p_row.get("Unit", "Pieces")
      min_limit = int(p_row.get("Min Stock Limit", 10))
      opening_val = 50

      if has_prev_data:
        matched_item = prev_day_records[prev_day_records["Item Name"] == i_name]
        if not matched_item.empty:
          opening_val = int(matched_item.iloc[-1].get("Actual", 50))

      default_rows.append({
          "Item Name": i_name,
          "Category": i_cat,
          "Unit": i_unit,
          "Opening": opening_val,
          "Additional": 0,
          "Sale": 0,
          "Discount": 0,
          "Return": 0,
          "Wastage": 0,
          "Actual": opening_val,
          "Min Stock Limit": min_limit,
      })

    default_inv = pd.DataFrame(default_rows)
    if has_prev_data:
      st.success(
          f"💡 Opening stock loaded from previous day ({prev_date_str})!"
      )

  edited_inventory = st.data_editor(
      default_inv, num_rows="dynamic", key="all_inv_box", use_container_width=True
  )

  if not edited_inventory.empty:
    df = edited_inventory.copy()
    df["Date"] = str(selected_date)
    df["Shift"] = shift
    df["Total"] = df["Opening"] + df["Additional"]
    df["Balance"] = (
        df["Total"] - (df["Sale"] - df["Discount"]) + df["Return"] - df["Wastage"]
    )
    df["Variance"] = df["Actual"] - df["Balance"]

    if st.button("💾 Save Today's Record"):
      if os.path.exists(INVENTORY_FILE):
        existing_df = pd.read_csv(INVENTORY_FILE)
        if "Shift" in existing_df.columns:
          existing_df = existing_df[~(
              (existing_df["Date"] == str(selected_date))
              & (existing_df["Shift"] == shift)
          )]
        else:
          existing_df = existing_df[existing_df["Date"] != str(selected_date)]
        updated_df = pd.concat([existing_df, df], ignore_index=True)
      else:
        updated_df = df
      updated_df.to_csv(INVENTORY_FILE, index=False)
      st.success("✅ Today's inventory record saved permanently!")
      st.rerun()

    st.markdown("#### 📊 Calculated Report Preview")
    st.dataframe(df, use_container_width=True)

  st.markdown("---")
  st.subheader("📦 Demand Box (Send Order via WhatsApp)")

  if not edited_inventory.empty:
    demand_df = edited_inventory[
        edited_inventory["Actual"] <= edited_inventory["Min Stock Limit"]
    ]

    if not demand_df.empty:
      demand_text = f"--- CHEESY DELIGHTS STOCK DEMAND ({selected_date}) ---\n"
      for index, row in demand_df.iterrows():
        required_qty = (row["Min Stock Limit"] - row["Actual"]) + 10
        demand_text += f"• Item: {row['Item Name']} | Unit: {row['Unit']} | Current: {row['Actual']} | Bring: {required_qty}\n"

      final_demand_text = st.text_area(
          "Review Order Text:", value=demand_text, height=140
      )
      encoded_text = urllib.parse.quote(final_demand_text)

      st.markdown("### 🟢 Send via WhatsApp")
      w_col1, w_col2 = st.columns(2)

      with w_col1:
        if st.session_state.brother_1_phone:
          wa_link_1 = (
              f"https://wa.me/{st.session_state.brother_1_phone}?text={encoded_text}"
          )
          st.markdown(
              f'<a href="{wa_link_1}" target="_blank"><button'
              ' style="background-color:#25D366; color:white; border:none;'
              " padding:10px 20px; border-radius:5px; font-weight:bold;"
              f' cursor:pointer;">💬 Send to {st.session_state.brother_1_name}</button></a>',
              unsafe_allow_html=True,
          )
        else:
          st.warning("Add Brother 1 number in Settings tab.")

      with w_col2:
        if st.session_state.brother_2_phone:
          wa_link_2 = (
              f"https://wa.me/{st.session_state.brother_2_phone}?text={encoded_text}"
          )
          st.markdown(
              f'<a href="{wa_link_2}" target="_blank"><button'
              ' style="background-color:#25D366; color:white; border:none;'
              " padding:10px 20px; border-radius:5px; font-weight:bold;"
              f' cursor:pointer;">💬 Send to {st.session_state.brother_2_name}</button></a>',
              unsafe_allow_html=True,
          )
        else:
          st.warning("Add Brother 2 number in Settings tab.")
    else:
      st.success("✅ All items have sufficient stock levels.")

# ==========================================
# SCREEN 3: 🏷️ EXPENSES MANAGEMENT
# ==========================================
elif nav_option == "🏷️ Pricing & Expenses":
  st.title("💸 Daily Expenses Management")

  st.subheader("💸 Daily Expenses Box")
  default_expenses = pd.DataFrame([{
      "Expense Reason": "Utility / Bills",
      "Amount": 1500.0,
  }, {
      "Expense Reason": "Raw Material Cash",
      "Amount": 2000.0,
  }])
  edited_expenses = st.data_editor(
      default_expenses,
      num_rows="dynamic",
      key="exp_box",
      use_container_width=True,
  )

  if st.button("💾 Save Today's Expenses"):
    edited_expenses["Date"] = str(date.today())
    if os.path.exists(EXPENSES_FILE):
      exp_df = pd.read_csv(EXPENSES_FILE)
      exp_df = exp_df[exp_df["Date"] != str(date.today())]
      exp_updated = pd.concat([exp_df, edited_expenses], ignore_index=True)
    else:
      exp_updated = edited_expenses
    exp_updated.to_csv(EXPENSES_FILE, index=False)
    st.success("✅ Expenses saved permanently!")

  if os.path.exists(EXPENSES_FILE):
    exp_history = pd.read_csv(EXPENSES_FILE)
    if not exp_history.empty and "Expense Reason" in exp_history.columns:
      st.markdown("#### 📊 Expenses Breakdown Chart")
      exp_chart_data = (
          exp_history.groupby("Expense Reason")["Amount"].sum().reset_index()
      )
      st.bar_chart(exp_chart_data.set_index("Expense Reason"))

# ==========================================
# SCREEN 4: ⚡ QUICK SALES (POS)
# ==========================================
elif nav_option == "⚡ Quick Sales (POS)":
  st.title("⚡ Quick Sales Calculator (POS)")
  st.write(
      "Add and edit items like the inventory box. Enter the quantity sold and"
      " remaining stock, and totals will calculate automatically:"
  )

  pos_date = st.date_input(
      "Select Sale Date", date.today(), key="pos_date_picker"
  )

  if "pos_df_state" not in st.session_state:
    st.session_state.pos_df_state = pd.DataFrame([
        {
            "Item Name": "Zinger Burger",
            "Quantity Sold": 1,
            "Stock Remaining": 15,
            "Price Per Unit": 450.0,
        },
        {
            "Item Name": "French Fries (Large)",
            "Quantity Sold": 2,
            "Stock Remaining": 20,
            "Price Per Unit": 180.0,
        },
    ])

  edited_pos_df = st.data_editor(
      st.session_state.pos_df_state,
      num_rows="dynamic",
      key="pos_table_editor",
      use_container_width=True,
  )
  st.session_state.pos_df_state = edited_pos_df

  if not edited_pos_df.empty:
    df_pos = edited_pos_df.copy()
    df_pos["Quantity Sold"] = pd.to_numeric(
        df_pos["Quantity Sold"], errors="coerce"
    ).fillna(0)
    df_pos["Stock Remaining"] = pd.to_numeric(
        df_pos["Stock Remaining"], errors="coerce"
    ).fillna(0)
    df_pos["Price Per Unit"] = pd.to_numeric(
        df_pos["Price Per Unit"], errors="coerce"
    ).fillna(0.0)
    df_pos["Total Amount"] = df_pos["Quantity Sold"] * df_pos["Price Per Unit"]

    total_items_sold = int(df_pos["Quantity Sold"].sum())
    grand_total = float(df_pos["Total Amount"].sum())

    st.markdown("---")
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("📦 Total Items Sold (Quantity)", f"{total_items_sold} Units")
    col_m2.metric("💰 Grand Total Amount", f"Rs. {grand_total:,.2f}")

    st.markdown("#### 📊 POS Calculated Summary Preview")
    st.dataframe(df_pos, use_container_width=True)

    if st.button("💾 Save Today's POS Sales"):
      df_pos["Date"] = str(pos_date)
      if os.path.exists(POS_FILE):
        existing_pos = pd.read_csv(POS_FILE)
        existing_pos = existing_pos[existing_pos["Date"] != str(pos_date)]
        updated_pos = pd.concat([existing_pos, df_pos], ignore_index=True)
      else:
        updated_pos = df_pos
      updated_pos.to_csv(POS_FILE, index=False)
      st.success("✅ POS sales saved successfully!")

  if os.path.exists(POS_FILE):
    st.markdown("---")
    st.subheader("📜 Saved POS Sales History")
    saved_pos_history = pd.read_csv(POS_FILE)
    st.dataframe(saved_pos_history, use_container_width=True)

# ==========================================
# SCREEN 5: 📈 REPORTS
# ==========================================
elif nav_option == "📈 Monthly & Yearly Reports":
  st.title("📈 Business Reports & Custom Date Range")
  st.write("Analyze business revenue and profit with advanced filters:")

  if os.path.exists(INVENTORY_FILE):
    inv_records = pd.read_csv(INVENTORY_FILE)

    if "Category" not in inv_records.columns:
      inv_records["Category"] = "General"

    prices_df = st.session_state.prices_data

    merged_rep = pd.merge(
        inv_records, prices_df, on="Item Name", how="left"
    ).fillna(0)
    if "Category_x" in merged_rep.columns:
      merged_rep["Category"] = merged_rep["Category_x"]
      merged_rep.drop(
          columns=["Category_x", "Category_y"], errors="ignore", inplace=True
      )

    merged_rep["Revenue"] = merged_rep["Sale"] * merged_port["Selling Price"] if "Selling Price" in merged_rep.columns else merged_rep["Sale"] * 0
    # Safe calculation for revenue & profit
    merged_rep["Revenue"] = merged_rep["Sale"] * merged_rep.get(
        "Selling Price", 0
    )
    merged_rep["Cost"] = merged_rep["Sale"] * merged_rep.get(
        "Purchase Price", 0
    )
    merged_rep["Profit"] = merged_rep["Revenue"] - merged_rep["Cost"]

    merged_rep["Date_Parsed"] = pd.to_datetime(
        merged_rep["Date"], errors="coerce"
    )
    merged_rep["Year"] = merged_rep["Date_Parsed"].dt.year
    merged_rep["Month"] = merged_rep["Date_Parsed"].dt.strftime("%Y-%m")

    tab1, tab2, tab3 = st.tabs(
        ["📅 Monthly Report", "📊 Yearly Report", "🔍 Custom Date Filter"]
    )

    with tab1:
      st.subheader("Monthly Sales & Profit Breakdown")
      valid_months = merged_rep["Month"].dropna().unique()
      if len(valid_months) > 0:
        selected_month = st.selectbox(
            "Select Month", sorted(valid_months, reverse=True)
        )
        month_data = merged_rep[merged_rep["Month"] == selected_month]

        m_revenue = month_data["Revenue"].sum()
        m_profit = month_data["Profit"].sum()

        if os.path.exists(POS_FILE):
          pos_hist = pd.read_csv(POS_FILE)
          if "Date" in pos_hist.columns and "Total Amount" in pos_hist.columns:
            pos_hist["Month"] = pd.to_datetime(
                pos_hist["Date"], errors="coerce"
            ).dt.strftime("%Y-%m")
            m_pos = pos_hist[pos_hist["Month"] == selected_month]
            m_revenue += m_pos["Total Amount"].sum()

        c1, c2 = st.columns(2)
        c1.metric(
            label=f"Total Revenue ({selected_month})",
            value=f"Rs. {m_revenue:,.2f}",
        )
        c2.metric(
            label=f"Total Gross Profit ({selected_month})",
            value=f"Rs. {m_profit:,.2f}",
        )

        show_cols = [
            c
            for c in [
                "Date",
                "Item Name",
                "Category",
                "Sale",
                "Revenue",
                "Profit",
            ]
            if c in month_data.columns
        ]
        st.dataframe(month_data[show_cols], use_container_width=True)

        st.markdown("#### 📈 Visual Performance Chart")
        chart_data = (
            month_data.groupby("Item Name")[["Revenue", "Profit"]]
            .sum()
            .reset_index()
        )
        if not chart_data.empty:
          st.bar_chart(chart_data.set_index("Item Name"))

        @st.cache_data
        def convert_df_to_csv(df):
          return df.to_csv(index=False).encode("utf-8")

        csv_data = convert_df_to_csv(month_data)
        st.download_button(
            label="📥 Download Monthly Report (Excel/CSV)",
            data=csv_data,
            file_name=f"Cheesy_Delights_Monthly_{selected_month}.csv",
            mime="text/csv",
        )
      else:
        st.info("No valid month data available.")

    with tab2:
      st.subheader("Yearly Sales & Profit Breakdown")
      valid_years = merged_rep["Year"].dropna().unique()
      if len(valid_years) > 0:
        selected_year = st.selectbox(
            "Select Year", sorted(valid_years, reverse=True)
        )
        year_data = merged_rep[merged_rep["Year"] == selected_year]

        y_revenue = year_data["Revenue"].sum()
        y_profit = year_data["Profit"].sum()

        y1, y2 = st.columns(2)
        y1.metric(
            label=f"Total Revenue ({selected_year})",
            value=f"Rs. {y_revenue:,.2f}",
        )
        y2.metric(
            label=f"Total Gross Profit ({selected_year})",
            value=f"Rs. {y_profit:,.2f}",
        )

        show_y_cols = [
            c
            for c in [
                "Month",
                "Item Name",
                "Category",
                "Sale",
                "Revenue",
                "Profit",
            ]
            if c in year_data.columns
        ]
        st.dataframe(year_data[show_y_cols], use_container_width=True)

        st.markdown("#### 📈 Yearly Trend Chart")
        y_chart_data = (
            year_data.groupby("Month")[["Revenue", "Profit"]].sum().reset_index()
        )
        if not y_chart_data.empty:
          st.bar_chart(y_chart_data.set_index("Month"))
      else:
        st.info("No valid year data available.")

    with tab3:
      st.subheader("🔍 Custom Date Range Filter")
      d_col1, d_col2 = st.columns(2)
      with d_col1:
        start_d = st.date_input("Start Date", date.today())
      with d_col2:
        end_d = st.date_input("End Date", date.today())

      filtered_range_data = merged_rep[
          (merged_rep["Date_Parsed"].dt.date >= start_d)
          & (merged_rep["Date_Parsed"].dt.date <= end_d)
      ]

      if not filtered_range_data.empty:
        r_rev = filtered_range_data["Revenue"].sum()
        r_prof = filtered_range_data["Profit"].sum()

        rc1, rc2 = st.columns(2)
        rc1.metric("Revenue in Range", f"Rs. {r_rev:,.2f}")
        rc2.metric("Gross Profit in Range", f"Rs. {r_prof:,.2f}")

        show_r_cols = [
            c
            for c in [
                "Date",
                "Item Name",
                "Category",
                "Sale",
                "Revenue",
                "Profit",
            ]
            if c in filtered_range_data.columns
        ]
        st.dataframe(filtered_range_data[show_r_cols], use_container_width=True)
      else:
        st.info("No records found in this date range.")

    st.markdown("---")
    st.subheader("🗑️ Delete Saved Date Record")
    available_dates = sorted(inv_records["Date"].dropna().unique(), reverse=True)
    if len(available_dates) > 0:
      date_to_delete = st.selectbox(
          "Select Date to Delete", available_dates, key="del_date_report"
      )
      if st.button("🗑️ Delete Selected Date Record"):
        new_saved_df = inv_records[inv_records["Date"] != date_to_delete]
        new_saved_df.to_csv(INVENTORY_FILE, index=False)
        st.success(
            f"✅ Record for date {date_to_delete} has been deleted successfully!"
        )
        st.rerun()
    else:
      st.info("No records available to delete.")
  else:
    st.warning("⚠️ No saved inventory records found yet!")

# ==========================================
# SCREEN 6: ⚙️ SETTINGS
# ==========================================
else:
  st.title("⚙️ Settings & Configuration")

  st.subheader("🔑 Change Admin Name, Username & Password")
  with st.form("auth_form"):
    new_admin_name = st.text_input("Admin Name", value=saved_admin_name)
    new_username = st.text_input("New Username", value=saved_user)
    new_password = st.text_input(
        "New Password", value=saved_pass, type="password"
    )

    if st.form_submit_button("Update Login Credentials"):
      auth_save = pd.DataFrame({
          "Key": ["admin_name", "username", "password"],
          "Value": [new_admin_name, new_username, new_password],
      })
      auth_save.to_csv(AUTH_FILE, index=False)
      st.success("✅ Admin credentials updated permanently! Please reload.")

  st.markdown("---")
  st.subheader("📥 Data Backup Feature")
  st.write("Download your complete inventory records as backup:")
  if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "rb") as f:
      st.download_button(
          label="💾 Download Complete Inventory Backup (.csv)",
          data=f,
          file_name="inventory_backup.csv",
          mime="text/csv",
      )

  st.markdown("---")
  st.subheader("💬 WhatsApp Contacts Configuration")
  with st.form("settings_form"):
    b1_name_in = st.text_input(
        "Brother 1 Name", value=st.session_state.brother_1_name
    )
    b1_phone_in = st.text_input(
        "Brother 1 WhatsApp (with country code, e.g. 92300...)",
        value=st.session_state.brother_1_phone,
    )

    st.markdown("---")

    b2_name_in = st.text_input(
        "Brother 2 Name", value=st.session_state.brother_2_name
    )
    b2_phone_in = st.text_input(
        "Brother 2 WhatsApp (with country code, e.g. 92300...)",
        value=st.session_state.brother_2_phone,
    )

    if st.form_submit_button("Save WhatsApp Settings"):
      st.session_state.brother_1_name = b1_name_in
      st.session_state.brother_1_phone = b1_phone_in
      st.session_state.brother_2_name = b2_name_in
      st.session_state.brother_2_phone = b2_phone_in

      settings_save = pd.DataFrame({
          "Key": ["b1_name", "b1_phone", "b2_name", "b2_phone"],
          "Value": [b1_name_in, b1_phone_in, b2_name_in, b2_phone_in],
      })
      settings_save.to_csv(SETTINGS_FILE, index=False)
      st.success("✅ WhatsApp settings saved permanently!")
