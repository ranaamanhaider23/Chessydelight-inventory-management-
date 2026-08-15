import streamlit as st
import pandas as pd
from datetime import date
import os

# ==========================================
# 🎨 EXECUTIVE SAAS DASHBOARD THEME (CSS)
# ==========================================
st.set_page_config(page_title="Cheesy Delights | Inventory OS", layout="wide", page_icon="🍕")

st.markdown("""
    <style>
        .stApp { background-color: #0B0F19; color: #E2E8F0; font-family: 'Inter', sans-serif; }
        
        .custom-card {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        }
        
        .card-header { font-size: 13px; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .card-val { font-size: 26px; font-weight: 800; color: #38BDF8; margin: 8px 0; }
        
        .badge-green { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid #059669; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
        .badge-red { background: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid #DC2626; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
        
        .stButton>button {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            padding: 10px 20px !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        }

        section[data-testid="stSidebar"] { background-color: #030712; border-right: 1px solid #1E293B; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📁 DATA HANDLING
# ==========================================
TODAY_STOCK_FILE = "daily_closing_stock.csv"
HISTORY_FILE = "inventory_history_archive.csv"
PURCHASE_FILE = "purchases_log.csv"

if not os.path.exists(TODAY_STOCK_FILE):
    df_init = pd.DataFrame([
        {"Item Name": "Dawn Burger Bun (2 pcs pack)", "Unit": "Pcs", "Opening Stock": 0.0, "Purchased": 2.0, "Closing Stock": 1.0, "Min Alert": 2.0},
        {"Item Name": "Arfa Yellow Cheese (2kg pack)", "Unit": "Pcs", "Opening Stock": 0.0, "Purchased": 1.0, "Closing Stock": 0.5, "Min Alert": 1.0},
        {"Item Name": "Karachi Fajita Topping", "Unit": "Pcs", "Opening Stock": 0.0, "Purchased": 2.0, "Closing Stock": 1.0, "Min Alert": 1.5}
    ])
    df_init.to_csv(TODAY_STOCK_FILE, index=False)

stock_df = pd.read_csv(TODAY_STOCK_FILE)

for col in ["Opening Stock", "Purchased", "Closing Stock"]:
    stock_df[col] = pd.to_numeric(stock_df[col], errors='coerce').fillna(0.0)

# ==========================================
# 🧭 SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color: #F59E0B; text-align: center; margin-bottom: 0;'>🍕 Cheesy Delights</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; text-align: center; font-size:12px; margin-top: 0;'>Satyana Road Branch</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    nav = st.radio("OPERATIONS", [
        "📊 Live Dashboard",
        "🌙 End-of-Day Closing", 
        "📅 History & Reports", 
        "🧾 Add Vendor Invoice"
    ])

# ==========================================
# MODULE 1: LIVE DASHBOARD
# ==========================================
if nav == "📊 Live Dashboard":
    st.markdown("<h2 style='color: #38BDF8;'>📊 Real-time Stock Overview</h2>", unsafe_allow_html=True)
    st.caption("Live status of all kitchen inventory items:")
    
    cols = st.columns(3)
    for idx, row in stock_df.iterrows():
        c = cols[idx % 3]
        total_avail = row["Opening Stock"] + row["Purchased"]
        used = total_avail - row["Closing Stock"]
        is_low = row["Closing Stock"] <= row.get("Min Alert", 1.0)
        
        badge_html = f'<span class="badge-red">⚠️ REORDER NEEDED</span>' if is_low else f'<span class="badge-green">✅ STOCK SUFFICIENT</span>'
        
        c.markdown(f"""
            <div class="custom-card">
                <div class="card-header">{row['Item Name']}</div>
                <div class="card-val">{row['Closing Stock']} <span style="font-size: 14px; color: #94A3B8;">{row['Unit']}</span></div>
                <div style="font-size: 12px; color: #94A3B8; margin-bottom: 10px;">Used Today: <b>{used:.1f} {row['Unit']}</b></div>
                {badge_html}
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# MODULE 2: END-OF-DAY CLOSING
# ==========================================
elif nav == "🌙 End-of-Day Closing":
    st.markdown("<h2 style='color: #38BDF8;'>🌙 Nightly Closing Sheet</h2>", unsafe_allow_html=True)
    st.caption("Raat ko physical count check karke numbers enter karein:")

    closing_date = st.date_input("Closing Date", date.today())
    st.markdown("---")

    updated_closing = {}
    st.subheader("📝 Closing Quantities Enter Karein:")
    
    for idx, row in stock_df.iterrows():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"**{row['Item Name']}** `({row['Unit']})`")
            st.caption(f"Opening: {row['Opening Stock']} | Purchased Today: {row['Purchased']}")
        with c2:
            val = st.number_input(
                f"Closing ({row['Unit']})",
                min_value=0.0,
                step=0.5,
                value=float(row["Closing Stock"]),
                key=f"close_{idx}"
            )
            updated_closing[row['Item Name']] = val
        st.markdown("<hr style='border-color: #1E293B; margin: 8px 0;'>", unsafe_allow_html=True)

    if st.button("💾 Save & Lock Today's Closing"):
        for item, close_val in updated_closing.items():
            stock_df.loc[stock_df["Item Name"] == item, "Closing Stock"] = close_val
            
        stock_df["Total Available"] = stock_df["Opening Stock"] + stock_df["Purchased"]
        stock_df["Total Used Today"] = stock_df["Total Available"] - stock_df["Closing Stock"]
        stock_df.to_csv(TODAY_STOCK_FILE, index=False)
        
        archive_entry = stock_df.copy()
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
        st.success(f"✅ Daily Closing for {closing_date} Saved Successfully!")
        st.rerun()

