import streamlit as st
import pandas as pd
from datetime import date, datetime
import os

# =========================================================
# CHEESY DELIGHTS — PROFESSIONAL RESTAURANT INVENTORY OS
# =========================================================
st.set_page_config(
    page_title="Cheesy Delights | Restaurant OS",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Theme ----------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg:#0b1120;
    --panel:#111827;
    --panel2:#172033;
    --border:#263247;
    --text:#eef2ff;
    --muted:#94a3b8;
    --blue:#38bdf8;
    --green:#34d399;
    --orange:#f59e0b;
    --red:#fb7185;
}

.stApp {
    background: radial-gradient(circle at 80% 0%, #13243d 0, #0b1120 34%, #070b14 100%);
    color:var(--text);
    font-family:'Inter',sans-serif;
}
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#070b14,#0b1220);
    border-right:1px solid var(--border);
}
[data-testid="stSidebar"] * { font-family:'Inter',sans-serif; }
.block-container { padding-top:1.8rem; max-width:1450px; }

.hero {
    padding:24px 26px;
    border:1px solid var(--border);
    border-radius:22px;
    background:linear-gradient(135deg,rgba(30,41,59,.92),rgba(15,23,42,.82));
    box-shadow:0 18px 45px rgba(0,0,0,.24);
    margin-bottom:20px;
}
.hero-title {font-size:30px;font-weight:800;letter-spacing:-.8px;}
.hero-sub {color:var(--muted);margin-top:5px;font-size:13px;}

