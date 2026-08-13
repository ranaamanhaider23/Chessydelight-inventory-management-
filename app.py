import streamlit as st
import pandas as pd
from datetime import date
import os

# ==========================================
# 🎨 UI & THEME SETUP
# ==========================================
st.set_page_config(page_title="Cheesy Delights | Inventory OS", layout="wide", page_icon="🍕")

st.markdown("""
    <style>
        .stApp { background-color: #0F172A; color: #F8FAFC; }
        div[data-testid="stMetric"] {
            background: #1E293B;
            border: 1px solid #334155;
            padding: 16px;
            border-radius: 12px;
        }
        div[data-testid="stMetric"] label { color: #94A3B8 !important; font-size: 13px !important; }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #38BDF8 !important; font-size: 22px !important; }
        .stButton>button {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            color: white; border: none; border-radius: 8px; font-weight: bold; width: 100%;
        }
        section[data-testid="stSidebar"] { background-color: #020617; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📁 FILE SYSTEM SETUP
# ==========================================
TODAY_STOCK_FILE = "daily_closing_stock.csv"
HISTORY_FILE = "inventory_history_archive.csv"
PURCHASE_FILE = "purchases_log.csv"

if not os.path.exists(TODAY_STOCK_FILE):
    df_init = pd.DataFrame([
        {"Item Name": "Dawn Burger Bun (2 pcs pack)", "Unit": "Pcs", "Opening Stock": 0.0, "Purchased": 2.0, "Closing Stock": 1.0},
        {"Item Name": "Arfa Yellow Cheese (2kg pack)", "Unit": "Pcs", "Opening Stock": 0.0, "Purchased": 1.0, "Closing Stock": 0.5},
        {"Item Name": "Karachi Fajita Topping", "Unit": "Pcs", "Opening Stock": 0.0, "Purchased": 2.0, "Closing Stock": 1.0}
    ])
    df_init.to_csv(TODAY_STOCK_FILE, index=False)

stock_df = pd.read_csv(TODAY_STOCK_FILE)

# ==========================================
# 🧭 SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color: #F59E0B; text-align: center;'>🍕 Cheesy Delights</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; text-align: center; font-size:12px;'>Satyana Road Branch</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    nav = st.radio("MENU", [
        "🌙 Daily Closing Sheet", 
        "📅 Monthly & Yearly History", 
        "🧾 Invoice Log", 
        "🤖 AI Stock Assistant"
    ])

# ==========================================
# MODULE 1: DAILY CLOSING SHEET
# ==========================================
if nav == "🌙 Daily Closing Sheet":
    st.markdown("<h2 style='color: #38BDF8;'>🌙 Daily Closing Sheet</h2>", unsafe_allow_html=True)
    closing_date = st.date_input("Closing Date", date.today())

    stock_df["Total Available"] = stock_df["Opening Stock"] + stock_df["Purchased"]
    stock_df["Total Used Today"] = stock_df["Total Available"] - stock_df["Closing Stock"]

    st.markdown("---")
    st.subheader("📝 Enter Closing Quantities")
    edited_df = st.data_editor(
        stock_df[["Item Name", "Unit", "Opening Stock", "Purchased", "Closing Stock"]],
        num_rows="dynamic",
        use_container_width=True,
        key="editor"
    )

    if st.button("💾 Save Daily Sheet & Archive History", type="primary"):
        edited_df["Total Available"] = edited_df["Opening Stock"] + edited_df["Purchased"]
        edited_df["Total Used Today"] = edited_df["Total Available"] - edited_df["Closing Stock"]
        edited_df.to_csv(TODAY_STOCK_FILE, index=False)
        
        # Monthly / Yearly History Archive
        archive_entry = edited_df.copy()
        archive_entry["Date"] = str(closing_date)
        archive_entry["Year"] = closing_date.year
        archive_entry["Month"] = closing_date.strftime("%B")
        
        if os.path.exists(HISTORY_FILE):
            hist_existing = pd.read_csv(HISTORY_FILE)
            hist_existing = hist_existing[hist_existing["Date"] != str(closing_date)]
            final_hist = pd.concat([hist_existing, archive_entry], ignore_index=True)
        else:
            final_hist = archive_entry
            
        final_hist.to_csv(HISTORY_FILE, index=False)
        st.success(f"✅ Daily Record Saved for {closing_date} into Permanent History Database!")
        st.rerun()

    st.markdown("---")
    st.subheader("📊 Aaj Ki Total Usage Summary")
    cols = st.columns(3)
    for idx, row in edited_df.iterrows():
        c = cols[idx % 3]
        used = (row["Opening Stock"] + row["Purchased"]) - row["Closing Stock"]
        c.metric(
            label=row["Item Name"],
            value=f"{row['Closing Stock']} {row['Unit']} Left",
            delta=f"-{used} {row['Unit']} Used",
            delta_color="inverse"
        )

# ==========================================
# MODULE 2: MONTHLY & YEARLY HISTORY
# ==========================================
elif nav == "📅 Monthly & Yearly History":
    st.markdown("<h2 style='color: #38BDF8;'>📅 Monthly & Yearly Inventory Reports</h2>", unsafe_allow_html=True)
    
    if os.path.exists(HISTORY_FILE):
        hist_df = pd.read_csv(HISTORY_FILE)
        
        if not hist_df.empty:
            c1, c2 = st.columns(2)
            with c1:
                selected_year = st.selectbox("Select Year", sorted(hist_df["Year"].unique(), reverse=True))
            with c2:
                available_months = hist_df[hist_df["Year"] == selected_year]["Month"].unique()
                selected_month = st.selectbox("Select Month", available_months)

            filtered_df = hist_df[(hist_df["Year"] == selected_year) & (hist_df["Month"] == selected_month)]
            
            st.markdown("---")
            st.subheader(f"📊 Summary for {selected_month} {selected_year}")
            
            monthly_summary = filtered_df.groupby("Item Name").agg({
                "Purchased": "sum",
                "Total Used Today": "sum",
                "Unit": "first"
            }).reset_index()
            monthly_summary.rename(columns={"Total Used Today": "Total Used In Month"}, inplace=True)

            st.dataframe(monthly_summary, use_container_width=True)

            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label=f"📥 Download Full {selected_month} Report (CSV)",
                data=csv_data,
                file_name=f"Inventory_Report_{selected_month}_{selected_year}.csv",
                mime="text/csv"
            )

            st.markdown("---")
            st.subheader("🗓️ Day-by-Day Historical Log")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("History file is empty. Save closing sheets to generate reports!")
    else:
        st.info("Abhi tak koi history save nahi hui. Pehle 'Daily Closing Sheet' save karein!")

# ==========================================
# MODULE 3: INVOICE LOG
# ==========================================
elif nav == "🧾 Invoice Log":
    st.markdown("<h2 style='color: #38BDF8;'>🧾 Vendor Invoice Record</h2>", unsafe_allow_html=True)
    
    with st.form("inv_form"):
        inv_no = st.text_input("Invoice Number", value="608547")
        item_selected = st.selectbox("Select Item", stock_df["Item Name"].tolist())
        qty = st.number_input("Quantity Received", min_value=1.0, step=1.0, value=1.0)
        rate = st.number_input("Rate (Rs.)", min_value=0.0, step=10.0, value=100.0)
        
        if st.form_submit_button("➕ Add Invoice Stock"):
            stock_df.loc[stock_df["Item Name"] == item_selected, "Purchased"] += qty
            stock_df.to_csv(TODAY_STOCK_FILE, index=False)
            
            new_p = pd.DataFrame([{"Invoice": inv_no, "Date": str(date.today()), "Item": item_selected, "Qty": qty, "Amount": qty*rate}])
            hist = pd.read_csv(PURCHASE_FILE) if os.path.exists(PURCHASE_FILE) else pd.DataFrame()
            pd.concat([hist, new_p], ignore_index=True).to_csv(PURCHASE_FILE, index=False)
            
            st.success(f"✅ Added {qty} {item_selected} into Today's Purchased Stock!")
            st.rerun()

# ==========================================
# MODULE 4: AI ASSISTANT
# ==========================================
else:
    st.markdown("<h2 style='color: #38BDF8;'>🤖 AI Stock Manager</h2>", unsafe_allow_html=True)
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Salam! Main Cheesy Delights ka AI Manager hoon. Daily, Monthly ya Yearly stock usage ke baare mein poochein!"}
        ]

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if q := st.chat_input("Poochein (e.g., 'Is mahine kitni cheese use hui?'):"):
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.chat_message("user"): st.markdown(q)

        q_lower = q.lower()
        res = ""

        if os.path.exists(HISTORY_FILE):
            h_df = pd.read_csv(HISTORY_FILE)
            if not h_df.empty and any(w in q_lower for w in ["mahina", "month", "used", "cheese", "total"]):
                summary = h_df.groupby("Item Name")["Total Used Today"].sum().reset_index()
                info = "\n".join([f"- **{r['Item Name']}**: `{r['Total Used Today']}` Total Used" for _, r in summary.iterrows()])
                res = f"📊 **Over-All Recorded Consumption History:**\n\n{info}"
            else:
                res = "Main aapke daily, monthly aur yearly stock archives se connected hoon. Aap kisi bhi mahine ya item ki khapat pooch sakte hain!"
        else:
            res = "Abhi tak koi history file save nahi hui hai. Closing sheet save karein taake reports ban sakein."

        with st.chat_message("assistant"): st.markdown(res)
        st.session_state.chat_history.append({"role": "assistant", "content": res})
