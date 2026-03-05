# This file simulates a database or external "source of truth" for the POC.
# In a production system, this data would come from live API calls to R3 and OneView.

# --- MASTER CLIENT RULEBOOK (Simulates the "Matrix" or SLA documentation) ---
# This defines the business rules for each client.
CLIENT_SLA_RULES = {
    # --- Previous Clients ---
    "ARVEST": {"SLA_DAYS": 5},
    "SUNTRUST": {"SLA_DAYS": 3},
    "CENLAR": {"SLA_DAYS": 5},
    "DEUTSCHE BANK": {"SLA_DAYS": 5}, 
    "NATIONSTAR MORTGAGE": {"SLA_DAYS": 5}, # Also Mr. Cooper
    "MR COOPER": {"SLA_DAYS": 5},
    "CHASE": {"SLA_DAYS": 5},
    "BANK OF OKLAHOMA": {"SLA_DAYS": 4},
    "CALIBER": {"SLA_DAYS": 5},
    "M&T": {"SLA_DAYS": 3},
    "MID AMERICA": {"SLA_DAYS": 5}, 
    "MORTGAGE SOLUTIONS": {"SLA_DAYS": 5}, 
    "PA EQUITY": {"SLA_DAYS": 5}, 
    "US BANCORP (SRVBRG)": {"SLA_DAYS": 5},
    "SLS": {"SLA_DAYS": 5}, # Specialized Loan Servicing
    "COMPULINK": {"SLA_DAYS": 5},
    "KEMNETZ, CHESTER R & DOROTHY R": {"SLA_DAYS": 99}, # Homeowner, M8 will fail
    "WELLS FARGO": {"SLA_DAYS": 5}, # From Doc 1043804695
}

