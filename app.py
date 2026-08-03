from datetime import date
import os
import urllib.parse
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Cheesy Delights | Complete Manager", layout="wide")

# ==========================================
# 🎨 CUSTOM CSS TO FIX SCROLLING & UI FOCUS
# ==========================================
st.markdown(
    """
    <style>
        /* Prevent jarring page jumps on data edits */
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
SETTINGS_FILE = "settings.csv"
AUTH_FILE = "auth_settings.csv"

# ==========================================
# 🔐 AUTHENTICATION & LOGIN SYSTEM
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
          "📈 Monthly & Yearly Reports",
          "⚙️ Settings",
      ],
  )
  st.markdown("---")
  if st.button("🔒 Logout"):
    st.session_state.authenticated = False
    st.rerun()

# ==========================================
# DATA FRAMES INITIALIZATION
# ==========================================
if "prices_data" not in st.session_state:
  st.session_state.prices_data = pd.DataFrame([
      {
          "Item Name": "Zinger Burger",
          "Purchase Price": 250.0,
          "Selling Price": 450.0,
      },
      {
          "Item Name": "French Fries (Large)",
          "Purchase Price": 80.0,
          "Selling Price": 180.0,
      },
  ])

# ==========================================
# SCREEN 1: 🏠 HOME SCREEN (With Profit/Loss & Expenses Summary)
# ==========================================
if nav_option == "🏠 Home Screen":
  st.title("🍕 Cheesy Delights - Home Dashboard")
  st.write(f"Welcome back, **{saved_admin_name}**! Here is your business overview:")

  # Calculate Financial Summary if records exist
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

  if os.path.exists(EXPENSES_FILE):
    exp_df = pd.read_csv(EXPENSES_FILE)
    if "Amount" in exp_df.columns:
      total_exp = exp_df["Amount"].sum()

  gross_profit = total_rev - total_cost
  net_profit_loss = gross_profit - total_exp

  # Display Metrics on Home Screen
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
  st.subheader("📦 Live Stock Overview")

  if os.path.exists(INVENTORY_FILE):
    saved_inv = pd.read_csv(INVENTORY_FILE)
    latest_date = (
        saved_inv["Date"].max() if "Date" in saved_inv.columns else None
    )
    if latest_date:
      st.info(f"Showing latest saved stock for date: {latest_date}")
      latest_df = saved_inv[saved_inv["Date"] == latest_date]
      st.dataframe(latest_df, use_container_width=True)
    else:
      st.dataframe(saved_inv, use_container_width=True)
  else:
    st.info(
        "No saved inventory data found yet. Go to 'All Inventory & Daily Entry'"
        " to save records."
    )

# ==========================================
# SCREEN 2: 📦 ALL INVENTORY & DAILY ENTRY
# ==========================================
elif nav_option == "📦 All Inventory & Daily Entry":
  st.title("📦 Daily Inventory & Sales Entry")

  col1, col2 = st.columns(2)
  with col1:
    selected_date = st.date_input("Select Date", date.today())
  with col2:
    shift = st.selectbox("Select Shift", ["Morning", "Evening", "Full Day"])

  st.markdown("---")

  default_inv = pd.DataFrame([
      {
          "Item Name": "Zinger Burger",
          "Unit": "Pieces",
          "Opening": 50,
          "Additional": 10,
          "Sale": 20,
          "Discount": 2,
          "Return": 1,
          "Wastage": 1,
          "Actual": 5,
          "Min Stock Limit": 10,
      },
      {
          "Item Name": "French Fries (Large)",
          "Unit": "Portion",
          "Opening": 40,
          "Additional": 5,
          "Sale": 25,
          "Discount": 0,
          "Return": 0,
          "Wastage": 2,
          "Actual": 18,
          "Min Stock Limit": 15,
      },
  ])

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

    # Save Button
    if st.button("💾 Save Today's Record"):
      if os.path.exists(INVENTORY_FILE):
        existing_df = pd.read_csv(INVENTORY_FILE)
        existing_df = existing_df[~(
            (existing_df["Date"] == str(selected_date))
            & (existing_df["Shift"] == shift)
        )]
        updated_df = pd.concat([existing_df, df], ignore_index=True)
      else:
        updated_df = df
      updated_df.to_csv(INVENTORY_FILE, index=False)
      st.success("✅ Today's inventory record saved permanently!")

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
# SCREEN 3: 🏷️ PRICING & EXPENSES
# ==========================================
elif nav_option == "🏷️ Pricing & Expenses":
  st.title("🏷️ Pricing & Daily Expenses Management")

  st.subheader("🏷️ Purchase & Selling Prices Box")
  edited_prices = st.data_editor(
      st.session_state.prices_data,
      num_rows="dynamic",
      key="price_box",
      use_container_width=True,
  )
  st.session_state.prices_data = edited_prices

  st.markdown("---")

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

# ==========================================
# SCREEN 4: 📈 MONTHLY & YEARLY REPORTS
# ==========================================
elif nav_option == "📈 Monthly & Yearly Reports":
  st.title("📈 Monthly & Yearly Sales / Profit Reports")
  st.write(
      "Analyze business revenue and profit over months and years based on saved"
      " records:"
  )

  if os.path.exists(INVENTORY_FILE):
    inv_records = pd.read_csv(INVENTORY_FILE)
    prices_df = st.session_state.prices_data

    merged_rep = pd.merge(
        inv_records, prices_df, on="Item Name", how="left"
    ).fillna(0)
    merged_rep["Revenue"] = merged_rep["Sale"] * merged_rep["Selling Price"]
    merged_rep["Cost"] = merged_rep["Sale"] * merged_rep["Purchase Price"]
    merged_rep["Profit"] = merged_rep["Revenue"] - merged_rep["Cost"]

    merged_rep["Date_Parsed"] = pd.to_datetime(
        merged_rep["Date"], errors="coerce"
    )
    merged_rep["Year"] = merged_rep["Date_Parsed"].dt.year
    merged_rep["Month"] = merged_rep["Date_Parsed"].dt.strftime("%Y-%m")

    tab1, tab2 = st.tabs(["📅 Monthly Report", "📊 Yearly Report"])

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

        c1, c2 = st.columns(2)
        c1.metric(
            label=f"Total Revenue ({selected_month})",
            value=f"Rs. {m_revenue:,.2f}",
        )
        c2.metric(
            label=f"Total Gross Profit ({selected_month})",
            value=f"Rs. {m_profit:,.2f}",
        )

        st.dataframe(
            month_data[["Date", "Item Name", "Sale", "Revenue", "Profit"]],
            use_container_width=True,
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

        st.dataframe(
            year_data[["Month", "Item Name", "Sale", "Revenue", "Profit"]],
            use_container_width=True,
        )
      else:
        st.info("No valid year data available.")

    st.markdown("---")

    # ==========================================
    # 🗑️ DELETE RECORD SECTION (IN REPORTS)
    # ==========================================
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
# SCREEN 5: ⚙️ SETTINGS
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