# ==========================================
# MODULE 3: HISTORY & REPORTS
# ==========================================
elif nav == "📅 History & Reports":
    st.markdown("<h2 style='color: #38BDF8;'>📅 Monthly & Yearly History</h2>", unsafe_allow_html=True)
    
    if os.path.exists(HISTORY_FILE):
        hist_df = pd.read_csv(HISTORY_FILE)
        if not hist_df.empty:
            c1, c2 = st.columns(2)
            with c1:
                selected_year = st.selectbox("Year Select Karein", sorted(hist_df["Year"].unique(), reverse=True))
            with c2:
                available_months = hist_df[hist_df["Year"] == selected_year]["Month"].unique()
                selected_month = st.selectbox("Month Select Karein", available_months)

            filtered_df = hist_df[(hist_df["Year"] == selected_year) & (hist_df["Month"] == selected_month)]
            
            st.markdown("---")
            st.subheader(f"📊 Summary: {selected_month} {selected_year}")
            
            summary = filtered_df.groupby("Item Name").agg({
                "Purchased": "sum",
                "Total Used Today": "sum",
                "Unit": "first"
            }).reset_index()
            
            st.dataframe(summary, use_container_width=True)

            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Excel / CSV Download Karein",
                data=csv_data,
                file_name=f"Report_{selected_month}_{selected_year}.csv",
                mime="text/csv"
            )
        else:
            st.info("Pehle Daily Closing Save Karein!")
    else:
        st.info("Koi history record nahi mila.")

# ==========================================
# MODULE 4: VENDOR INVOICE LOG
# ==========================================
else:
    st.markdown("<h2 style='color: #38BDF8;'>🧾 Vendor Invoice Log</h2>", unsafe_allow_html=True)
    
    with st.form("inv_form"):
        inv_no = st.text_input("Invoice Number", value="608547")
        item_selected = st.selectbox("Item Select Karein", stock_df["Item Name"].tolist())
        qty = st.number_input("Quantity Received", min_value=1.0, step=1.0, value=1.0)
        rate = st.number_input("Rate per Unit (Rs.)", min_value=0.0, step=10.0, value=100.0)
        
        if st.form_submit_button("➕ Add Purchase Stock"):
            stock_df.loc[stock_df["Item Name"] == item_selected, "Purchased"] += qty
            stock_df.to_csv(TODAY_STOCK_FILE, index=False)
            
            new_p = pd.DataFrame([{"Invoice": inv_no, "Date": str(date.today()), "Item": item_selected, "Qty": qty, "Amount": qty*rate}])
            hist = pd.read_csv(PURCHASE_FILE) if os.path.exists(PURCHASE_FILE) else pd.DataFrame()
            pd.concat([hist, new_p], ignore_index=True).to_csv(PURCHASE_FILE, index=False)
            
            st.success(f"✅ Added {qty} {item_selected} to Purchased Stock!")
            st.rerun()
