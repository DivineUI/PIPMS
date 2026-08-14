"""
permissions.py
Role-based access control.
Permission strings are any combination of c(create) r(read) u(update) d(delete).
An empty string means the role cannot see that section at all.
"""

ROLES = ["Admin", "Pharmacist", "Cashier", "Inventory Manager"]

PERMISSIONS = {
    "MEDICINE":          {"Admin": "crud", "Pharmacist": "r",   "Cashier": "r",  "Inventory Manager": "crud"},
    "SUPPLIER":          {"Admin": "crud", "Pharmacist": "",    "Cashier": "",   "Inventory Manager": "crud"},
    "CUSTOMER":          {"Admin": "crud", "Pharmacist": "cru", "Cashier": "cru", "Inventory Manager": "r"},
    "PHARMACIST":        {"Admin": "crud", "Pharmacist": "r",   "Cashier": "",   "Inventory Manager": ""},
    "PRESCRIPTION":      {"Admin": "crud", "Pharmacist": "cru", "Cashier": "r",  "Inventory Manager": "r"},
    "PRESCRIPTION_ITEM": {"Admin": "crud", "Pharmacist": "cr",  "Cashier": "cr", "Inventory Manager": "r"},
    "PURCHASE":          {"Admin": "crud", "Pharmacist": "",    "Cashier": "",   "Inventory Manager": "crud"},
    "PURCHASE_ITEM":     {"Admin": "crud", "Pharmacist": "",    "Cashier": "",   "Inventory Manager": "crud"},
    "REPORTS":           {"Admin": "r",    "Pharmacist": "r",   "Cashier": "r",  "Inventory Manager": "r"},
    "DASHBOARD":         {"Admin": "r",    "Pharmacist": "r",   "Cashier": "r",  "Inventory Manager": "r"},
}


def can(role: str, entity: str, action: str) -> bool:
    perms = PERMISSIONS.get(entity, {}).get(role, "")
    return action in perms


def can_read(role: str, entity: str) -> bool:
    return can(role, entity, "r")
