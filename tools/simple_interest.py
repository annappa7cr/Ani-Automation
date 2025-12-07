import streamlit as st
import datetime

def run_tool():
    """
    Advanced Simple Interest Calculator with 'Quick Select' and 'Manual' modes,
    plus Exact Date calculation.
    """
    st.subheader("💰 Professional Interest Calculator")
    
    # --- 1. MODE SELECTION (Tabs for better UI) ---
    mode = st.radio("Choose Input Mode:", ["✍️ Manual Entry", "🎯 Quick Select"], horizontal=True)
    st.divider()

    principal = None
    rate = None
    time_years = 0.0
    is_date_mode = False
    
    # --- 2. INPUT LOGIC BASED ON MODE ---
    
    if mode == "✍️ Manual Entry":
        col1, col2 = st.columns(2)
        
        with col1:
            # WATERMARK: We use value=None and placeholder="..."
            principal = st.number_input(
                "Principal Amount (₹)", 
                min_value=0.0, 
                value=None, 
                placeholder="Enter amount (e.g. 50000)..."
            )
            
            rate = st.number_input(
                "Annual Interest Rate (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=None, 
                placeholder="Enter rate (e.g. 12)..."
            )

        with col2:
            # Sub-selection for Time: Yearly vs Exact Date
            time_type = st.selectbox("Time Duration Type", ["Yearly/Monthly Period", "Exact Date Range 📅"])
            
            if time_type == "Yearly/Monthly Period":
                t_val = st.number_input(
                    "Time Duration", 
                    min_value=0.0, 
                    value=None, 
                    placeholder="Enter duration..."
                )
                t_unit = st.selectbox("Unit", ["Years", "Months"])
                
                # Convert to Years for calculation
                if t_val is not None:
                    if t_unit == "Years":
                        time_years = t_val
                    else:
                        time_years = t_val / 12.0
                        
            else: # Exact Date Range
                is_date_mode = True
                d_col_a, d_col_b = st.columns(2)
                with d_col_a:
                    start_date = st.date_input("Start Date", datetime.date.today())
                with d_col_b:
                    end_date = st.date_input("End Date", datetime.date.today())
                
                if end_date < start_date:
                    st.error("End Date must be after Start Date!")
                else:
                    days_diff = (end_date - start_date).days
                    st.caption(f"🗓️ Duration: **{days_diff} days**")
                    time_years = days_diff / 365.0

    elif mode == "🎯 Quick Select":
        # Sliders and Presets for easy choosing
        col1, col2 = st.columns(2)
        with col1:
            principal = st.slider("Choose Principal (₹)", 1000, 1000000, 10000, step=1000)
            
        with col2:
            loan_type = st.selectbox("Choose Loan/Investment Type", 
                                     ["Custom", "Savings Account (3%)", "Fixed Deposit (6%)", "Car Loan (9%)", "Personal Loan (12%)", "Credit Card (36%)"])
            
            if loan_type == "Custom":
                rate = st.slider("Select Rate (%)", 0.0, 50.0, 10.0)
            else:
                # Extract number from string (e.g., "Car Loan (9%)" -> 9.0)
                rate = float(loan_type.split("(")[1].split("%")[0])
                st.info(f"Rate auto-set to **{rate}%**")

        time_years = st.slider("Time Period (Years)", 0.5, 30.0, 1.0, step=0.5)

    # --- 3. CALCULATION & PROFESSIONAL DISPLAY ---
    
    st.write("---")
    
    # Only show button if inputs are valid
    if st.button("Calculate Details 🚀", type="primary"):
        if principal is None or rate is None:
            st.error("⚠️ Please enter both Principal Amount and Rate to proceed.")
        else:
            # Core Calculation
            interest = (principal * rate * time_years) / 100
            total_amount = principal + interest
            
            # --- RESULTS SECTION ---
            st.success("✅ Calculation Complete")
            
            # 1. High-Level Metrics (The "Money" View)
            m1, m2, m3 = st.columns(3)
            m1.metric("Principal", f"₹ {principal:,.2f}")
            m2.metric("Total Interest", f"₹ {interest:,.2f}", delta="Extra Cost")
            m3.metric("Total Payable", f"₹ {total_amount:,.2f}")
            
            # 2. Detailed Breakdown Table
            st.markdown("### 📋 Breakdown Analysis")
            
            # Calculate breakdown metrics
            monthly_interest = (principal * rate) / 100 / 12
            daily_interest = (principal * rate) / 100 / 365
            
            with st.container(border=True):
                col_d1, col_d2 = st.columns(2)
                
                with col_d1:
                    st.markdown(f"""
                    * **Rate Applied:** {rate}% per annum
                    * **Time Calculated:** {time_years:.2f} years
                    * **Daily Interest Cost:** ₹ {daily_interest:,.2f}
                    """)
                    
                with col_d2:
                    st.markdown(f"""
                    * **Monthly Interest Cost:** ₹ {monthly_interest:,.2f}
                    * **Yearly Interest Cost:** ₹ {(monthly_interest * 12):,.2f}
                    """)
            
            # 3. Date Specific Note
            if is_date_mode:
                st.info(f"ℹ️ Calculation based on exact duration of **{(end_date - start_date).days} days**.")