# --- LOAN "ANSWER KEY" (Simulates data from R3 and OneView for the test loans) ---
# This contains the known-correct data for the specific PDFs being used in the POC.
LOAN_DATA_GROUND_TRUTH = {
    # --- PREVIOUS 22 ENTRIES ---
    "775308166": {
        "client": "Arvest",
        "situs_address": "6623 AR HWY 58, WILLIFORD AR 72482",
        "parcel_number": "001-02402-000",
        "expected_document_type": "CURRENT BILL ONLY", 
        "received_date": "2025-04-01" 
    },
    "4765727831": {
        "client": "Suntrust",
        "situs_address": "1001 SEMMES AV, RICHMOND, VA 23244", 
        "parcel_number": "12633887", 
        "expected_document_type": "DELINQUENT TAX BILL", 
        "received_date": "2025-06-04"
    },
     "6801001210442": {
        "client": "Deutsche Bank",
        "situs_address": "33 POTOMAC, FAIRVIEW HEIGHTS IL 62208",
        "parcel_number": "03-29.0-207-027",
        "expected_document_type": "ASSESSMENTS", 
        "received_date": "2025-03-26"
    },
    "3008881041": {
        "client": "Mr Cooper", 
        "situs_address": "0008411 WILSHIRE DR",
        "parcel_number": "171163", 
        "expected_document_type": "CURRENT BILL ONLY", 
        "received_date": "2025-01-08" 
    },
    "4028770763": {
        "client": "Chase",
        "situs_address": None, 
        "parcel_number": "09-23-319-004-0000",
        "expected_document_type": "CORRESPONDENCE", 
        "received_date": "2025-08-24" 
    },
    "431052539": {
        "client": "Mr Cooper", 
        "situs_address": "HIGHLAND CITY (1.19) 117B", 
        "parcel_number": "12410-000-000",
        "expected_document_type": "ASSESSMENTS", 
        "received_date": "2025-08-25" 
    },
    "683741532": {
        "client": "Mr Cooper",
        "situs_address": None, 
        "parcel_number": None, 
        "expected_document_type": "CORRESPONDENCE", 
        "received_date": "2025-07-29" 
    },
    "80383136": {
        "client": "Bank of Oklahoma",
        "situs_address": "75-5905 KUALII PL, KAILUA KONA HI 96740", 
        "parcel_number": "3-7-5-031-100-0000", 
        "expected_document_type": "DELINQUENT TAX BILL", 
        "received_date": "2025-08-26" 
    },
    "8679805402410": {
        "client": "Caliber", 
        "situs_address": "538 KING ST",
        "parcel_number": "R06-002",
        "expected_document_type": "LIEN RELATED", 
        "received_date": "2025-08-26" 
    },
    "717340467": {
        "client": "Mr Cooper",
        "situs_address": "2900 FLYING BLACKBIRD RD, BARTOW FL 33830-2981", 
        "parcel_number": "1117488.0000", 
        "expected_document_type": "REFUND - RECOVERY RELATED", 
        "received_date": "2025-10-18" 
    },
    "7428535": {
        "client": "M&T",
        "situs_address": None, 
        "parcel_number": None, 
        "expected_document_type": "CORRESPONDENCE", 
        "received_date": "2025-08-29" 
    },
    "150157973": {
        "client": "Mid America", 
        "situs_address": "627 S CONSTANTINE ST", 
        "parcel_number": "051 335 019 00", 
        "expected_document_type": "DELINQUENT TAX BILL", 
        "received_date": "2025-09-08" 
    },
    "38200110376": {
        "client": "Mortgage Solutions", 
        "situs_address": "3300 E GODDARD ST", 
        "parcel_number": None, 
        "expected_document_type": "CORRESPONDENCE", 
        "received_date": "2025-09-09" 
    },
    "59715976": {
        "client": "Arvest", 
        "situs_address": "78 WESTSIDE AVE, FREEPORT NY 11520", 
        "parcel_number": "62138 00380", 
        "expected_document_type": "PROOF OF PAYMENT", 
        "received_date": "2025-09-10" 
    },
    "737356444": {
        "client": "Mr Cooper", 
        "situs_address": "375 N BROOKING AVE, SMITH RIVER CA 95567", 
        "parcel_number": "103-041-003-000", 
        "expected_document_type": "CORRESPONDENCE", 
        "received_date": "2025-09-10" 
    },
    "732490206": {
        "client": "Mr Cooper", 
        "situs_address": "006101 DELMAR ST FAIRWAY, KS 66205-3233", 
        "parcel_number": "EF05400000-0010A", 
        "expected_document_type": "CORRESPONDENCE", 
        "received_date": "2025-09-11" 
    },
    "1260115F00235": {
        "client": "PA Equity", 
        "situs_address": "610 BRIGHTON WOODS RD", 
        "parcel_number": "1260115F00235", 
        "expected_document_type": "DELINQUENT TAX BILL", 
        "received_date": "2025-09-12" 
    },
    "9921174033": {
        "client": "US Bancorp (SrcBrg)",
        "situs_address": "2409 W BRITTON RD, OKLAHOMA CITY, OK 73120",
        "parcel_number": None,
        "expected_document_type": "TAX INFORMATION SHEET", 
        "received_date": "2025-08-04" 
    },
    "6841014322610": {
        "client": "SLS",
        "situs_address": "11816 CLARIDGE RD, WHEATON, MD 20902",
        "parcel_number": "3071248", 
        "expected_document_type": "CORRESPONDENCE", 
        "received_date": "2025-09-03" 
    },
    "052-8632022": {
        "client": "CompuLink",
        "situs_address": "4841 CARSON ST, DENVER CO 80239-4923",
        "parcel_number": "012 4113043000", 
        "expected_document_type": "CORRESPONDENCE", 
        "received_date": "2025-08-15" 
    },
    "05-06-104-023": {
        "client": "KEMNETZ, CHESTER R & DOROTHY R", 
        "situs_address": "117 MUIR DR, BELVIDERE, IL",
        "parcel_number": "05-06-104-023",
        "expected_document_type": "PROOF OF PAYMENT", 
        "received_date": "2025-05-21" 
    },
    "0625197306": {
        "client": "Mr. Cooper", 
        "situs_address": "104 ST ANDREWS CT, BLUE BELL PA 19422-1718",
        "parcel_number": "66-00-01116-00-1",
        "expected_document_type": "CORRESPONDENCE", 
        "received_date": "2024-11-01" 
    },

    # --- 2 NEW ENTRIES ADDED BELOW ---

    # Doc 1043493120.pdf
    "745783456": {
        "client": "Mr Cooper",
        "situs_address": None, # Not present in the email
        "parcel_number": None, # Not present in the email
        "expected_document_type": "CORRESPONDENCE", # Priority 12 (Email)
        "received_date": "2025-08-30" # From email "Sent" date
    },

    # Doc 1043588791.pdf
    "737406108": {
        "client": "Mr Cooper",
        "situs_address": "414 LOCUST ST", # From Page 2
        "parcel_number": "00,18-0622-000", # From "Parcel #" on Page 2
        "expected_document_type": "CORRESPONDENCE", # Priority 12 (Email) > Priority 30 (Current Bill)
        "received_date": "2025-08-30" # From email "Sent" date
    }
}

