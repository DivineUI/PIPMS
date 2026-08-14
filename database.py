"""
database.py

Owns the SQLite schema, seed data, views, and triggers for the Pharmacy
Inventory & Prescription Management System.
"""

import sqlite3

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE CUSTOMER (
  CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
  FirstName VARCHAR(50) NOT NULL,
  LastName VARCHAR(50) NOT NULL,
  ContactNumber VARCHAR(20) NOT NULL,
  Address VARCHAR(100),
  DateOfBirth DATE
);

CREATE TABLE PHARMACIST (
  PharmacistID INTEGER PRIMARY KEY AUTOINCREMENT,
  Name VARCHAR(50) NOT NULL,
  ContactNumber VARCHAR(20) NOT NULL,
  Email VARCHAR(100) UNIQUE,
  Position VARCHAR(50)
);

CREATE TABLE SUPPLIER (
  SupplierID INTEGER PRIMARY KEY AUTOINCREMENT,
  SupplierName VARCHAR(100) NOT NULL,
  ContactNumber VARCHAR(20) NOT NULL,
  Address VARCHAR(100),
  Email VARCHAR(100) UNIQUE
);

CREATE TABLE MEDICINE (
  MedicineID INTEGER PRIMARY KEY AUTOINCREMENT,
  MedicineName VARCHAR(100) NOT NULL,
  Category VARCHAR(50),
  Dosage VARCHAR(50),
  UnitPrice DECIMAL(10,2) NOT NULL CHECK (UnitPrice >= 0),
  StockQuantity INTEGER NOT NULL DEFAULT 0 CHECK (StockQuantity >= 0),
  ExpiryDate DATE NOT NULL,
  SupplierID INTEGER,
  FOREIGN KEY (SupplierID) REFERENCES SUPPLIER(SupplierID)
    ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE PRESCRIPTION (
  PrescriptionID INTEGER PRIMARY KEY AUTOINCREMENT,
  PrescriptionDate DATE NOT NULL,
  DosageInstructions VARCHAR(255),
  Duration VARCHAR(50),
  CustomerID INTEGER NOT NULL,
  PharmacistID INTEGER NOT NULL,
  FOREIGN KEY (CustomerID) REFERENCES CUSTOMER(CustomerID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (PharmacistID) REFERENCES PHARMACIST(PharmacistID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE PRESCRIPTION_ITEM (
  PrescriptionItemID INTEGER PRIMARY KEY AUTOINCREMENT,
  PrescriptionID INTEGER NOT NULL,
  MedicineID INTEGER NOT NULL,
  Quantity INTEGER NOT NULL CHECK (Quantity > 0),
  Dosage VARCHAR(50),
  Frequency VARCHAR(50),
  Duration VARCHAR(50),
  FOREIGN KEY (PrescriptionID) REFERENCES PRESCRIPTION(PrescriptionID)
    ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (MedicineID) REFERENCES MEDICINE(MedicineID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE PURCHASE (
  PurchaseID INTEGER PRIMARY KEY AUTOINCREMENT,
  PurchaseDate DATE NOT NULL,
  SupplierID INTEGER NOT NULL,
  FOREIGN KEY (SupplierID) REFERENCES SUPPLIER(SupplierID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE PURCHASE_ITEM (
  PurchaseItemID INTEGER PRIMARY KEY AUTOINCREMENT,
  PurchaseID INTEGER NOT NULL,
  MedicineID INTEGER NOT NULL,
  QuantityPurchased INTEGER NOT NULL CHECK (QuantityPurchased > 0),
  UnitCost DECIMAL(10,2) NOT NULL CHECK (UnitCost >= 0),
  FOREIGN KEY (PurchaseID) REFERENCES PURCHASE(PurchaseID)
    ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (MedicineID) REFERENCES MEDICINE(MedicineID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_medicine_name ON MEDICINE(MedicineName);
CREATE INDEX idx_medicine_expiry ON MEDICINE(ExpiryDate);
CREATE INDEX idx_prescription_date ON PRESCRIPTION(PrescriptionDate);
CREATE INDEX idx_customer_lastname ON CUSTOMER(LastName);
"""

SEED_SQL = """
INSERT INTO SUPPLIER (SupplierName, ContactNumber, Address, Email) VALUES
('MedPlus Distributors Ltd', '0302-551-201', '12 Independence Ave, Accra', 'orders@medplus-dist.com'),
('PharmaCare Wholesale', '0302-551-202', '8 Ring Road East, Accra', 'sales@pharmacarewholesale.com'),
('GlobalMeds Supply Co.', '0302-551-203', '45 Spintex Road, Accra', 'contact@globalmedsupply.com'),
('HealthLink Distributors', '0302-551-204', '19 Liberation Road, Accra', 'info@healthlinkdist.com'),
('Accra Pharma Wholesalers', '0302-551-205', '3 Kojo Thompson Rd, Accra', 'orders@accrapharma.com'),
('Continental Drug House', '0302-551-206', '77 Osu Oxford St, Accra', 'sales@continentaldrug.com'),
('Unity Pharmaceuticals Supply', '0302-551-207', '5 Tema Station Rd, Accra', 'supply@unitypharma.com'),
('Westgate Medical Imports', '0302-551-208', '22 Achimota Rd, Accra', 'info@westgatemedical.com'),
('Kumasi Pharma Traders', '0322-551-209', '14 Adum High St, Kumasi', 'orders@kumasipharma.com'),
('BlueCross Pharma Supply', '0302-551-210', '9 Cantonments Rd, Accra', 'sales@bluecrosspharma.com'),
('Everwell Distributors', '0302-551-211', '31 Dansoman Rd, Accra', 'contact@everwelldist.com'),
('Sunrise Pharmaceuticals Ltd', '0302-551-212', '6 East Legon Blvd, Accra', 'info@sunrisepharma.com'),
('National Drug Supply Co.', '0302-551-213', '2 Ministries Rd, Accra', 'orders@nationaldrugco.com'),
('Coastal Meds Wholesale', '0312-551-214', '10 Beach Rd, Takoradi', 'sales@coastalmeds.com'),
('Prime Health Distributors', '0302-551-215', '17 Airport Bypass, Accra', 'info@primehealthdist.com'),
('Zenith Pharma Imports', '0302-551-216', '40 Labone Crescent, Accra', 'contact@zenithpharma.com'),
('TrustMed Supply Chain', '0302-551-217', '25 Haatso Rd, Accra', 'orders@trustmedsupply.com'),
('Golden Star Pharmaceuticals', '0332-551-218', '8 Sunyani High St, Sunyani', 'sales@goldenstarpharma.com'),
('Radiant Health Imports', '0302-551-219', '13 Madina Market Rd, Accra', 'info@radianthealth.com'),
('Apex Pharma Wholesale', '0302-551-220', '29 Circle Rd, Accra', 'orders@apexpharma.com'),
('Reliable Drug Distributors', '0302-551-221', '16 Teshie Rd, Accra', 'sales@reliabledrug.com'),
('Horizon Medical Supply', '0372-551-222', '4 Tamale Central, Tamale', 'contact@horizonmedsupply.com');

INSERT INTO MEDICINE (MedicineName, Category, Dosage, UnitPrice, StockQuantity, ExpiryDate, SupplierID) VALUES
('Amoxicillin', 'Antibiotic', '500mg', 0.45, 420, '2028-01-30', 3),
('Paracetamol', 'Painkiller', '500mg', 0.10, 1200, '2028-07-28', 1),
('Ibuprofen', 'Painkiller', '400mg', 0.15, 850, '2028-05-29', 1),
('Metformin', 'Antidiabetic', '500mg', 0.30, 300, '2027-12-01', 5),
('Amlodipine', 'Antihypertensive', '5mg', 0.35, 260, '2027-12-21', 5),
('Loratadine', 'Antihistamine', '10mg', 0.25, 180, '2027-09-12', 7),
('Cetirizine', 'Antihistamine', '10mg', 0.22, 210, '2027-10-02', 7),
('Omeprazole', 'Antacid / PPI', '20mg', 0.40, 190, '2027-08-23', 9),
('Ranitidine', 'Antacid', '150mg', 0.28, 0, '2026-09-02', 9),
('Ciprofloxacin', 'Antibiotic', '500mg', 0.55, 5, '2026-09-17', 3),
('Azithromycin', 'Antibiotic', '250mg', 0.75, 140, '2027-06-04', 3),
('Salbutamol Inhaler', 'Bronchodilator', '100mcg', 3.20, 60, '2027-04-15', 11),
('Vitamin C', 'Vitamin/Supplement', '500mg', 0.12, 500, '2029-01-24', 12),
('Multivitamin Complex', 'Vitamin/Supplement', 'Tablet', 0.20, 430, '2028-10-16', 12),
('Diclofenac', 'Painkiller / NSAID', '50mg', 0.18, 310, '2027-11-11', 1),
('Insulin Glargine', 'Antidiabetic', '100 IU/mL', 12.50, 8, '2026-10-07', 5),
('Losartan', 'Antihypertensive', '50mg', 0.38, 220, '2027-12-21', 5),
('Metronidazole', 'Antibiotic', '400mg', 0.20, 0, '2026-08-23', 3),
('Doxycycline', 'Antibiotic', '100mg', 0.32, 150, '2027-08-23', 3),
('Hydrochlorothiazide', 'Antihypertensive', '25mg', 0.18, 200, '2027-11-01', 5),
('Aspirin', 'Painkiller / Antiplatelet', '75mg', 0.08, 700, '2029-01-24', 1),
('Prednisolone', 'Corticosteroid', '5mg', 0.26, 90, '2026-07-29', 9),
('Folic Acid', 'Vitamin/Supplement', '5mg', 0.10, 260, '2028-07-28', 12),
('Artemether/Lumefantrine', 'Antimalarial', '20/120mg', 1.80, 320, '2027-06-04', 16),
('Chlorpheniramine', 'Antihistamine', '4mg', 0.12, 12, '2026-08-03', 7),
('Simvastatin', 'Antilipidemic', '20mg', 0.34, 175, '2027-12-21', 5),
('Co-trimoxazole', 'Antibiotic', '480mg', 0.24, 3, '2026-08-28', 3),
('ORS Sachets', 'Rehydration', 'Sachet', 0.15, 640, '2028-05-09', 19),
('Zinc Sulfate', 'Vitamin/Supplement', '20mg', 0.14, 380, '2028-07-08', 12),
('Cough Syrup (Dextromethorphan)', 'Cold & Flu', '100ml bottle', 1.10, 95, '2027-02-24', 19);

INSERT INTO CUSTOMER (FirstName, LastName, ContactNumber, Address, DateOfBirth) VALUES
('Ama', 'Ofori', '024-100-2000', '10 Ring Road St, Accra', '1955-01-01'),
('Kwame', 'Adjei', '024-101-2001', '11 Spintex St, Accra', '1958-02-02'),
('Efua', 'Antwi', '024-102-2002', '12 Dansoman St, Accra', '1961-03-03'),
('Kojo', 'Yeboah', '024-103-2003', '13 East Legon St, Accra', '1964-04-04'),
('Akosua', 'Aidoo', '024-104-2004', '14 Achimota St, Accra', '1967-05-05'),
('Yaw', 'Lartey', '024-105-2005', '15 Tesano St, Accra', '1970-06-06'),
('Abena', 'Mensah', '024-106-2006', '16 Adenta St, Accra', '1973-07-07'),
('Kofi', 'Asante', '024-107-2007', '17 Madina St, Accra', '1976-08-08'),
('Adjoa', 'Agyeman', '024-108-2008', '18 Labone St, Accra', '1979-09-09'),
('Kwabena', 'Amoah', '024-109-2009', '19 Osu St, Accra', '1982-10-10'),
('Esi', 'Sarpong', '024-110-2010', '20 Ring Road St, Accra', '1985-11-11'),
('Kwesi', 'Baffour', '024-111-2011', '21 Spintex St, Accra', '1988-12-12'),
('Afia', 'Nkrumah', '024-112-2012', '22 Dansoman St, Accra', '1991-01-13'),
('Yaw', 'Tetteh', '024-113-2013', '23 East Legon St, Accra', '1994-02-14'),
('Abena', 'Bonsu', '024-114-2014', '24 Achimota St, Accra', '1997-03-15'),
('Nana', 'Boateng', '024-115-2015', '25 Tesano St, Accra', '2000-04-16'),
('Adwoa', 'Osei', '024-116-2016', '26 Adenta St, Accra', '2003-05-17'),
('Kwaku', 'Darko', '024-117-2017', '27 Madina St, Accra', '2006-06-18'),
('Akua', 'Frimpong', '024-118-2018', '28 Labone St, Accra', '2009-07-19'),
('Fiifi', 'Acheampong', '024-119-2019', '29 Osu St, Accra', '1957-08-20'),
('Gifty', 'Gyasi', '024-120-2020', '30 Ring Road St, Accra', '1960-09-21'),
('Emmanuel', 'Quaye', '024-121-2021', '31 Spintex St, Accra', '1963-10-22'),
('Comfort', 'Addo', '024-122-2022', '32 Dansoman St, Accra', '1966-11-23'),
('Samuel', 'Owusu', '024-123-2023', '33 East Legon St, Accra', '1969-12-24'),
('Mercy', 'Appiah', '024-124-2024', '34 Achimota St, Accra', '1972-01-25'),
('Daniel', 'Ofori', '024-125-2025', '35 Tesano St, Accra', '1975-02-26'),
('Grace', 'Adjei', '024-126-2026', '36 Adenta St, Accra', '1978-03-27'),
('Isaac', 'Antwi', '024-127-2027', '37 Madina St, Accra', '1981-04-01');

INSERT INTO PHARMACIST (Name, ContactNumber, Email, Position) VALUES
('Nana Owusu', '020-300-4000', 'nana.owusu0@pipms-pharmacy.com', 'Pharmacist'),
('Kwabena Darko', '020-301-4001', 'kwabena.darko1@pipms-pharmacy.com', 'Senior Pharmacist'),
('Abena Kusi', '020-302-4002', 'abena.kusi2@pipms-pharmacy.com', 'Pharmacy Technician'),
('Yaw Twum', '020-303-4003', 'yaw.twum3@pipms-pharmacy.com', 'Intern Pharmacist'),
('Adwoa Owusu', '020-304-4004', 'adwoa.owusu4@pipms-pharmacy.com', 'Pharmacy Manager'),
('Kofi Darko', '020-305-4005', 'kofi.darko5@pipms-pharmacy.com', 'Pharmacist'),
('Akosua Kusi', '020-306-4006', 'akosua.kusi6@pipms-pharmacy.com', 'Senior Pharmacist'),
('Kwame Twum', '020-307-4007', 'kwame.twum7@pipms-pharmacy.com', 'Pharmacy Technician'),
('Efua Owusu', '020-308-4008', 'efua.owusu8@pipms-pharmacy.com', 'Intern Pharmacist'),
('Kwesi Darko', '020-309-4009', 'kwesi.darko9@pipms-pharmacy.com', 'Pharmacy Manager'),
('Gifty Kusi', '020-310-4010', 'gifty.kusi10@pipms-pharmacy.com', 'Pharmacist'),
('Samuel Twum', '020-311-4011', 'samuel.twum11@pipms-pharmacy.com', 'Senior Pharmacist'),
('Grace Owusu', '020-312-4012', 'grace.owusu12@pipms-pharmacy.com', 'Pharmacy Technician'),
('Emmanuel Darko', '020-313-4013', 'emmanuel.darko13@pipms-pharmacy.com', 'Intern Pharmacist'),
('Comfort Kusi', '020-314-4014', 'comfort.kusi14@pipms-pharmacy.com', 'Pharmacy Manager'),
('Isaac Twum', '020-315-4015', 'isaac.twum15@pipms-pharmacy.com', 'Pharmacist'),
('Mercy Owusu', '020-316-4016', 'mercy.owusu16@pipms-pharmacy.com', 'Senior Pharmacist'),
('Daniel Darko', '020-317-4017', 'daniel.darko17@pipms-pharmacy.com', 'Pharmacy Technician'),
('Patience Kusi', '020-318-4018', 'patience.kusi18@pipms-pharmacy.com', 'Intern Pharmacist'),
('Joseph Twum', '020-319-4019', 'joseph.twum19@pipms-pharmacy.com', 'Pharmacy Manager');

INSERT INTO PRESCRIPTION (PrescriptionDate, DosageInstructions, Duration, CustomerID, PharmacistID) VALUES
('2026-08-03', '1 tablet in the morning', '30 days', 5, 4),
('2026-07-25', '1 capsule at bedtime', '3 days', 19, 11),
('2026-07-16', '2 tablets twice daily', '5 days', 6, 18),
('2026-07-07', '1 capsule at bedtime', '21 days', 4, 5),
('2026-06-28', '5ml three times daily', '5 days', 6, 12),
('2026-06-19', '1 capsule at bedtime', '21 days', 8, 19),
('2026-06-10', '2 tablets twice daily', '14 days', 7, 6),
('2026-06-01', '5ml three times daily', '14 days', 3, 13),
('2026-05-23', '1 tablet in the morning', '7 days', 15, 20),
('2026-05-14', '1 tablet in the morning', '10 days', 8, 7),
('2026-05-05', '1 capsule at bedtime', '3 days', 4, 14),
('2026-04-26', '5ml three times daily', '3 days', 5, 1),
('2026-04-17', '2 tablets twice daily', '30 days', 14, 8),
('2026-04-08', '1 tablet every 8 hours', '30 days', 1, 15),
('2026-03-30', '1 capsule at bedtime', '7 days', 23, 2),
('2026-03-21', '1 tablet twice daily with water', '14 days', 1, 9),
('2026-03-12', '5ml three times daily', '3 days', 1, 16),
('2026-03-03', '1 capsule at bedtime', '3 days', 27, 3),
('2026-02-22', '1 tablet in the morning', '21 days', 3, 10),
('2026-02-13', '1 tablet after meals', '7 days', 2, 17),
('2026-02-04', '1 tablet after meals', '21 days', 20, 4),
('2026-01-26', '1 tablet in the morning', '14 days', 4, 11),
('2026-01-17', '5ml three times daily', '5 days', 5, 18),
('2026-01-08', '1 capsule at bedtime', '30 days', 25, 5),
('2025-12-30', '1 tablet in the morning', '7 days', 2, 12),
('2025-12-21', '1 tablet twice daily with water', '14 days', 16, 19),
('2025-12-12', '1 tablet twice daily with water', '7 days', 1, 6),
('2025-12-03', '5ml three times daily', '7 days', 13, 13),
('2025-11-24', '1 capsule at bedtime', '3 days', 4, 20),
('2025-11-15', '5ml three times daily', '3 days', 7, 7);

INSERT INTO PRESCRIPTION_ITEM (PrescriptionID, MedicineID, Quantity, Dosage, Frequency, Duration) VALUES
(1, 14, 14, '1 tablet in the morning', 'Twice daily', '7 days'),
(1, 29, 30, '1 tablet twice daily with water', 'Once daily', '21 days'),
(1, 19, 1, '2 tablets twice daily', 'Twice daily', '3 days'),
(2, 26, 14, '2 tablets twice daily', 'Every 8 hours', '14 days'),
(3, 15, 30, '1 tablet after meals', 'Every 12 hours', '3 days'),
(3, 17, 1, '5ml three times daily', 'Every 12 hours', '10 days'),
(3, 9, 1, '5ml three times daily', 'Every 8 hours', '7 days'),
(4, 1, 5, '1 tablet every 8 hours', 'As needed', '5 days'),
(4, 24, 5, '1 capsule at bedtime', 'Twice daily', '10 days'),
(5, 18, 30, '1 tablet after meals', 'As needed', '10 days'),
(6, 1, 10, '5ml three times daily', 'Twice daily', '5 days'),
(6, 4, 3, '2 tablets twice daily', 'Once daily', '3 days'),
(7, 27, 30, '1 tablet every 8 hours', 'Twice daily', '3 days'),
(7, 3, 20, '1 tablet every 8 hours', 'Three times daily', '30 days'),
(8, 14, 30, '1 capsule at bedtime', 'Every 12 hours', '10 days'),
(8, 7, 14, '1 tablet in the morning', 'Every 8 hours', '30 days'),
(8, 30, 20, '2 tablets twice daily', 'Twice daily', '7 days'),
(9, 11, 1, '1 capsule at bedtime', 'As needed', '7 days'),
(10, 3, 1, '1 capsule at bedtime', 'Once daily', '5 days'),
(11, 3, 3, '5ml three times daily', 'Every 12 hours', '14 days'),
(11, 17, 3, '1 tablet every 8 hours', 'Every 12 hours', '30 days'),
(12, 16, 20, '2 puffs as needed', 'Twice daily', '5 days'),
(12, 8, 1, '2 puffs as needed', 'Three times daily', '14 days'),
(12, 26, 14, '1 tablet twice daily with water', 'Every 12 hours', '5 days'),
(13, 2, 14, '1 tablet in the morning', 'Once daily', '7 days'),
(14, 7, 30, '1 tablet twice daily with water', 'Twice daily', '14 days'),
(15, 9, 20, '1 capsule at bedtime', 'Once daily', '14 days'),
(16, 4, 30, '1 tablet after meals', 'Once daily', '21 days'),
(16, 2, 3, '1 tablet every 8 hours', 'Every 8 hours', '14 days'),
(16, 21, 20, '1 capsule at bedtime', 'Every 8 hours', '5 days'),
(17, 13, 1, '2 puffs as needed', 'Three times daily', '21 days'),
(18, 10, 30, '1 tablet twice daily with water', 'Twice daily', '7 days'),
(18, 14, 5, '1 capsule at bedtime', 'Once daily', '30 days'),
(19, 2, 1, '1 tablet after meals', 'As needed', '14 days'),
(19, 24, 30, '1 tablet every 8 hours', 'Once daily', '30 days'),
(19, 11, 1, '1 tablet every 8 hours', 'Once daily', '30 days'),
(20, 22, 3, '2 puffs as needed', 'Once daily', '30 days'),
(21, 19, 1, '2 tablets twice daily', 'Every 8 hours', '3 days'),
(22, 19, 5, '1 capsule at bedtime', 'Every 12 hours', '3 days'),
(22, 17, 10, '1 capsule at bedtime', 'Three times daily', '14 days'),
(22, 11, 2, '5ml three times daily', 'Every 8 hours', '10 days'),
(23, 8, 5, '1 tablet twice daily with water', 'Once daily', '14 days'),
(23, 4, 10, '1 tablet after meals', 'Every 8 hours', '5 days'),
(24, 6, 20, '1 capsule at bedtime', 'Every 12 hours', '7 days'),
(24, 30, 5, '1 tablet in the morning', 'Once daily', '10 days'),
(25, 3, 3, '2 puffs as needed', 'Every 8 hours', '3 days'),
(25, 16, 10, '1 tablet every 8 hours', 'Three times daily', '21 days'),
(26, 21, 20, '1 tablet twice daily with water', 'Once daily', '14 days'),
(27, 4, 1, '1 capsule at bedtime', 'As needed', '7 days'),
(27, 9, 3, '5ml three times daily', 'Every 12 hours', '7 days'),
(28, 12, 5, '2 puffs as needed', 'Twice daily', '7 days'),
(29, 25, 1, '1 tablet every 8 hours', 'Once daily', '3 days'),
(29, 20, 20, '1 tablet after meals', 'Every 8 hours', '30 days'),
(30, 5, 5, '1 tablet in the morning', 'Once daily', '10 days'),
(30, 14, 3, '1 capsule at bedtime', 'Every 12 hours', '5 days'),
(30, 2, 10, '2 puffs as needed', 'As needed', '3 days');

INSERT INTO PURCHASE (PurchaseDate, SupplierID) VALUES
('2026-07-29', 3), ('2026-07-18', 7), ('2026-07-07', 11), ('2026-06-26', 15), ('2026-06-15', 19),
('2026-06-04', 1), ('2026-05-24', 5), ('2026-05-13', 9), ('2026-05-02', 13), ('2026-04-21', 17),
('2026-04-10', 21), ('2026-03-30', 3), ('2026-03-19', 7), ('2026-03-08', 11), ('2026-02-25', 15),
('2026-02-14', 19), ('2026-02-03', 1), ('2026-01-23', 5), ('2026-01-12', 9), ('2026-01-01', 13),
('2025-12-21', 17), ('2025-12-10', 21), ('2025-11-29', 3), ('2025-11-18', 7), ('2025-11-07', 11);

INSERT INTO PURCHASE_ITEM (PurchaseID, MedicineID, QuantityPurchased, UnitCost) VALUES
(1, 30, 500, 0.64), (1, 8, 500, 0.28), (2, 1, 150, 0.32), (2, 6, 200, 0.18), (2, 24, 500, 1.25),
(3, 9, 500, 0.19), (3, 6, 200, 0.18), (4, 8, 200, 0.25), (4, 7, 500, 0.16), (4, 27, 100, 0.14),
(5, 13, 150, 0.09), (5, 11, 500, 0.45), (6, 22, 150, 0.19), (6, 27, 50, 0.17), (6, 18, 150, 0.12),
(7, 2, 250, 0.06), (7, 4, 300, 0.21), (8, 20, 200, 0.13), (8, 17, 100, 0.23), (8, 4, 300, 0.19),
(9, 12, 50, 2.37), (9, 14, 150, 0.13), (10, 24, 150, 1.17), (11, 11, 150, 0.50), (11, 13, 100, 0.08),
(11, 23, 200, 0.07), (12, 20, 150, 0.11), (12, 19, 500, 0.18), (13, 7, 500, 0.15), (13, 14, 300, 0.12),
(14, 15, 250, 0.12), (14, 22, 500, 0.18), (14, 7, 300, 0.12), (15, 3, 500, 0.09), (15, 27, 150, 0.14),
(16, 5, 50, 0.21), (16, 1, 200, 0.30), (17, 15, 200, 0.13), (18, 23, 200, 0.06), (18, 13, 100, 0.08),
(19, 29, 500, 0.10), (20, 25, 200, 0.07), (21, 2, 500, 0.06), (21, 18, 100, 0.14), (21, 8, 300, 0.26),
(22, 25, 200, 0.08), (22, 29, 300, 0.10), (23, 27, 200, 0.18), (23, 30, 300, 0.79), (23, 18, 200, 0.12),
(24, 27, 150, 0.17), (24, 21, 250, 0.05), (25, 9, 50, 0.19), (25, 15, 100, 0.11);
"""

VIEWS_SQL = """
CREATE VIEW View_ExpiringMedicines AS
SELECT MedicineID, MedicineName, Category, ExpiryDate, StockQuantity,
       CAST(julianday(ExpiryDate) - julianday('now') AS INTEGER) AS DaysToExpiry
FROM MEDICINE WHERE ExpiryDate < date('now','+60 day')
ORDER BY ExpiryDate;

CREATE VIEW View_LowStock AS
SELECT MedicineID, MedicineName, Category, StockQuantity
FROM MEDICINE WHERE StockQuantity < 10
ORDER BY StockQuantity;

CREATE VIEW View_SalesSummary AS
SELECT p.PrescriptionID, p.PrescriptionDate, SUM(pi.Quantity) AS TotalItems,
       ROUND(SUM(pi.Quantity * m.UnitPrice), 2) AS TotalValue
FROM PRESCRIPTION_ITEM pi
JOIN PRESCRIPTION p ON pi.PrescriptionID = p.PrescriptionID
JOIN MEDICINE m ON pi.MedicineID = m.MedicineID
GROUP BY p.PrescriptionID
ORDER BY p.PrescriptionDate DESC;

CREATE VIEW View_SupplierPurchaseHistory AS
SELECT s.SupplierID, s.SupplierName, m.MedicineName, pi.QuantityPurchased, pi.UnitCost, p.PurchaseDate
FROM SUPPLIER s
JOIN PURCHASE p ON s.SupplierID = p.SupplierID
JOIN PURCHASE_ITEM pi ON p.PurchaseID = pi.PurchaseID
JOIN MEDICINE m ON pi.MedicineID = m.MedicineID
ORDER BY p.PurchaseDate DESC;

CREATE VIEW View_PrescriptionHistory AS
SELECT c.CustomerID, c.FirstName, c.LastName, p.PrescriptionID, p.PrescriptionDate,
       p.DosageInstructions, p.Duration, ph.Name AS PharmacistName
FROM CUSTOMER c
JOIN PRESCRIPTION p ON c.CustomerID = p.CustomerID
JOIN PHARMACIST ph ON p.PharmacistID = ph.PharmacistID
ORDER BY p.PrescriptionDate DESC;
"""

# Audit table + the business-rule triggers. Created AFTER seeding so the
# historical seed rows aren't double-counted against StockQuantity.
TRIGGERS_SQL = """
CREATE TABLE AUDIT_LOG (
  AuditID INTEGER PRIMARY KEY AUTOINCREMENT,
  TableName VARCHAR(50),
  Action VARCHAR(20),
  RecordID INTEGER,
  Details VARCHAR(255),
  ChangedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_BlockExpiredDispense
BEFORE INSERT ON PRESCRIPTION_ITEM
FOR EACH ROW
WHEN (SELECT ExpiryDate FROM MEDICINE WHERE MedicineID = NEW.MedicineID) < date('now')
BEGIN
  SELECT RAISE(ABORT, 'Cannot dispense: this medicine batch has expired');
END;

CREATE TRIGGER trg_BlockInsufficientStock
BEFORE INSERT ON PRESCRIPTION_ITEM
FOR EACH ROW
WHEN (SELECT StockQuantity FROM MEDICINE WHERE MedicineID = NEW.MedicineID) < NEW.Quantity
BEGIN
  SELECT RAISE(ABORT, 'Cannot dispense: not enough stock on hand');
END;

CREATE TRIGGER trg_AutoUpdateStockOnDispense
AFTER INSERT ON PRESCRIPTION_ITEM
FOR EACH ROW
BEGIN
  UPDATE MEDICINE SET StockQuantity = StockQuantity - NEW.Quantity WHERE MedicineID = NEW.MedicineID;
  INSERT INTO AUDIT_LOG (TableName, Action, RecordID, Details)
  VALUES ('MEDICINE', 'DISPENSE', NEW.MedicineID, 'Stock reduced by ' || NEW.Quantity || ' via prescription #' || NEW.PrescriptionID);
END;

CREATE TRIGGER trg_AutoUpdateStockOnPurchase
AFTER INSERT ON PURCHASE_ITEM
FOR EACH ROW
BEGIN
  UPDATE MEDICINE SET StockQuantity = StockQuantity + NEW.QuantityPurchased WHERE MedicineID = NEW.MedicineID;
  INSERT INTO AUDIT_LOG (TableName, Action, RecordID, Details)
  VALUES ('MEDICINE', 'RESTOCK', NEW.MedicineID, 'Stock increased by ' || NEW.QuantityPurchased || ' via purchase #' || NEW.PurchaseID);
END;
"""


def build_connection() -> sqlite3.Connection:
    """Create a fresh, fully-seeded in-memory database for one user session."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_SQL)
    conn.executescript(VIEWS_SQL)
    conn.executescript(TRIGGERS_SQL)
    conn.commit()
    return conn


def query(conn: sqlite3.Connection, sql: str, params=()):
    """Run a SELECT and return a list of plain dicts."""
    cur = conn.execute(sql, params)
    return [dict(row) for row in cur.fetchall()]


def query_one(conn: sqlite3.Connection, sql: str, params=()):
    rows = query(conn, sql, params)
    return rows[0] if rows else None


def execute(conn: sqlite3.Connection, sql: str, params=()):
    """Run an INSERT/UPDATE/DELETE. Raises sqlite3.Error on failure."""
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.lastrowid
