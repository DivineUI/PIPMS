"""
app.py
Pharmacy Inventory & Prescription Management System.
Enhanced with local background image (bg_pharmacy.jpg), custom glassmorphism styling, and clean UI.
"""

import sqlite3
import base64
import pandas as pd
from datetime import date

import streamlit as st

import database
from entities import ENTITIES, NAV, singular
from permissions import ROLES, can, can_read

st.set_page_config(
    page_title="PIPMS — Pharmacy Inventory & Prescriptions",
    page_icon="℞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to convert local image to base64 for reliable CSS injection
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

img_base64 = get_base64_image("bg_pharmacy.jpg")
bg_css = f"url('data:image/jpeg;base64,{img_base64}')" if img_base64 else "linear-gradient(135deg, #090d16 0%, #0f172a 100%)"

# -----------------------------------------------------------------------------
# CUSTOM STYLING & UI INJECTION
# -----------------------------------------------------------------------------
st.markdown(f"""
<style>
    .stApp {{
        background-image: linear-gradient(rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.94)), {bg_css};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        color: #f1f5f9;
    }}
    
    .main-header {{
        background: rgba(30, 41, 59, 0.85);
        backdrop-filter: blur(10px);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }}
    .main-header h1 {{
        color: #f8fafc;
        font-weight: 700;
        margin: 0;
        font-size: 1.85rem;
    }}
    .main-header p {{
        color: #94a3b8;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }}

    div[data-testid="stMetric"] {{
        background: rgba(30, 41, 59, 0.85);
        backdrop-filter: blur(8px);
        border: 1px solid #334155;
        padding: 0.75rem 0.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        text-align: center;
    }}
    div[data-testid="stMetric"] label {{
        color: #94a3b8 !important;
        font-size: 0.65rem !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        white-space: normal !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: #f8fafc !important;
        font-size: 1.4rem !important;
        font-weight: 700;
    }}

    section[data-testid="stSidebar"] {{
        background-color: rgba(11, 17, 32, 0.95);
        border-right: 1px solid #1e293b;
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

if "conn" not in st.session_state:
    st.session_state.conn = database.build_connection()
    st.session_state.role = "Admin"
    st.session_state.section = "DASHBOARD"
    st.session_state.search = {}
    st.session_state.active_filters = {}
    st.session_state.form_mode = None          
    st.session_state.confirm_delete = None      
    st.session_state.drill = None               

conn: sqlite3.Connection = st.session_state.conn


def friendly_sql_error(err: Exception) -> str:
    msg = str(err)
    if "FOREIGN KEY constraint failed" in msg:
        return "Can't complete this — other records still reference this record."
    if "expired" in msg:
        return "Cannot dispense: this medicine batch has expired"
    if "not enough stock" in msg:
        return "Cannot dispense: not enough stock on hand"
    if "CHECK constraint failed" in msg:
        return "That value violates a database rule (e.g. quantity or price can't be negative)."
    if "UNIQUE constraint failed" in msg:
        return "That value is already in use (must be unique)."
    return f"Something went wrong: {msg}"


with st.sidebar:
    st.markdown("### \u211E PIPMS")
    st.caption("Pharmacy Inventory & Prescriptions")
    st.divider()

    role = st.selectbox("Signed in as", ROLES, index=ROLES.index(st.session_state.role))
    if role != st.session_state.role:
        st.session_state.role = role
        if not can_read(role, st.session_state.section):
            st.session_state.section = "DASHBOARD"
        st.session_state.drill = None
        st.rerun()

    access_note = "full access" if st.session_state.role == "Admin" else "scoped access"
    st.caption(f"**{st.session_state.role}** \u00b7 {access_note}")
    st.divider()

    for group_label, items in NAV:
        visible = [it for it in items if can_read(st.session_state.role, it[0])]
        if not visible:
            continue
        st.markdown(f"<p style='color: #64748b; font-size: 0.75rem; font-weight: 700; margin-top: 1rem;'>{group_label.upper()}</p>", unsafe_allow_html=True)
        for key, label, icon in visible:
            is_active = key == st.session_state.section and st.session_state.drill is None
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.section = key
                st.session_state.drill = None
                st.session_state.form_mode = None
                st.rerun()

    st.divider()


def render_form():
    mode, entity_key, pk, presets = st.session_state.form_mode
    ent = ENTITIES[entity_key]
    is_edit = mode == "edit"
    record = {}
    if is_edit:
        record = database.query_one(conn, f"SELECT * FROM {entity_key} WHERE {ent['pk']} = ?", (pk,)) or {}
    elif presets:
        record = dict(presets)

    st.markdown(f"""
    <div class="main-header">
        <h1>{("Edit " if is_edit else "Add ") + singular(ent["label"])}</h1>
        <p>Fill in the required information below.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form(key=f"form_{entity_key}_{pk}"):
        values = {}
        for f in ent["fields"]:
            key = f["key"]
            current = record.get(key)
            locked = presets is not None and key in presets and not is_edit
            if f["type"] == "fk":
                options = database.query(
                    conn, f"SELECT {f['fk_pk']} AS id, ({f['fk_label_sql']}) AS lbl FROM {f['fk_entity']} ORDER BY lbl"
                )
                ids = [o["id"] for o in options]
                labels = {o["id"]: o["lbl"] for o in options}
                default_index = ids.index(current) if current in ids else None
                if locked:
                    st.text_input(f["label"], value=labels.get(current, str(current)), disabled=True)
                    values[key] = current
                else:
                    choice = st.selectbox(
                        f["label"] + (" *" if f.get("required") else ""),
                        options=ids, index=default_index if default_index is not None else 0,
                        format_func=lambda i: labels.get(i, str(i)), key=f"fld_{entity_key}_{key}_{pk}",
                    )
                    values[key] = choice
            elif f["type"] == "date":
                default = date.fromisoformat(current) if current else date.today()
                values[key] = st.date_input(f["label"] + (" *" if f.get("required") else ""), value=default,
                                             key=f"fld_{entity_key}_{key}_{pk}")
            elif f["type"] == "int":
                values[key] = st.number_input(f["label"] + (" *" if f.get("required") else ""),
                                               value=int(current) if current not in (None, "") else f.get("min", 0),
                                               step=int(f.get("step", 1)), min_value=f.get("min"),
                                               key=f"fld_{entity_key}_{key}_{pk}")
            elif f["type"] == "float":
                values[key] = st.number_input(f["label"] + (" *" if f.get("required") else ""),
                                               value=float(current) if current not in (None, "") else float(f.get("min", 0.0)),
                                               step=float(f.get("step", 0.01)), min_value=f.get("min"), format="%.2f",
                                               key=f"fld_{entity_key}_{key}_{pk}")
            else:
                values[key] = st.text_input(f["label"] + (" *" if f.get("required") else ""),
                                             value=current or "", placeholder=f.get("placeholder", ""),
                                             key=f"fld_{entity_key}_{key}_{pk}")

        c1, c2 = st.columns([1, 1])
        submitted = c1.form_submit_button("Save changes" if is_edit else "Create", type="primary", use_container_width=True)
        cancelled = c2.form_submit_button("Cancel", use_container_width=True)

    if cancelled:
        st.session_state.form_mode = None
        st.rerun()

    if submitted:
        missing = [f["label"] for f in ent["fields"]
                   if f.get("required") and (values.get(f["key"]) in (None, ""))]
        if missing:
            st.error("Required: " + ", ".join(missing))
            return
        clean = {}
        for f in ent["fields"]:
            v = values[f["key"]]
            clean[f["key"]] = v.isoformat() if hasattr(v, "isoformat") else v
        try:
            if not is_edit:
                cols = list(clean.keys())
                placeholders = ",".join(["?"] * len(cols))
                database.execute(conn, f"INSERT INTO {entity_key} ({','.join(cols)}) VALUES ({placeholders})",
                                  [clean[c] for c in cols])
                st.success(f"{singular(ent['label'])} added.")
            else:
                cols = list(clean.keys())
                set_clause = ",".join(f"{c}=?" for c in cols)
                database.execute(conn, f"UPDATE {entity_key} SET {set_clause} WHERE {ent['pk']}=?",
                                  [clean[c] for c in cols] + [pk])
                st.success(f"{singular(ent['label'])} updated.")
            st.session_state.form_mode = None
            st.rerun()
        except sqlite3.Error as e:
            st.error(friendly_sql_error(e))


def render_table(ent, rows, entity_key, can_update, can_delete):
    if not rows:
        st.info("No matching records.")
        return

    show_actions = can_update or can_delete or ent["row_extra"]
    ncols = len(ent["columns"]) + (1 if show_actions else 0)
    weights = [2] * len(ent["columns"]) + ([2] if show_actions else [])

    header = st.columns(weights)
    for c, col in zip(header, ent["columns"]):
        c.markdown(f"**{col['label']}**")
    if show_actions:
        header[-1].markdown("**Actions**")

    for row in rows:
        cells = st.columns(weights)
        for c, col in zip(cells, ent["columns"]):
            val = row.get(col["key"])
            c.write(col["fmt"](val) if col.get("fmt") else (val if val is not None else "\u2014"))
        if show_actions:
            with cells[-1]:
                b1, b2, b3 = st.columns(3)
                pk = row[ent["pk"]]
                if ent["row_extra"] == "prescription_items":
                    if b1.button("Items", key=f"items_{entity_key}_{pk}"):
                        st.session_state.drill = ("prescription_items", pk)
                        st.rerun()
                elif ent["row_extra"] == "purchase_items":
                    if b1.button("Items", key=f"items_{entity_key}_{pk}"):
                        st.session_state.drill = ("purchase_items", pk)
                        st.rerun()
                if can_update and not ent.get("no_edit"):
                    if b2.button("Edit", key=f"edit_{entity_key}_{pk}"):
                        st.session_state.form_mode = ("edit", entity_key, pk, None)
                        st.rerun()
                if can_delete:
                    if b3.button("Delete", key=f"del_{entity_key}_{pk}"):
                        st.session_state.confirm_delete = (entity_key, pk)
                        st.rerun()


def render_entity(entity_key):
    ent = ENTITIES[entity_key]
    st.markdown(f"""
    <div class="main-header">
        <h1>{ent["title"]}</h1>
        <p>{ent["desc"]}</p>
    </div>
    """, unsafe_allow_html=True)

    role = st.session_state.role
    can_create = can(role, entity_key, "c")
    can_update = can(role, entity_key, "u")
    can_delete = can(role, entity_key, "d")

    if st.session_state.confirm_delete and st.session_state.confirm_delete[0] == entity_key:
        _, pk = st.session_state.confirm_delete
        st.warning(f"Delete this {singular(ent['label']).lower()}? This cannot be undone.")
        cc1, cc2 = st.columns(2)
        if cc1.button("Yes, delete", type="primary", key=f"confirm_del_{entity_key}_{pk}"):
            try:
                database.execute(conn, f"DELETE FROM {entity_key} WHERE {ent['pk']} = ?", (pk,))
                st.success(f"{singular(ent['label'])} deleted.")
            except sqlite3.Error as e:
                st.error(friendly_sql_error(e))
            st.session_state.confirm_delete = None
            st.rerun()
        if cc2.button("Cancel", key=f"cancel_del_{entity_key}_{pk}"):
            st.session_state.confirm_delete = None
            st.rerun()
        return

    if st.session_state.form_mode and st.session_state.form_mode[1] == entity_key:
        render_form()
        return

    rows = database.query(conn, ent["list_sql"])

    # Toolbar setup safely avoiding column count mismatches
    num_filters = len(ent["filters"])
    cols_spec = [3] + [1] * num_filters + ([1] if can_create else [])
    toolbar = st.columns(cols_spec)
    
    search_val = toolbar[0].text_input(f"Search {ent['label'].lower()}\u2026",
                                        value=st.session_state.search.get(entity_key, ""),
                                        key=f"search_{entity_key}", label_visibility="collapsed",
                                        placeholder=f"Search {ent['label'].lower()}\u2026")
    st.session_state.search[entity_key] = search_val

    active = st.session_state.active_filters.setdefault(entity_key, {})
    for i, f in enumerate(ent["filters"]):
        active[f["key"]] = toolbar[i + 1].checkbox(f["label"], value=active.get(f["key"], False),
                                                     key=f"filter_{entity_key}_{f['key']}")

    if can_create:
        if toolbar[-1].button(f"+ Add {singular(ent['label'])}", key=f"add_{entity_key}", type="primary", use_container_width=True):
            st.session_state.form_mode = ("add", entity_key, None, None)
            st.rerun()

    if search_val.strip():
        t = search_val.strip().lower()
        rows = [r for r in rows if any(t in str(r.get(k, "") or "").lower() for k in ent["search_keys"])]
    for f in ent["filters"]:
        if active.get(f["key"]):
            rows = [r for r in rows if f["test"](r)]

    st.caption(f"{len(rows)} record{'s' if len(rows) != 1 else ''}")
    
    # CSV Download option right above table
    if rows:
        df_export = pd.DataFrame(rows)
        csv_bytes = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Download {ent['label']} as CSV",
            data=csv_bytes,
            file_name=f"{entity_key.lower()}_export.csv",
            mime="text/csv",
            key=f"download_btn_{entity_key}"
        )

    render_table(ent, rows, entity_key, can_update, can_delete)


def render_prescription_items(rx_id):
    st.markdown(f"""
    <div class="main-header">
        <h1>Items for Prescription #{rx_id}</h1>
        <p>Detailed breakdown of dispensed medicines.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("\u2190 All prescriptions"):
        st.session_state.drill = None
        st.rerun()

    rows = database.query(conn, """SELECT MedicineName, Quantity, pi.Dosage, Frequency, pi.Duration
                                    FROM PRESCRIPTION_ITEM pi JOIN MEDICINE m ON pi.MedicineID = m.MedicineID
                                    WHERE pi.PrescriptionID = ? ORDER BY pi.PrescriptionItemID""", (rx_id,))
    if not rows:
        st.info("No items dispensed yet on this prescription.")
    else:
        df_rx = pd.DataFrame(rows)
        st.dataframe(df_rx, use_container_width=True, hide_index=True)
        st.download_button("📥 Download Dispensing Items as CSV", df_rx.to_csv(index=False).encode('utf-8'), f"rx_{rx_id}_items.csv", "text/csv")


def render_purchase_items(po_id):
    st.markdown(f"""
    <div class="main-header">
        <h1>Items for Purchase Order #{po_id}</h1>
        <p>Detailed breakdown of received stock items.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("\u2190 All purchases"):
        st.session_state.drill = None
        st.rerun()

    rows = database.query(conn, """SELECT MedicineName, QuantityPurchased, UnitCost
                                    FROM PURCHASE_ITEM pi JOIN MEDICINE m ON pi.MedicineID = m.MedicineID
                                    WHERE pi.PurchaseID = ? ORDER BY pi.PurchaseItemID""", (po_id,))
    if not rows:
        st.info("No items received yet on this order.")
    else:
        df_po = pd.DataFrame(rows)
        st.dataframe(df_po, use_container_width=True, hide_index=True)
        st.download_button("📥 Download Purchase Items as CSV", df_po.to_csv(index=False).encode('utf-8'), f"po_{po_id}_items.csv", "text/csv")


def render_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>Pharmacy Dashboard</h1>
        <p>Real-time inventory metrics and stock alerts.</p>
    </div>
    """, unsafe_allow_html=True)

    med_count = database.query_one(conn, "SELECT COUNT(*) AS n FROM MEDICINE")["n"]
    cust_count = database.query_one(conn, "SELECT COUNT(*) AS n FROM CUSTOMER")["n"]
    rx_count = database.query_one(conn, "SELECT COUNT(*) AS n FROM PRESCRIPTION")["n"]
    stock_value = database.query_one(conn, "SELECT ROUND(SUM(UnitPrice*StockQuantity),2) AS v FROM MEDICINE")["v"] or 0
    low = database.query(conn, "SELECT * FROM View_LowStock")
    expiring = database.query(conn, "SELECT * FROM View_ExpiringMedicines")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Medicines tracked", med_count)
    c2.metric("Customers", cust_count)
    c3.metric("Prescriptions on file", rx_count)
    c4.metric("Stock value on hand", f"GHS {stock_value:,.2f}")
    c5.metric("Low-stock alerts", len(low))
    c6.metric("Expiring within 60 days", len(expiring))

    st.write("")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("\u211E Low stock \u2014 reorder soon")
        if low:
            st.table(low)
        else:
            st.info("Nothing is currently low on stock.")
    with col_b:
        st.subheader("\u211E Expiring or expired batches")
        if expiring:
            st.table(expiring)
        else:
            st.info("Nothing expiring in the next 60 days.")


def render_reports():
    st.markdown("""
    <div class="main-header">
        <h1>Operational Reports</h1>
        <p>Live database queries and analytical snapshots.</p>
    </div>
    """, unsafe_allow_html=True)

    reports = [
        ("Expiring Medicines", "View_ExpiringMedicines",
         "SELECT MedicineName AS Medicine, Category, ExpiryDate, StockQuantity, DaysToExpiry FROM View_ExpiringMedicines"),
        ("Low Stock Alert", "View_LowStock",
         "SELECT MedicineName AS Medicine, Category, StockQuantity FROM View_LowStock"),
        ("Sales Summary (by prescription)", "View_SalesSummary",
         'SELECT PrescriptionID AS "Rx#", PrescriptionDate AS Date, TotalItems AS "Items dispensed", '
         'TotalValue AS "Value (GHS)" FROM View_SalesSummary LIMIT 30'),
        ("Supplier Purchase History", "View_SupplierPurchaseHistory",
         'SELECT SupplierName AS Supplier, MedicineName AS Medicine, QuantityPurchased AS Qty, '
         'UnitCost AS "Unit cost", PurchaseDate AS Date FROM View_SupplierPurchaseHistory LIMIT 30'),
        ("Prescription History (by customer)", "View_PrescriptionHistory",
         "SELECT FirstName || ' ' || LastName AS Customer, PrescriptionDate AS Date, "
         "DosageInstructions AS Instructions, Duration, PharmacistName AS Pharmacist "
         "FROM View_PrescriptionHistory LIMIT 30"),
    ]
    
    for title, view_name, sql in reports:
        st.subheader(title)
        rows = database.query(conn, sql)
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                label=f"📥 Download {title} as CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"{view_name.lower()}_report.csv",
                mime="text/csv",
                key=f"download_{view_name}"
            )
        else:
            st.info("No rows.")
        st.divider()

section = st.session_state.section

if not can_read(st.session_state.role, section):
    st.title("Access restricted")
    st.warning(f"Your current role ({st.session_state.role}) doesn't have access to this section.")
elif st.session_state.drill is not None:
    drill_type, drill_id = st.session_state.drill
    if drill_type == "prescription_items":
        render_prescription_items(drill_id)
    else:
        render_purchase_items(drill_id)
elif section == "DASHBOARD":
    render_dashboard()
elif section == "REPORTS":
    render_reports()
else:
    render_entity(section)
