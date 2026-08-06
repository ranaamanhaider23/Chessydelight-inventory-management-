# ==========================================
# SCREEN 4: 📈 PROFIT & LOSS REPORTS (DAILY, MONTHLY & YEARLY)
# ==========================================
elif nav_option == "📈 Profit & Loss Reports":
    st.title("📈 Profit & Loss Financial Reports")
    
    if os.path.exists(INVENTORY_FILE):
        inv_records = pd.read_csv(INVENTORY_FILE)
        prices_df = st.session_state.prices_data
        
        # Merge inventory with prices
        merged_rep = pd.merge(inv_records, prices_df, on="Item Name", how="left", suffixes=('', '_m')).fillna(0)
        
        p_price_col = "Purchase Price" if "Purchase Price" in merged_rep.columns else "Purchase Price_m"
        s_price_col = "Selling Price" if "Selling Price" in merged_rep.columns else "Selling Price_m"
        
        # Profit / Loss Logic
        merged_rep["Revenue"] = merged_rep["Sale"] * merged_rep[s_price_col]
        merged_rep["Cost"] = merged_rep["Sale"] * merged_rep[p_price_col]
        merged_rep["Gross Profit"] = merged_rep["Revenue"] - merged_rep["Cost"]
        
        merged_rep["Date_Parsed"] = pd.to_datetime(merged_rep["Date"], errors='coerce')
        merged_rep["Year"] = merged_rep["Date_Parsed"].dt.year
        merged_rep["Month"] = merged_rep["Date_Parsed"].dt.strftime("%Y-%m")
        
        # ADDED "📅 Daily Report" TAB HERE 👇
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
                
        # 4. DAILY RECORD DELETE SECTION
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
