from datetime import datetime
import os
import pandas as pd
import streamlit as st

# --- CẤU HÌNH GIAO DIỆN HIỆN ĐẠI ---
st.set_page_config(
    page_title="Arirang ERP - Quản Lý Đơn Hàng & Bảng Giá",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- TÙY CHỈNH CSS ĐỂ GỌN GÀNG, CÂN ĐỐI VÀ KHÔNG BỊ TRỐNG RỖNG ---
st.markdown(
    """
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .main-title {
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 13px;
            color: #64748b;
            margin-bottom: 15px;
        }
        /* Khung viền phiếu PO gọn gàng, giảm khoảng trắng thừa */
        .po-container {
            border: 2px solid #cbd5e1;
            padding: 25px 35px;
            border-radius: 10px;
            background-color: #ffffff;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            color: #1e293b;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .po-header {
            text-align: center;
            font-weight: 700;
            font-size: 22px;
            color: #0f172a;
            margin-bottom: 15px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        /* Thu hẹp khoảng cách dòng cho các thông tin chung */
        .po-info-row {
            font-size: 14px;
            line-height: 1.5;
            color: #334155;
            margin-bottom: 4px;
        }
        .po-summary {
            text-align: right;
            font-size: 14px;
            line-height: 1.5;
            color: #334155;
            margin-top: 10px;
        }
        
        /* Tối ưu khi in ấn giấy (Ctrl + P) */
        @media print {
            body {
                background-color: #ffffff;
            }
            .po-container {
                border: 2px solid #000000 !important;
                box-shadow: none !important;
                padding: 15px !important;
                width: 100% !important;
            }
            header, footer, .stTabs {
                display: none !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">📦 ARIRANG CHEMICAL - HỆ THỐNG QUẢN LÝ PO & BẢNG'
    " GIÁ</div>",
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Phần mềm hỗ trợ sales tự động hóa báo giá, kiểm'
    " tra bậc số lượng và phát hành phiếu PO chuẩn doanh nghiệp.</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- XỬ LÝ LỊCH SỬ PO (FILE CSV) ---
HISTORY_FILE = "po_history.csv"


def load_po_history():
  if os.path.exists(HISTORY_FILE):
    df = pd.read_csv(HISTORY_FILE)
    if not df.empty and "Stt" not in df.columns:
      df.insert(0, "Stt", range(1, len(df) + 1))
    return df
  else:
    return pd.DataFrame(columns=[
        "Stt",
        "Mã PO",
        "Tên Công Ty / Khách Hàng",
        "Phân Loại Đơn",
        "Địa Chỉ Giao Hàng",
        "Sales Phụ Trách",
        "Ngày Nhận PO",
        "Ngày Giao Hàng",
        "Tổng Tiền Hàng (VNĐ)",
        "Thuế VAT (8%) (VNĐ)",
        "Tổng Thanh Toán (VNĐ)",
        "Chi Tiết Sản Phẩm",
        "Ghi Chú",
    ])


def save_po_record(po_record):
  df_history = load_po_history()
  if "Stt" in df_history.columns:
    df_history = df_history.drop(columns=["Stt"])

  new_row = pd.DataFrame([po_record])
  df_history = pd.concat([df_history, new_row], ignore_index=True)
  df_history.insert(0, "Stt", range(1, len(df_history) + 1))
  df_history.to_csv(HISTORY_FILE, index=False)


def delete_po_record_by_index(stt_to_delete):
  df_history = load_po_history()
  if not df_history.empty and "Stt" in df_history.columns:
    df_history = df_history[df_history["Stt"] != stt_to_delete]
    if not df_history.empty:
      df_history = df_history.drop(columns=["Stt"])
      df_history.insert(0, "Stt", range(1, len(df_history) + 1))
      df_history.to_csv(HISTORY_FILE, index=False)
    else:
      if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


def clear_all_history():
  if os.path.exists(HISTORY_FILE):
    os.remove(HISTORY_FILE)


# 1. Khởi tạo Bảng giá chuẩn chung trong Session State
if "df_price_list" not in st.session_state:
  st.session_state.df_price_list = pd.DataFrame([
      # Mực In
      {
          "Loại": "🖨️ Mực In",
          "Tên Công Ty / Khách Hàng": "Lộ Đức",
          "Mã SP / Quy cách": "OPP 39",
          "ĐVT": "Kg",
          "Số Lượng Tối Đa (Kg)": 999999.0,
          "Đơn giá chuẩn (VNĐ)": 75000.0,
          "Ngày Báo Giá": "15/01/2026",
      },
      {
          "Loại": "🖨️ Mực In",
          "Tên Công Ty / Khách Hàng": "Lộ Đức",
          "Mã SP / Quy cách": "PE GOLD",
          "ĐVT": "Thùng",
          "Số Lượng Tối Đa (Kg)": 999999.0,
          "Đơn giá chuẩn (VNĐ)": 139000.0,
          "Ngày Báo Giá": "01/02/2026",
      },
      {
          "Loại": "🖨️ Mực In",
          "Tên Công Ty / Khách Hàng": "Vina Úc ĐN",
          "Mã SP / Quy cách": "OPP 39",
          "ĐVT": "Kg",
          "Số Lượng Tối Đa (Kg)": 999999.0,
          "Đơn giá chuẩn (VNĐ)": 78000.0,
          "Ngày Báo Giá": "10/03/2026",
      },
      # Hạt Màu (Phân bậc số lượng)
      {
          "Loại": "🎨 Hạt Màu",
          "Tên Công Ty / Khách Hàng": "Lộ Đức",
          "Mã SP / Quy cách": "MBP-2010",
          "ĐVT": "Kg",
          "Số Lượng Tối Đa (Kg)": 50.0,
          "Đơn giá chuẩn (VNĐ)": 154000.0,
          "Ngày Báo Giá": "01/03/2026",
      },
      {
          "Loại": "🎨 Hạt Màu",
          "Tên Công Ty / Khách Hàng": "Lộ Đức",
          "Mã SP / Quy cách": "MBP-2010",
          "ĐVT": "Kg",
          "Số Lượng Tối Đa (Kg)": 200.0,
          "Đơn giá chuẩn (VNĐ)": 101000.0,
          "Ngày Báo Giá": "01/03/2026",
      },
      {
          "Loại": "🎨 Hạt Màu",
          "Tên Công Ty / Khách Hàng": "Lộ Đức",
          "Mã SP / Quy cách": "MBP-2010",
          "ĐVT": "Kg",
          "Số Lượng Tối Đa (Kg)": 999999.0,
          "Đơn giá chuẩn (VNĐ)": 94000.0,
          "Ngày Báo Giá": "01/03/2026",
      },
  ])

# 2. Session state lưu kết quả PO
if "po_data" not in st.session_state:
  st.session_state.po_data = None

if "df_po_items" not in st.session_state:
  st.session_state.df_po_items = pd.DataFrame([{
      "Mã SP / Quy cách": "OPP 39",
      "Số lượng": 340.0,
      "ĐVT": "Kg",
      "Đơn giá (VNĐ)": 75000.0,
  }])

tab1, tab2, tab3 = st.tabs([
    "🚀 Tạo Đơn Hàng (PO)",
    "⚙️ Quản Lý Bảng Giá & Phân Loại",
    "📜 Lịch Sử Đơn Hàng (PO)",
])

# ==================== TAB 1: TẠO ĐƠN HÀNG ====================
with tab1:
  st.markdown("### 📋 1. Thiết Lập Thông Tin Chung Đơn Hàng")

  order_category = st.radio(
      "📌 Chọn phân loại dòng hàng sản xuất:",
      options=["🖨️ Mực In", "🎨 Hạt Màu"],
      horizontal=True,
  )

  df_cat_price = st.session_state.df_price_list[
      st.session_state.df_price_list["Loại"] == order_category
  ]
  if df_cat_price.empty:
    df_cat_price = st.session_state.df_price_list

  unique_customers = (
      df_cat_price["Tên Công Ty / Khách Hàng"].dropna().unique().tolist()
  )
  if not unique_customers:
    unique_customers = ["Lộ Đức"]

  df_history_check = load_po_history()

  col1, col2 = st.columns(2)

  with col1:
    customer_name = st.selectbox(
        "🏢 Tên Khách Hàng / Công Ty",
        options=unique_customers,
        key=f"cust_{order_category}",
    )

    past_addresses = []
    if (
        not df_history_check.empty
        and "Địa Chỉ Giao Hàng" in df_history_check.columns
    ):
      matched_hist = df_history_check[
          df_history_check["Tên Công Ty / Khách Hàng"]
          .astype(str)
          .str.strip()
          .str.lower()
          == customer_name.strip().lower()
      ]
      past_addresses = (
          matched_hist["Địa Chỉ Giao Hàng"].dropna().unique().tolist()
      )

    delivery_address = st.text_input(
        "📍 Địa chỉ giao hàng",
        value=past_addresses[0] if past_addresses else "",
        placeholder="Nhập địa chỉ giao hàng...",
    )
    if past_addresses:
      st.caption("💡 Địa chỉ từng giao gần đây: " + " | ".join(past_addresses))

    po_number = st.text_input("🔖 Mã số PO", value="PO-01")

  with col2:
    order_date_val = st.date_input("📅 Ngày nhận PO", value=datetime.today())
    order_date_str = order_date_val.strftime("%d/%m/%Y")

    delivery_date_val = st.date_input(
        "🚚 Ngày yêu cầu giao hàng", value=datetime.today()
    )
    delivery_date_str = delivery_date_val.strftime("%d/%m/%Y")

    sales_person = st.text_input("👤 Sales phụ trách", value="Lê Thanh Duy")

  st.markdown("---")
  st.markdown(f"### 📦 2. Chi Tiết Danh Sách Sản Phẩm ({order_category})")

  if order_category == "🖨️ Mực In":
    df_price_filtered = df_cat_price[
        df_cat_price["Tên Công Ty / Khách Hàng"].str.strip().str.lower()
        == customer_name.strip().lower()
    ]
    available_codes = (
        df_price_filtered["Mã SP / Quy cách"].dropna().unique().tolist()
        if not df_price_filtered.empty
        else df_cat_price["Mã SP / Quy cách"].dropna().unique().tolist()
    )

    price_dict = dict(
        zip(
            df_price_filtered["Mã SP / Quy cách"]
            if not df_price_filtered.empty
            else df_cat_price["Mã SP / Quy cách"],
            df_price_filtered["Đơn giá chuẩn (VNĐ)"]
            if not df_price_filtered.empty
            else df_cat_price["Đơn giá chuẩn (VNĐ)"],
        )
    )
    unit_dict = dict(
        zip(
            df_price_filtered["Mã SP / Quy cách"]
            if not df_price_filtered.empty
            else df_cat_price["Mã SP / Quy cách"],
            df_price_filtered["ĐVT"]
            if not df_price_filtered.empty
            else df_cat_price["ĐVT"],
        )
    )

    if available_codes:
      st.info(
          "💡 **Mã mực in chuẩn:** "
          + ", ".join(f"`{c}`" for c in available_codes)
      )

    edited_df = st.data_editor(
        st.session_state.df_po_items,
        num_rows="dynamic",
        use_container_width=True,
        key="po_table_mucin",
        column_config={
            "Mã SP / Quy cách": st.column_config.TextColumn(
                "Mã SP / Quy cách", required=True
            ),
            "ĐVT": st.column_config.SelectboxColumn(
                "Đơn vị tính",
                options=["Kg", "Thùng", "Phuy", "Lon"],
                required=True,
            ),
            "Số lượng": st.column_config.NumberColumn(
                min_value=0.0, step=1.0, format="%,.0f"
            ),
            "Đơn giá (VNĐ)": st.column_config.NumberColumn(
                min_value=0.0, step=1000.0, format="%,.0f"
            ),
        },
    )

    for idx, row in edited_df.iterrows():
      code = str(row["Mã SP / Quy cách"]).strip()
      if code in price_dict:
        curr_p = row["Đơn giá (VNĐ)"]
        if pd.isna(curr_p) or curr_p == 0.0 or curr_p != price_dict[code]:
          edited_df.loc[idx, "Đơn giá (VNĐ)"] = price_dict[code]
        if code in unit_dict and (
            pd.isna(row["ĐVT"]) or str(row["ĐVT"]).strip() == ""
        ):
          edited_df.loc[idx, "ĐVT"] = unit_dict[code]

    st.session_state.df_po_items = edited_df

  else:
    df_price_filtered = df_cat_price[
        df_cat_price["Tên Công Ty / Khách Hàng"].str.strip().str.lower()
        == customer_name.strip().lower()
    ]
    available_codes = (
        df_price_filtered["Mã SP / Quy cách"].dropna().unique().tolist()
        if not df_price_filtered.empty
        else df_cat_price["Mã SP / Quy cách"].dropna().unique().tolist()
    )

    if available_codes:
      st.info(
          "💡 **Mã hạt màu chuẩn:** "
          + ", ".join(f"`{c}`" for c in available_codes)
      )

    edited_df = st.data_editor(
        st.session_state.df_po_items,
        num_rows="dynamic",
        use_container_width=True,
        key="po_table_hatmau",
        column_config={
            "Mã SP / Quy cách": st.column_config.TextColumn(
                "Mã SP / Quy cách", required=True
            ),
            "ĐVT": st.column_config.SelectboxColumn(
                "Đơn vị tính",
                options=["Kg", "Thùng", "Phuy", "Lon"],
                required=True,
            ),
            "Số lượng": st.column_config.NumberColumn(
                "Số lượng", min_value=0.0, step=1.0, format="%,.0f"
            ),
            "Đơn giá (VNĐ)": st.column_config.NumberColumn(
                "Đơn giá (VNĐ) - Tự động dò bậc",
                min_value=0.0,
                step=1000.0,
                format="%,.0f",
            ),
        },
    )

    for idx, row in edited_df.iterrows():
      code = str(row["Mã SP / Quy cách"]).strip()
      qty = float(row["Số lượng"]) if not pd.isna(row["Số lượng"]) else 0.0

      if code and not df_price_filtered.empty:
        matched_tiers = df_price_filtered[
            df_price_filtered["Mã SP / Quy cách"]
            .astype(str)
            .str.strip()
            .str.lower()
            == code.lower()
        ].sort_values(by="Số Lượng Tối Đa (Kg)", ascending=True)

        if not matched_tiers.empty:
          matched_price = None
          matched_unit = matched_tiers.iloc[0]["ĐVT"]

          for _, tier_row in matched_tiers.iterrows():
            if qty <= float(tier_row["Số Lượng Tối Đa (Kg)"]):
              matched_price = float(tier_row["Đơn giá chuẩn (VNĐ)"])
              break

          if matched_price is None:
            matched_price = float(
                matched_tiers.iloc[-1]["Đơn giá chuẩn (VNĐ)"]
            )

          if (
              pd.isna(row["Đơn giá (VNĐ)"])
              or row["Đơn giá (VNĐ)"] != matched_price
          ):
            edited_df.loc[idx, "Đơn giá (VNĐ)"] = matched_price
          if pd.isna(row["ĐVT"]) or str(row["ĐVT"]).strip() == "":
            edited_df.loc[idx, "ĐVT"] = matched_unit

    st.session_state.df_po_items = edited_df

  note = st.text_area(
      "📝 Ghi chú đặc biệt cho phòng kế hoạch / sản xuất",
      value="Giao gấp, kiểm tra kỹ chất lượng màu trước khi xuất kho.",
  )

  if st.button(
      "🚀 Tạo và Xuất Bản Phiếu Xác Nhận PO",
      type="primary",
      use_container_width=True,
  ):
    if not customer_name or not po_number or edited_df.empty:
      st.error(
          "Vui lòng điền Tên khách hàng, Mã số PO và nhập ít nhất 1 sản phẩm!"
      )
    else:
      has_error = False
      error_messages = []
      valid_codes_lower = [str(c).strip().lower() for c in available_codes]

      for index, row in edited_df.iterrows():
        code = str(row["Mã SP / Quy cách"]).strip()
        qty = (
            float(row["Số lượng"])
            if not pd.isna(row["Số lượng"])
            else 0.0
        )

        if code and qty > 0:
          if code.lower() not in valid_codes_lower:
            has_error = True
            error_messages.append(
                f"❌ Lỗi dòng {index + 1}: Công ty **'{customer_name}'** không"
                f" có báo giá cho mã sản phẩm **'{code}'**!"
            )

      if has_error:
        for err in error_messages:
          st.error(err)
        st.warning(
            "⚠️ Vui lòng kiểm tra lại mã sản phẩm trong bảng giá trước khi tạo"
            " PO."
        )
      else:
        items = []
        item_summary_list = []
        subtotal = 0.0

        for index, row in edited_df.iterrows():
          code = str(row["Mã SP / Quy cách"]).strip()
          qty = (
              float(row["Số lượng"])
              if not pd.isna(row["Số lượng"])
              else 0.0
          )
          unit = str(row["ĐVT"])
          price = (
              float(row["Đơn giá (VNĐ)"])
              if not pd.isna(row["Đơn giá (VNĐ)"])
              else 0.0
          )

          if code and qty > 0:
            amount = qty * price
            subtotal += amount
            items.append({
                "Mã SP / Quy cách": code,
                "Số lượng": f"{qty:,.0f}",
                "ĐVT": unit,
                "Đơn giá (VNĐ)": f"{price:,.0f}",
                "Thành tiền (VNĐ)": f"{amount:,.0f}",
            })
            item_summary_list.append(f"{code} ({qty:,.0f} {unit})")

        vat_amount = subtotal * 0.08
        grand_total = subtotal + vat_amount

        st.session_state.po_data = {
            "customer": customer_name,
            "category": order_category,
            "address": delivery_address,
            "po_no": po_number,
            "order_date": order_date_str,
            "delivery_date": delivery_date_str,
            "sales": sales_person,
            "items": items,
            "subtotal": f"{subtotal:,.0f}",
            "vat": f"{vat_amount:,.0f}",
            "grand_total": f"{grand_total:,.0f}",
            "note": note,
        }

        po_record = {
            "Mã PO": po_number,
            "Tên Công Ty / Khách Hàng": customer_name,
            "Phân Loại Đơn": order_category,
            "Địa Chỉ Giao Hàng": delivery_address,
            "Sales Phụ Trách": sales_person,
            "Ngày Nhận PO": order_date_str,
            "Ngày Giao Hàng": delivery_date_str,
            "Tổng Tiền Hàng (VNĐ)": f"{subtotal:,.0f}",
            "Thuế VAT (8%) (VNĐ)": f"{vat_amount:,.0f}",
            "Tổng Thanh Toán (VNĐ)": f"{grand_total:,.0f}",
            "Chi Tiết Sản Phẩm": ", ".join(item_summary_list),
            "Ghi Chú": note,
        }
        save_po_record(po_record)

        st.success(
            f"Đã lập và lưu lịch sử thành công đơn hàng {po_number} cho"
            f" khách hàng {customer_name}!"
        )

  # --- KHUNG HIỂN THỊ PHIẾU PO ĐÃ ĐƯỢC THU GỌN KHOẢNG CÁCH ---
  if st.session_state.po_data is not None:
    data = st.session_state.po_data

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
      st.markdown('<div class="po-container">', unsafe_allow_html=True)
      st.markdown(
          f'<div class="po-header">PHIẾU XÁC NHẬN ĐƠN HÀNG ({data["category"]})'
          ' <br><span style="font-size:12px; color:#64748b; font-weight:normal;">Gửi'
          " Phòng Kế Hoạch & Tài Chính - Arirang Chemical</span></div>",
          unsafe_allow_html=True,
      )

      # Dùng các dòng thông tin gom gọn, căn đối 2 cột
      col_a, col_b = st.columns(2)
      with col_a:
        st.markdown(
            f'<div class="po-info-row"><b>🔖 Mã số PO:</b>'
            f" {data['po_no']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="po-info-row"><b>🏢 Khách hàng:</b>'
            f" {data['customer']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="po-info-row"><b>📌 Phân loại:</b>'
            f" {data['category']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="po-info-row"><b>📍 Địa chỉ giao hàng:</b>'
            f" {data['address']}</div>",
            unsafe_allow_html=True,
        )
      with col_b:
        st.markdown(
            f'<div class="po-info-row"><b>👤 Sales phụ trách:</b>'
            f" {data['sales']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="po-info-row"><b>📅 Ngày nhận PO:</b>'
            f" {data['order_date']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="po-info-row"><b>🚚 Ngày yêu cầu giao:</b>'
            f" {data['delivery_date']}</div>",
            unsafe_allow_html=True,
        )

      st.markdown("---")
      st.markdown(
          '<div style="font-weight:600; margin-bottom:8px;">📦 Chi tiết danh'
          " sách sản phẩm đặt hàng:</div>",
          unsafe_allow_html=True,
      )

      df_display = pd.DataFrame(data["items"])
      st.dataframe(
          df_display, use_container_width=True, hide_index=True
      )

      st.markdown(
          f"""
            <div class="po-summary">
                <b>Cộng tiền hàng:</b> {data['subtotal']} VNĐ<br>
                <b>Thuế VAT (8%):</b> {data['vat']} VNĐ<br>
                <b><span style="font-size: 16px; color: #dc2626;">Tổng cộng thanh toán (Gồm VAT):</span></b> <span style="font-size: 16px; color: #dc2626; font-weight: bold;">{data['grand_total']} VNĐ</span>
            </div>
            """,
          unsafe_allow_html=True,
      )

      st.markdown(
          '<div style="font-weight:600; margin-top:15px; margin-bottom:5px;">📝'
          " Ghi chú:</div>",
          unsafe_allow_html=True,
      )
      st.info(
          data["note"] if data["note"] else "Không có ghi chú đặc biệt."
      )
      st.markdown("</div>", unsafe_allow_html=True)

# ==================== TAB 2: QUẢN LÝ BẢNG GIÁ ====================
with tab2:
  st.subheader("⚙️ Quản Lý Hệ Thống Bảng Giá")
  price_tab_choice = st.radio(
      "Chọn danh mục bảng giá:",
      options=["🖨️ Bảng Giá Mực In", "🎨 Bảng Giá Hạt Màu"],
      horizontal=True,
  )
  st.markdown("---")

  df_all = st.session_state.df_price_list

  if price_tab_choice == "🖨️ Bảng Giá Mực In":
    st.markdown("### 🖨️ Danh Mục Bảng Giá Mực In")
    df_mucin = df_all[df_all["Loại"] == "🖨️ Mực In"].copy()

    edited_mucin = st.data_editor(
        df_mucin,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_mucin",
        column_config={
            "Loại": None,
            "Tên Công Ty / Khách Hàng": st.column_config.TextColumn(
                "Tên Công Ty / Khách Hàng", required=True
            ),
            "Mã SP / Quy cách": st.column_config.TextColumn(
                "Mã SP / Quy cách", required=True
            ),
            "ĐVT": st.column_config.SelectboxColumn(
                "Đơn vị tính",
                options=["Kg", "Thùng", "Phuy", "Lon"],
                required=True,
            ),
            "Số Lượng Tối Đa (Kg)": None,
            "Đơn giá chuẩn (VNĐ)": st.column_config.NumberColumn(
                "Đơn giá chuẩn (VNĐ)",
                min_value=0.0,
                step=1000.0,
                format="%,.0f",
            ),
            "Ngày Báo Giá": st.column_config.TextColumn(
                "Ngày Báo Giá (dd/mm/yyyy)", required=True
            ),
        },
    )

    if st.button("💾 Lưu Cập Nhật Bảng Giá Mực In", type="primary"):
      edited_mucin["Loại"] = "🖨️ Mực In"
      edited_mucin["Số Lượng Tối Đa (Kg)"] = 999999.0
      df_hatmau_old = df_all[df_all["Loại"] == "🎨 Hạt Màu"]
      st.session_state.df_price_list = pd.concat(
          [edited_mucin, df_hatmau_old], ignore_index=True
      )
      st.success("Đã cập nhật Bảng Giá Mực In thành công!")

  else:
    st.markdown("### 🎨 Danh Mục Bảng Giá Hạt Màu (Theo Bậc Số Lượng)")
    df_hatmau = df_all[df_all["Loại"] == "🎨 Hạt Màu"].copy()

    edited_hatmau = st.data_editor(
        df_hatmau,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_hatmau",
        column_config={
            "Loại": None,
            "Tên Công Ty / Khách Hàng": st.column_config.TextColumn(
                "Tên Công Ty / Khách Hàng", required=True
            ),
            "Mã SP / Quy cách": st.column_config.TextColumn(
                "Mã SP / Quy cách", required=True
            ),
            "ĐVT": st.column_config.SelectboxColumn(
                "Đơn vị tính",
                options=["Kg", "Thùng", "Phuy", "Lon"],
                required=True,
            ),
            "Số Lượng Tối Đa (Kg)": st.column_config.NumberColumn(
                "Số Lượng Tối Đa (Kg)",
                min_value=1.0,
                step=1.0,
                format="%,.0f",
            ),
            "Đơn giá chuẩn (VNĐ)": st.column_config.NumberColumn(
                "Đơn giá chuẩn (VNĐ)",
                min_value=0.0,
                step=1000.0,
                format="%,.0f",
            ),
            "Ngày Báo Giá": st.column_config.TextColumn(
                "Ngày Báo Giá (dd/mm/yyyy)", required=True
            ),
        },
    )

    if st.button("💾 Lưu Cập Nhật Bảng Giá Hạt Màu", type="primary"):
      edited_hatmau["Loại"] = "🎨 Hạt Màu"
      df_mucin_old = df_all[df_all["Loại"] == "🖨️ Mực In"]
      st.session_state.df_price_list = pd.concat(
          [df_mucin_old, edited_hatmau], ignore_index=True
      )
      st.success("Đã cập nhật Bảng Giá Hạt Màu thành công!")

# ==================== TAB 3: LỊCH SỬ PO ====================
with tab3:
  st.subheader("📜 Tra Cứu Lịch Sử Đơn Hàng (PO)")
  df_history = load_po_history()

  if df_history.empty:
    st.info("Chưa có đơn hàng nào trong lịch sử.")
  else:
    search_keyword = st.text_input(
        "🔍 Tìm kiếm nhanh (Mã PO, Khách hàng, Phân loại...):",
        placeholder="Nhập từ khóa tìm kiếm...",
    )

    if search_keyword:
      kw = search_keyword.strip().lower()
      filtered_df = df_history[
          df_history["Mã PO"]
          .astype(str)
          .str.lower()
          .str.contains(kw, na=False)
          | df_history["Tên Công Ty / Khách Hàng"]
          .astype(str)
          .str.lower()
          .str.contains(kw, na=False)
          | df_history["Phân Loại Đơn"]
          .astype(str)
          .str.lower()
          .str.contains(kw, na=False)
          | df_history["Ngày Nhận PO"]
          .astype(str)
          .str.lower()
          .str.contains(kw, na=False)
      ]
    else:
      filtered_df = df_history

    st.markdown(f"**Kết quả tìm kiếm ({len(filtered_df)} đơn hàng):**")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🛠️ Quản Lý & Xóa Lịch Sử PO")
    col_del1, col_del2 = st.columns(2)

    with col_del1:
      max_stt = int(df_history["Stt"].max()) if not df_history.empty else 1
      stt_to_delete = st.number_input(
          "Chọn số thứ tự (Stt) đơn hàng cần xóa",
          min_value=1,
          max_value=max_stt,
          step=1,
      )
      if st.button("❌ Xóa dòng PO đã chọn", type="secondary"):
        delete_po_record_by_index(int(stt_to_delete))
        st.success(f"Đã xóa thành công đơn hàng số thứ tự: {stt_to_delete}!")
        st.rerun()

    with col_del2:
      st.markdown("<br>", unsafe_allow_html=True)
      if st.button(
          "⚠️ Xóa TẤT CẢ Lịch Sử Đơn Hàng", type="primary", use_container_width=True
      ):
        clear_all_history()
        st.success("Đã xóa sạch lịch sử PO!")
        st.rerun()

    st.markdown("---")
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Tải Xuất Báo Cáo Lịch Sử PO (CSV/Excel)",
        data=csv_bytes,
        file_name=f"Lich_Su_PO_Arirang_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )