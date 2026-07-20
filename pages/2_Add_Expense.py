"""Add/Edit/Delete Expense page with search and filters."""

import streamlit as st
from datetime import date, datetime
from auth import AuthManager
from expense import ExpenseManager, CATEGORIES, PAYMENT_MODES
from utils import apply_custom_css, format_currency


def render():
    AuthManager.require_auth()
    apply_custom_css(st.session_state.get("dark_mode", True))

    user_id = AuthManager.get_user_id()
    em = ExpenseManager(user_id)

    st.markdown('<p class="page-header">➕ Expense Management</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Add, edit, search and filter your expenses</p>',
        unsafe_allow_html=True,
    )

    tab_add, tab_manage = st.tabs(["➕ Add Expense", "📂 Manage Expenses"])

    with tab_add:
        with st.form("add_expense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                expense_date = st.date_input("Date", value=date.today())
                amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f")
                category = st.selectbox("Category", CATEGORIES)
            with col2:
                description = st.text_input("Description")
                payment_mode = st.selectbox("Payment Mode", PAYMENT_MODES)

            submitted = st.form_submit_button("Add Expense", type="primary", use_container_width=True)
            if submitted:
                success, msg = em.add_expense(expense_date, amount, category, description, payment_mode)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

    with tab_manage:
        st.subheader("🔍 Search & Filter")
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            search = st.text_input("Search", placeholder="Description or category...")
        with fcol2:
            filter_cat = st.selectbox("Category Filter", ["All"] + CATEGORIES, key="filter_cat")
        with fcol3:
            start_date = st.date_input("From", value=date.today().replace(day=1), key="start_d")
        with fcol4:
            end_date = st.date_input("To", value=date.today(), key="end_d")

        df = em.get_expenses_df(
            category=filter_cat,
            start_date=start_date,
            end_date=end_date,
            search=search if search else None,
        )

        if df.empty:
            st.info("No expenses found matching your filters.")
        else:
            st.caption(f"Showing {len(df)} expense(s) | Total: {format_currency(df['amount'].sum())}")

            for _, row in df.iterrows():
                with st.expander(
                    f"{row['date']} | {row['category']} | {format_currency(row['amount'])}"
                ):
                    edit_mode = st.session_state.get(f"edit_{row['id']}", False)

                    if edit_mode:
                        with st.form(f"edit_form_{row['id']}"):
                            e_date = st.date_input(
                                "Date", value=row["date"],
                                key=f"ed_{row['id']}",
                            )
                            e_amount = st.number_input(
                                "Amount", value=float(row["amount"]),
                                min_value=0.01, key=f"ea_{row['id']}",
                            )
                            e_cat = st.selectbox(
                                "Category", CATEGORIES,
                                index=CATEGORIES.index(row["category"]),
                                key=f"ec_{row['id']}",
                            )
                            e_desc = st.text_input(
                                "Description", value=row["description"] or "",
                                key=f"eds_{row['id']}",
                            )
                            e_pay = st.selectbox(
                                "Payment Mode", PAYMENT_MODES,
                                index=PAYMENT_MODES.index(row["payment_mode"])
                                if row["payment_mode"] in PAYMENT_MODES else 0,
                                key=f"ep_{row['id']}",
                            )
                            c1, c2 = st.columns(2)
                            with c1:
                                save = st.form_submit_button("💾 Save", type="primary")
                            with c2:
                                cancel = st.form_submit_button("Cancel")
                            if save:
                                ok, msg = em.update_expense(
                                    row["id"], e_date, e_amount, e_cat, e_desc, e_pay
                                )
                                st.session_state[f"edit_{row['id']}"] = False
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                            if cancel:
                                st.session_state[f"edit_{row['id']}"] = False
                                st.rerun()
                    else:
                        st.write(f"**Description:** {row['description'] or 'N/A'}")
                        st.write(f"**Payment Mode:** {row['payment_mode']}")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("✏️ Edit", key=f"btn_edit_{row['id']}"):
                                st.session_state[f"edit_{row['id']}"] = True
                                st.rerun()
                        with c2:
                            if st.button("🗑️ Delete", key=f"btn_del_{row['id']}"):
                                ok, msg = em.delete_expense(row["id"])
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