.kpi {
    padding:18px 19px;
    border:1px solid var(--border);
    border-radius:18px;
    background:linear-gradient(145deg,#162033,#0f1726);
    box-shadow:0 10px 25px rgba(0,0,0,.18);
    min-height:120px;
}
.kpi-label {font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.7px;font-weight:700;}
.kpi-value {font-size:27px;font-weight:800;margin-top:9px;}
.kpi-note {font-size:11px;color:#64748b;margin-top:7px;}

.section {
    font-size:18px;font-weight:800;margin:24px 0 12px;
}
.panel {
    border:1px solid var(--border);
    border-radius:18px;
    background:rgba(17,24,39,.78);
    padding:18px;
    margin-bottom:16px;
}
.item-card {
    border:1px solid var(--border);
    border-radius:16px;
    padding:16px;
    background:linear-gradient(145deg,#162033,#0f1726);
    margin-bottom:12px;
}
.item-name {font-weight:700;font-size:14px;}
.item-stock {font-size:25px;font-weight:800;margin:8px 0 3px;}
.pill {
    display:inline-block;padding:4px 9px;border-radius:999px;
    font-size:10px;font-weight:800;letter-spacing:.3px;
}
.good {background:rgba(52,211,153,.12);color:#6ee7b7;border:1px solid #065f46;}
.warn {background:rgba(251,113,133,.12);color:#fda4af;border:1px solid #9f1239;}

.stButton>button {
    border-radius:10px!important;
    border:1px solid #2563eb!important;
    background:linear-gradient(135deg,#2563eb,#1d4ed8)!important;
    color:white!important;font-weight:700!important;
}
.stDownloadButton>button {
    border-radius:10px!important;
    font-weight:700!important;
}
div[data-baseweb="tab-list"] {gap:8px;}
button[data-baseweb="tab"] {font-weight:700;}

[data-testid="stMetric"] {
    background:transparent;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------- Files -----------------------
STOCK_FILE = "daily_closing_stock.csv"
HISTORY_FILE = "inventory_history_archive.csv"
PURCHASE_FILE = "purchases_log.csv"
SALES_FILE = "sales_log.csv"
EXPENSE_FILE = "expenses_log.csv"

def save_csv(df, path):
    df.to_csv(path, index=False)

def load_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=columns)

# Compatible with the user's existing inventory file
if not os.path.exists(STOCK_FILE):
    pd.DataFrame([
        {"Item Name":"Dawn Burger Bun (2 pcs pack)","Unit":"Pcs","Opening Stock":10.0,"Purchased":20.0,"Closing Stock":22.0,"Min Alert":5.0},
        {"Item Name":"Arfa Yellow Cheese (2kg pack)","Unit":"Pcs","Opening Stock":4.0,"Purchased":3.0,"Closing Stock":5.0,"Min Alert":2.0},
        {"Item Name":"Karachi Fajita Topping","Unit":"Pcs","Opening Stock":6.0,"Purchased":4.0,"Closing Stock":7.0,"Min Alert":3.0},
    ]).to_csv(STOCK_FILE,index=False)

stock = pd.read_csv(STOCK_FILE)
for col in ["Opening Stock","Purchased","Closing Stock","Min Alert"]:
    if col not in stock.columns:
        stock[col] = 0.0
    stock[col] = pd.to_numeric(stock[col], errors="coerce").fillna(0.0)

sales = load_csv(SALES_FILE, ["Date","Invoice","Item","Qty","Amount","Payment"])
expenses = load_csv(EXPENSE_FILE, ["Date","Category","Description","Amount"])
purchases = load_csv(PURCHASE_FILE, ["Invoice","Date","Item","Qty","Amount"])

# ----------------------------- Sidebar ---------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:8px 0 18px">
        <div style="font-size:42px">🍕</div>
        <div style="font-size:20px;font-weight:800;color:#f8fafc">CHEESY DELIGHTS</div>
        <div style="font-size:11px;color:#64748b;letter-spacing:1px">RESTAURANT MANAGEMENT OS</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("MAIN MENU", [
        "📊 Dashboard",
        "💰 Sales",
        "📦 Inventory",
        "🛒 Purchases",
        "🌙 Daily Closing",
        "📈 Reports",
        "💸 Expenses",
    ], label_visibility="visible")
    st.markdown("---")
    st.caption("Satyana Road Branch")
    st.caption(f"System date: {date.today().strftime('%d %b %Y')}")

# ----------------------------- Metrics ---------------------
today = str(date.today())
today_sales = float(sales.loc[sales["Date"].astype(str)==today, "Amount"].sum()) if not sales.empty else 0
month_sales = float(sales.loc[sales["Date"].astype(str).str[:7]==today[:7], "Amount"].sum()) if not sales.empty else 0
purchase_total = float(purchases["Amount"].sum()) if not purchases.empty and "Amount" in purchases else 0
expense_total = float(expenses["Amount"].sum()) if not expenses.empty else 0
low_count = int((stock["Closing Stock"] <= stock["Min Alert"]).sum())
stock_value = float((stock["Closing Stock"]).sum())
profit = month_sales - expense_total

# =========================================================
# DASHBOARD
# =========================================================
if page == "📊 Dashboard":
    st.markdown("""
    <div class="hero">
      <div class="hero-title">Good afternoon 👋</div>
      <div class="hero-sub">Here is your restaurant's live operational overview.</div>
    </div>
    """, unsafe_allow_html=True)

    c = st.columns(4)
    vals = [
        ("TODAY'S SALES", f"Rs. {today_sales:,.0f}", "Live sales recorded today"),
        ("MONTHLY SALES", f"Rs. {month_sales:,.0f}", "Current month revenue"),
        ("STOCK ITEMS", f"{len(stock):,}", "Active inventory items"),
        ("LOW STOCK", f"{low_count}", "Items needing attention"),
    ]
    for col,(label,val,note) in zip(c,vals):
        col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div><div class="kpi-note">{note}</div></div>',unsafe_allow_html=True)

    left,right = st.columns([1.6,1])
    with left:
        st.markdown('<div class="section">📦 Inventory Health</div>',unsafe_allow_html=True)
        with st.container(border=True):
            show = stock.copy()
            show["Status"] = show.apply(lambda r: "⚠️ Reorder" if r["Closing Stock"] <= r["Min Alert"] else "✓ Healthy",axis=1)
            st.dataframe(
                show[["Item Name","Unit","Closing Stock","Min Alert","Status"]],
                use_container_width=True, hide_index=True,
                column_config={"Closing Stock":st.column_config.NumberColumn("Current Stock",format="%.1f")}
            )
    with right:
        st.markdown('<div class="section">📈 Financial Snapshot</div>',unsafe_allow_html=True)
        with st.container(border=True):
            st.metric("Monthly Sales",f"Rs. {month_sales:,.0f}")
            st.metric("Purchases",f"Rs. {purchase_total:,.0f}")
            st.metric("Expenses",f"Rs. {expense_total:,.0f}")
            st.metric("Estimated Net",f"Rs. {profit:,.0f}")

    st.markdown('<div class="section">⚡ Quick Actions</div>',unsafe_allow_html=True)
    q = st.columns(4)
    q[0].info("💰 Record sales from the Sales menu.")
    q[1].info("📦 Update stock in Inventory.")
    q[2].info("🛒 Add vendor purchases.")
    q[3].warning(f"⚠️ {low_count} low-stock item(s).")

# =========================================================
# SALES
# =========================================================
elif page == "💰 Sales":
    st.markdown('<div class="hero"><div class="hero-title">💰 Sales & POS</div><div class="hero-sub">Record revenue and keep your sales history organized.</div></div>',unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.metric("Today's Sales",f"Rs. {today_sales:,.0f}")
    b.metric("This Month",f"Rs. {month_sales:,.0f}")
    b.metric("Transactions",len(sales))
    c.metric("Average Sale",f"Rs. {(month_sales/max(len(sales),1)):,.0f}")

    with st.form("sales_form", clear_on_submit=True):
        st.subheader("➕ New Sale")
        x1,x2,x3 = st.columns(3)
        with x1: invoice = st.text_input("Invoice / Order #",value=f"ORD-{datetime.now().strftime('%H%M%S')}")
        with x2: item = st.selectbox("Item",stock["Item Name"].tolist())
        with x3: qty = st.number_input("Quantity",min_value=1.0,step=1.0)
        x4,x5 = st.columns(2)
        with x4: amount = st.number_input("Total Amount (Rs.)",min_value=0.0,step=50.0)
        with x5: payment = st.selectbox("Payment",["Cash","Card","Online"])
        if st.form_submit_button("💾 Save Sale",use_container_width=True):
            new = pd.DataFrame([{"Date":today,"Invoice":invoice,"Item":item,"Qty":qty,"Amount":amount,"Payment":payment}])
            save_csv(pd.concat([sales,new],ignore_index=True),SALES_FILE)
            st.success("Sale saved successfully.")
            st.rerun()

    st.markdown('<div class="section">Recent Sales</div>',unsafe_allow_html=True)
    st.dataframe(sales.tail(15).iloc[::-1],use_container_width=True,hide_index=True)

# =========================================================
# INVENTORY
# =========================================================
elif page == "📦 Inventory":
    st.markdown('<div class="hero"><div class="hero-title">📦 Inventory Control</div><div class="hero-sub">Monitor stock levels, minimum thresholds and daily movement.</div></div>',unsafe_allow_html=True)

    search = st.text_input("🔎 Search inventory",placeholder="Type an item name...")
    view = stock[stock["Item Name"].str.contains(search,case=False,na=False)] if search else stock

    cols = st.columns(3)
    for idx,row in view.iterrows():
        with cols[list(view.index).index(idx)%3]:
            low = row["Closing Stock"] <= row["Min Alert"]
            status = '<span class="pill warn">⚠ REORDER</span>' if low else '<span class="pill good">✓ HEALTHY</span>'
            st.markdown(f"""
            <div class="item-card">
                <div class="item-name">{row['Item Name']}</div>
                <div class="item-stock">{row['Closing Stock']:,.1f} <span style="font-size:12px;color:#94a3b8">{row['Unit']}</span></div>
                <div style="color:#64748b;font-size:11px;margin-bottom:9px">Minimum: {row['Min Alert']:,.1f} · Purchased: {row['Purchased']:,.1f}</div>
                {status}
            </div>""",unsafe_allow_html=True)

    st.markdown('<div class="section">➕ Add New Item</div>',unsafe_allow_html=True)
    with st.form("add_item", clear_on_submit=True):
        a,b,c = st.columns(3)
        with a: new_name = st.text_input("Item Name", placeholder="e.g. Mozzarella Cheese")
        with b: new_category = st.text_input("Category", placeholder="e.g. Dairy")
        with c: new_unit = st.selectbox("Unit", ["Pcs","Kg","Gram","Litre","Pack","Bottle","Box"])
        d,e,f = st.columns(3)
        with d: opening = st.number_input("Opening Stock", min_value=0.0, step=0.5)
        with e: purchase_price = st.number_input("Purchase Price (Rs.)", min_value=0.0, step=10.0)
        with f: min_alert = st.number_input("Minimum Stock Alert", min_value=0.0, step=0.5, value=2.0)
        if st.form_submit_button("➕ Add Item", use_container_width=True):
            if not new_name.strip():
                st.error("Item name is required.")
            elif new_name.strip().lower() in stock["Item Name"].astype(str).str.lower().tolist():
                st.warning("This item already exists.")
            else:
                new_row = pd.DataFrame([{
                    "Item Name":new_name.strip(),"Category":new_category.strip(),
                    "Unit":new_unit,"Opening Stock":opening,"Purchased":0.0,
                    "Closing Stock":opening,"Min Alert":min_alert,
                    "Purchase Price":purchase_price
                }])
                save_csv(pd.concat([stock,new_row],ignore_index=True), STOCK_FILE)
                st.success(f"✅ {new_name} added successfully.")
                st.rerun()

    st.markdown('<div class="section">✏️ Edit / 🗑️ Delete Item</div>',unsafe_allow_html=True)
    if not stock.empty:
        selected = st.selectbox("Select Item", stock["Item Name"].tolist(), key="manage_item")
        row_index = stock.index[stock["Item Name"] == selected][0]
        current = stock.loc[row_index]

        with st.form("edit_item"):
            a,b,c = st.columns(3)
            with a: edit_name = st.text_input("Item Name", value=str(current["Item Name"]))
            with b: edit_category = st.text_input("Category", value=str(current.get("Category","")))
            with c: edit_unit = st.selectbox("Unit", ["Pcs","Kg","Gram","Litre","Pack","Bottle","Box"],
                                              index=(["Pcs","Kg","Gram","Litre","Pack","Bottle","Box"].index(str(current["Unit"]))
                                                     if str(current["Unit"]) in ["Pcs","Kg","Gram","Litre","Pack","Bottle","Box"] else 0))
            a,b,c = st.columns(3)
            with a: edit_stock = st.number_input("Current Stock", min_value=0.0, value=float(current["Closing Stock"]), step=0.5)
            with b: edit_min = st.number_input("Minimum Alert", min_value=0.0, value=float(current["Min Alert"]), step=0.5)
            with c: edit_price = st.number_input("Purchase Price", min_value=0.0, value=float(current.get("Purchase Price",0)), step=10.0)
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                stock.loc[row_index,"Item Name"] = edit_name.strip()
                stock.loc[row_index,"Category"] = edit_category.strip()
                stock.loc[row_index,"Unit"] = edit_unit
                stock.loc[row_index,"Closing Stock"] = edit_stock
                stock.loc[row_index,"Min Alert"] = edit_min
                if "Purchase Price" not in stock.columns:
                    stock["Purchase Price"] = 0.0
                stock.loc[row_index,"Purchase Price"] = edit_price
                save_csv(stock, STOCK_FILE)
                st.success("✅ Item updated.")
                st.rerun()

        if st.button("🗑️ Delete Selected Item", type="secondary", use_container_width=True):
            stock = stock[stock["Item Name"] != selected].copy()
            save_csv(stock, STOCK_FILE)
            st.success(f"🗑️ {selected} deleted.")
            st.rerun()

# =========================================================
# PURCHASES
# =========================================================
elif page == "🛒 Purchases":
    st.markdown('<div class="hero"><div class="hero-title">🛒 Vendor Purchases</div><div class="hero-sub">Log invoices and incoming stock in one place.</div></div>',unsafe_allow_html=True)
    with st.form("purchase_form",clear_on_submit=True):
        p1,p2 = st.columns(2)
        with p1: inv = st.text_input("Invoice Number")
        with p2: pdate = st.date_input("Purchase Date",date.today())
        p3,p4,p5 = st.columns(3)
        with p3: item = st.selectbox("Item",stock["Item Name"].tolist())
        with p4: qty = st.number_input("Quantity",min_value=0.1,step=1.0)
        with p5: amount = st.number_input("Invoice Amount (Rs.)",min_value=0.0,step=100.0)
        if st.form_submit_button("➕ Add Purchase"):
            stock.loc[stock["Item Name"]==item,"Purchased"] += qty
            stock.loc[stock["Item Name"]==item,"Closing Stock"] += qty
            save_csv(stock,STOCK_FILE)
            row = pd.DataFrame([{"Invoice":inv,"Date":str(pdate),"Item":item,"Qty":qty,"Amount":amount}])
            save_csv(pd.concat([purchases,row],ignore_index=True),PURCHASE_FILE)
            st.success("Purchase and stock added.")
            st.rerun()
    st.markdown('<div class="section">Purchase History</div>',unsafe_allow_html=True)
    st.dataframe(purchases.tail(20).iloc[::-1],use_container_width=True,hide_index=True)

# =========================================================
# DAILY CLOSING
# =========================================================
elif page == "🌙 Daily Closing":
    st.markdown('<div class="hero"><div class="hero-title">🌙 Daily Closing</div><div class="hero-sub">Enter the physical closing count before ending the shift.</div></div>',unsafe_allow_html=True)
    closing_date = st.date_input("Closing Date",date.today())
    updated = {}
    for idx,row in stock.iterrows():
        a,b = st.columns([2,1])
        with a:
            st.markdown(f"**{row['Item Name']}**")
            st.caption(f"Opening: {row['Opening Stock']} · Purchased: {row['Purchased']}")
        with b:
            updated[row["Item Name"]] = st.number_input("Closing stock",min_value=0.0,value=float(row["Closing Stock"]),step=0.5,key=f"close_{idx}")
    if st.button("🔒 Save & Lock Closing",use_container_width=True):
        for item,val in updated.items():
            stock.loc[stock["Item Name"]==item,"Closing Stock"] = val
        stock["Total Available"] = stock["Opening Stock"] + stock["Purchased"]
        stock["Total Used Today"] = stock["Total Available"] - stock["Closing Stock"]
        save_csv(stock,STOCK_FILE)
        archive = stock.copy()
        archive["Date"] = str(closing_date)
        archive["Year"] = closing_date.year
        archive["Month"] = closing_date.strftime("%B")
        hist = load_csv(HISTORY_FILE, list(archive.columns))
        if not hist.empty and "Date" in hist.columns:
            hist = hist[hist["Date"].astype(str)!=str(closing_date)]
        save_csv(pd.concat([hist,archive],ignore_index=True),HISTORY_FILE)
        st.success(f"Closing for {closing_date} saved.")
        st.rerun()

# =========================================================
# REPORTS
# =========================================================
elif page == "📈 Reports":
    st.markdown('<div class="hero"><div class="hero-title">📈 Reports & Analytics</div><div class="hero-sub">Download operational and financial records for management.</div></div>',unsafe_allow_html=True)
    t1,t2,t3,t4 = st.tabs(["Sales","Purchases","Inventory","Expenses"])
    with t1:
        st.dataframe(sales,use_container_width=True,hide_index=True)
        st.download_button("📥 Download Sales CSV",sales.to_csv(index=False),"sales_report.csv","text/csv")
    with t2:
        st.dataframe(purchases,use_container_width=True,hide_index=True)
        st.download_button("📥 Download Purchases CSV",purchases.to_csv(index=False),"purchases_report.csv","text/csv")
    with t3:
        st.dataframe(stock,use_container_width=True,hide_index=True)
        st.download_button("📥 Download Inventory CSV",stock.to_csv(index=False),"inventory_report.csv","text/csv")
    with t4:
        st.dataframe(expenses,use_container_width=True,hide_index=True)
        st.download_button("📥 Download Expenses CSV",expenses.to_csv(index=False),"expenses_report.csv","text/csv")

# =========================================================
# EXPENSES
# =========================================================
else:
    st.markdown('<div class="hero"><div class="hero-title">💸 Expenses</div><div class="hero-sub">Track operating costs to understand real profitability.</div></div>',unsafe_allow_html=True)
    with st.form("expense_form",clear_on_submit=True):
        a,b = st.columns(2)
        with a: edate = st.date_input("Date",date.today())
        with b: category = st.selectbox("Category",["Utilities","Salary","Transport","Maintenance","Marketing","Other"])
        desc = st.text_input("Description")
        amount = st.number_input("Amount (Rs.)",min_value=0.0,step=100.0)
        if st.form_submit_button("💾 Save Expense"):
            row = pd.DataFrame([{"Date":str(edate),"Category":category,"Description":desc,"Amount":amount}])
            save_csv(pd.concat([expenses,row],ignore_index=True),EXPENSE_FILE)
            st.success("Expense saved.")
            st.rerun()
    st.markdown('<div class="section">Expense History</div>',unsafe_allow_html=True)
    st.dataframe(expenses.tail(20).iloc[::-1],use_container_width=True,hide_index=True)
