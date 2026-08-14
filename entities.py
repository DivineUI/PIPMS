"""
entities.py
Declarative configuration for the generic CRUD screens, one entry per table.
This mirrors the original app's `ENTITIES` JS object: each entity carries
the SQL to list rows, the columns to show, the fields for the add/edit
form (including foreign-key dropdowns), and which fields are searchable.
"""

from datetime import date, timedelta


def is_soon_or_expired(date_str, days=60):
    if not date_str:
        return False
    try:
        d = date.fromisoformat(str(date_str))
    except ValueError:
        return False
    return (d - date.today()).days < days


def expiry_label(date_str):
    if not date_str:
        return "—"
    try:
        d = date.fromisoformat(str(date_str))
    except ValueError:
        return str(date_str)
    diff = (d - date.today()).days
    if diff < 0:
        return f"\U0001F534 {date_str} (expired {abs(diff)}d ago)"
    if diff <= 60:
        return f"\U0001F7E0 {date_str} ({diff}d left)"
    return f"\u2705 {date_str}"


def stock_label(qty):
    qty = qty or 0
    if qty == 0:
        return f"\U0001F534 {qty}"
    if qty < 10:
        return f"\U0001F7E0 {qty}"
    return f"\u2705 {qty}"


ENTITIES = {
    "MEDICINE": {
        "label": "Medicines",
        "pk": "MedicineID",
        "title": "Medicine Catalog & Stock",
        "desc": "Every medicine carried, with live stock, price and expiry.",
        "list_sql": """SELECT m.MedicineID, m.MedicineName, m.Category, m.Dosage, m.UnitPrice,
                              m.StockQuantity, m.ExpiryDate, s.SupplierName, m.SupplierID
                       FROM MEDICINE m LEFT JOIN SUPPLIER s ON m.SupplierID = s.SupplierID
                       ORDER BY m.MedicineName""",
        "columns": [
            {"key": "MedicineName", "label": "Medicine"},
            {"key": "Category", "label": "Category"},
            {"key": "Dosage", "label": "Dosage"},
            {"key": "UnitPrice", "label": "Price", "fmt": lambda v: f"GHS {float(v or 0):.2f}"},
            {"key": "StockQuantity", "label": "Stock", "fmt": stock_label},
            {"key": "ExpiryDate", "label": "Expiry", "fmt": expiry_label},
            {"key": "SupplierName", "label": "Supplier", "fmt": lambda v: v or "—"},
        ],
        "search_keys": ["MedicineName", "Category", "Dosage", "SupplierName"],
        "filters": [
            {"key": "low", "label": "Low stock (<10)", "test": lambda r: (r.get("StockQuantity") or 0) < 10},
            {"key": "exp", "label": "Expiring \u2264 60 days", "test": lambda r: is_soon_or_expired(r.get("ExpiryDate"))},
        ],
        "fields": [
            {"key": "MedicineName", "label": "Medicine name", "type": "text", "required": True},
            {"key": "Category", "label": "Category", "type": "text"},
            {"key": "Dosage", "label": "Dosage", "type": "text", "placeholder": "e.g. 500mg"},
            {"key": "UnitPrice", "label": "Unit price (GHS)", "type": "float", "step": 0.01, "min": 0.0, "required": True},
            {"key": "StockQuantity", "label": "Stock quantity", "type": "int", "step": 1, "min": 0, "required": True},
            {"key": "ExpiryDate", "label": "Expiry date", "type": "date", "required": True},
            {"key": "SupplierID", "label": "Supplier", "type": "fk", "fk_entity": "SUPPLIER",
             "fk_label_sql": "SupplierName", "fk_pk": "SupplierID"},
        ],
        "row_extra": None,
        "no_edit": False,
    },
    "SUPPLIER": {
        "label": "Suppliers",
        "pk": "SupplierID",
        "title": "Suppliers",
        "desc": "Companies that supply medicines to the pharmacy.",
        "list_sql": "SELECT * FROM SUPPLIER ORDER BY SupplierName",
        "columns": [
            {"key": "SupplierName", "label": "Supplier"},
            {"key": "ContactNumber", "label": "Contact"},
            {"key": "Address", "label": "Address"},
            {"key": "Email", "label": "Email"},
        ],
        "search_keys": ["SupplierName", "Address", "Email"],
        "filters": [],
        "fields": [
            {"key": "SupplierName", "label": "Supplier name", "type": "text", "required": True},
            {"key": "ContactNumber", "label": "Contact number", "type": "text", "required": True},
            {"key": "Address", "label": "Address", "type": "text"},
            {"key": "Email", "label": "Email", "type": "text"},
        ],
        "row_extra": None,
        "no_edit": False,
    },
    "CUSTOMER": {
        "label": "Customers",
        "pk": "CustomerID",
        "title": "Customers",
        "desc": "Patients the pharmacy has dispensed prescriptions to.",
        "list_sql": "SELECT * FROM CUSTOMER ORDER BY LastName, FirstName",
        "columns": [
            {"key": "FirstName", "label": "First name"},
            {"key": "LastName", "label": "Last name"},
            {"key": "ContactNumber", "label": "Contact"},
            {"key": "Address", "label": "Address"},
            {"key": "DateOfBirth", "label": "DOB"},
        ],
        "search_keys": ["FirstName", "LastName", "ContactNumber", "Address"],
        "filters": [],
        "fields": [
            {"key": "FirstName", "label": "First name", "type": "text", "required": True},
            {"key": "LastName", "label": "Last name", "type": "text", "required": True},
            {"key": "ContactNumber", "label": "Contact number", "type": "text", "required": True},
            {"key": "Address", "label": "Address", "type": "text"},
            {"key": "DateOfBirth", "label": "Date of birth", "type": "date", "required": False},
        ],
        "row_extra": None,
        "no_edit": False,
    },
    "PHARMACIST": {
        "label": "Pharmacists",
        "pk": "PharmacistID",
        "title": "Pharmacists & Staff",
        "desc": "Pharmacy staff who can be attached to a prescription.",
        "list_sql": "SELECT * FROM PHARMACIST ORDER BY Name",
        "columns": [
            {"key": "Name", "label": "Name"},
            {"key": "Position", "label": "Position"},
            {"key": "ContactNumber", "label": "Contact"},
            {"key": "Email", "label": "Email"},
        ],
        "search_keys": ["Name", "Position", "Email"],
        "filters": [],
        "fields": [
            {"key": "Name", "label": "Full name", "type": "text", "required": True},
            {"key": "Position", "label": "Position", "type": "text", "placeholder": "e.g. Pharmacist, Pharmacy Manager"},
            {"key": "ContactNumber", "label": "Contact number", "type": "text", "required": True},
            {"key": "Email", "label": "Email", "type": "text"},
        ],
        "row_extra": None,
        "no_edit": False,
    },
    "PRESCRIPTION": {
        "label": "Prescriptions",
        "pk": "PrescriptionID",
        "title": "Prescriptions",
        "desc": "One row per prescription written for a customer by a pharmacist.",
        "list_sql": """SELECT p.PrescriptionID, p.PrescriptionDate, p.DosageInstructions, p.Duration,
                              (c.FirstName || ' ' || c.LastName) AS CustomerName, ph.Name AS PharmacistName,
                              p.CustomerID, p.PharmacistID
                       FROM PRESCRIPTION p JOIN CUSTOMER c ON p.CustomerID = c.CustomerID
                       JOIN PHARMACIST ph ON p.PharmacistID = ph.PharmacistID
                       ORDER BY p.PrescriptionDate DESC, p.PrescriptionID DESC""",
        "columns": [
            {"key": "PrescriptionID", "label": "ID"},
            {"key": "PrescriptionDate", "label": "Date"},
            {"key": "CustomerName", "label": "Customer"},
            {"key": "PharmacistName", "label": "Pharmacist"},
            {"key": "DosageInstructions", "label": "Instructions"},
            {"key": "Duration", "label": "Duration"},
        ],
        "search_keys": ["CustomerName", "PharmacistName", "DosageInstructions"],
        "filters": [],
        "fields": [
            {"key": "PrescriptionDate", "label": "Prescription date", "type": "date", "required": True},
            {"key": "CustomerID", "label": "Customer", "type": "fk", "fk_entity": "CUSTOMER",
             "fk_label_sql": "FirstName || ' ' || LastName", "fk_pk": "CustomerID", "required": True},
            {"key": "PharmacistID", "label": "Pharmacist", "type": "fk", "fk_entity": "PHARMACIST",
             "fk_label_sql": "Name", "fk_pk": "PharmacistID", "required": True},
            {"key": "DosageInstructions", "label": "Dosage instructions", "type": "text"},
            {"key": "Duration", "label": "Duration", "type": "text", "placeholder": "e.g. 14 days"},
        ],
        "row_extra": "prescription_items",
        "no_edit": False,
    },
    "PRESCRIPTION_ITEM": {
        "label": "Dispensing Log",
        "pk": "PrescriptionItemID",
        "title": "Dispensing Log",
        "desc": ("Every medicine dispensed against a prescription. Adding a row automatically "
                 "deducts stock (and is blocked if the batch is expired or stock is insufficient)."),
        "list_sql": """SELECT pi.PrescriptionItemID, pi.PrescriptionID, m.MedicineName, pi.Quantity,
                              pi.Dosage, pi.Frequency, pi.Duration, pi.MedicineID
                       FROM PRESCRIPTION_ITEM pi JOIN MEDICINE m ON pi.MedicineID = m.MedicineID
                       ORDER BY pi.PrescriptionItemID DESC""",
        "columns": [
            {"key": "PrescriptionID", "label": "Rx #"},
            {"key": "MedicineName", "label": "Medicine"},
            {"key": "Quantity", "label": "Qty"},
            {"key": "Dosage", "label": "Dosage"},
            {"key": "Frequency", "label": "Frequency"},
            {"key": "Duration", "label": "Duration"},
        ],
        "search_keys": ["MedicineName"],
        "filters": [],
        "no_edit": True,
        "fields": [
            {"key": "PrescriptionID", "label": "Prescription", "type": "fk", "fk_entity": "PRESCRIPTION",
             "fk_label_sql": "'#' || PrescriptionID || ' \u2014 ' || PrescriptionDate", "fk_pk": "PrescriptionID", "required": True},
            {"key": "MedicineID", "label": "Medicine (stock shown)", "type": "fk", "fk_entity": "MEDICINE",
             "fk_label_sql": "MedicineName || '  (' || StockQuantity || ' in stock)'", "fk_pk": "MedicineID", "required": True},
            {"key": "Quantity", "label": "Quantity to dispense", "type": "int", "step": 1, "min": 1, "required": True},
            {"key": "Dosage", "label": "Dosage", "type": "text"},
            {"key": "Frequency", "label": "Frequency", "type": "text"},
            {"key": "Duration", "label": "Duration", "type": "text"},
        ],
        "row_extra": None,
    },
    "PURCHASE": {
        "label": "Purchases",
        "pk": "PurchaseID",
        "title": "Purchase Orders",
        "desc": "One row per purchase order placed with a supplier.",
        "list_sql": """SELECT p.PurchaseID, p.PurchaseDate, s.SupplierName, p.SupplierID
                       FROM PURCHASE p JOIN SUPPLIER s ON p.SupplierID = s.SupplierID
                       ORDER BY p.PurchaseDate DESC""",
        "columns": [
            {"key": "PurchaseID", "label": "ID"},
            {"key": "PurchaseDate", "label": "Date"},
            {"key": "SupplierName", "label": "Supplier"},
        ],
        "search_keys": ["SupplierName"],
        "filters": [],
        "fields": [
            {"key": "PurchaseDate", "label": "Purchase date", "type": "date", "required": True},
            {"key": "SupplierID", "label": "Supplier", "type": "fk", "fk_entity": "SUPPLIER",
             "fk_label_sql": "SupplierName", "fk_pk": "SupplierID", "required": True},
        ],
        "row_extra": "purchase_items",
        "no_edit": False,
    },
    "PURCHASE_ITEM": {
        "label": "Stock Receiving",
        "pk": "PurchaseItemID",
        "title": "Stock Receiving",
        "desc": "Line items received against a purchase order. Adding a row automatically increases stock.",
        "list_sql": """SELECT pi.PurchaseItemID, pi.PurchaseID, m.MedicineName, pi.QuantityPurchased,
                              pi.UnitCost, pi.MedicineID
                       FROM PURCHASE_ITEM pi JOIN MEDICINE m ON pi.MedicineID = m.MedicineID
                       ORDER BY pi.PurchaseItemID DESC""",
        "columns": [
            {"key": "PurchaseID", "label": "PO #"},
            {"key": "MedicineName", "label": "Medicine"},
            {"key": "QuantityPurchased", "label": "Qty"},
            {"key": "UnitCost", "label": "Unit cost", "fmt": lambda v: f"GHS {float(v or 0):.2f}"},
        ],
        "search_keys": ["MedicineName"],
        "filters": [],
        "no_edit": True,
        "fields": [
            {"key": "PurchaseID", "label": "Purchase order", "type": "fk", "fk_entity": "PURCHASE",
             "fk_label_sql": "'#' || PurchaseID || ' \u2014 ' || PurchaseDate", "fk_pk": "PurchaseID", "required": True},
            {"key": "MedicineID", "label": "Medicine", "type": "fk", "fk_entity": "MEDICINE",
             "fk_label_sql": "MedicineName", "fk_pk": "MedicineID", "required": True},
            {"key": "QuantityPurchased", "label": "Quantity received", "type": "int", "step": 1, "min": 1, "required": True},
            {"key": "UnitCost", "label": "Unit cost (GHS)", "type": "float", "step": 0.01, "min": 0.0, "required": True},
        ],
        "row_extra": None,
    },
}

NAV = [
    ("General", [("DASHBOARD", "Dashboard", "\U0001F4CA"), ("REPORTS", "Reports", "\U0001F4CB")]),
    ("Clinical", [("PRESCRIPTION", "Prescriptions", "\u211E"), ("PRESCRIPTION_ITEM", "Dispensing Log", "\U0001F489"),
                  ("CUSTOMER", "Customers", "\U0001F642")]),
    ("Inventory", [("MEDICINE", "Medicines", "\U0001F48A"), ("SUPPLIER", "Suppliers", "\U0001F69A"),
                   ("PURCHASE", "Purchases", "\U0001F4E5"), ("PURCHASE_ITEM", "Stock Receiving", "\U0001F4E4")]),
    ("Staff", [("PHARMACIST", "Pharmacists", "\U0001FA7A")]),
]

SINGULAR = {
    "Medicines": "Medicine", "Suppliers": "Supplier", "Customers": "Customer",
    "Pharmacists": "Pharmacist", "Prescriptions": "Prescription",
    "Dispensing Log": "Dispense Record", "Purchases": "Purchase",
    "Stock Receiving": "Received Item",
}


def singular(label):
    return SINGULAR.get(label, label)
