"""OCR Bill Scanner page – upload bills and extract details."""

import streamlit as st
from datetime import date
from auth import AuthManager
from expense import ExpenseManager, CATEGORIES, PAYMENT_MODES
from ocr import BillScanner
from utils import apply_custom_css, format_currency


def render():
    AuthManager.require_auth()
    apply_custom_css(st.session_state.get("dark_mode", True))

    user_id = AuthManager.get_user_id()
    scanner = BillScanner(user_id)
    em = ExpenseManager(user_id)

    st.markdown('<p class="page-header">📷 OCR Bill Scanner</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Upload a bill image – AI extracts store, date, amount & items</p>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Upload Bill Image",
        type=["png", "jpg", "jpeg", "webp"],
        help="Supported formats: PNG, JPG, JPEG, WEBP",
    )

    if uploaded:
        col_img, col_data = st.columns([1, 1])

        with col_img:
            st.image(uploaded, caption="Uploaded Bill", use_container_width=True)

        with col_data:
            if st.button("🔍 Scan Bill", type="primary", use_container_width=True):
                with st.spinner("Running OCR... This may take a moment."):
                    try:
                        result = scanner.scan_bill(uploaded)
                        st.session_state["ocr_result"] = result
                        st.success("OCR extraction complete!")
                    except Exception as exc:
                        st.error(f"OCR failed: {exc}")

    if "ocr_result" in st.session_state:
        result = st.session_state["ocr_result"]

        st.subheader("📝 Extracted Details (Edit before saving)")
        with st.form("ocr_save_form"):
            store_name = st.text_input("Store Name", value=result.get("store_name", ""))
            bill_date = st.date_input(
                "Bill Date",
                value=result.get("bill_date") or date.today(),
            )
            total_amount = st.number_input(
                "Total Amount (₹)",
                value=float(result.get("total_amount", 0)),
                min_value=0.0,
                step=0.01,
            )
            items = st.text_area("Detected Items", value=result.get("items", ""))
            category = st.selectbox("Expense Category", CATEGORIES)
            payment_mode = st.selectbox("Payment Mode", PAYMENT_MODES, key="ocr_pay")
            description = st.text_input(
                "Description",
                value=f"Bill from {store_name}",
            )

            col1, col2 = st.columns(2)
            with col1:
                save_bill = st.form_submit_button("💾 Save Bill Record", use_container_width=True)
            with col2:
                save_expense = st.form_submit_button(
                    "✅ Save as Expense", type="primary", use_container_width=True
                )

            if save_bill:
                ok, msg = scanner.save_bill(
                    store_name, bill_date, total_amount, items,
                    result.get("image_path", ""),
                )
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

            if save_expense:
                ok, msg = em.add_expense(
                    bill_date, total_amount, category, description, payment_mode
                )
                if ok:
                    scanner.save_bill(
                        store_name, bill_date, total_amount, items,
                        result.get("image_path", ""),
                    )
                    st.success("Expense saved from scanned bill!")
                    del st.session_state["ocr_result"]
                    st.rerun()
                else:
                    st.error(msg)

        with st.expander("🔤 Raw OCR Text"):
            st.text(result.get("raw_text", "No text extracted"))

    else:
        st.info("Upload a bill image and click 'Scan Bill' to extract details using EasyOCR.")
