
import re
from datetime import datetime, date
import logging
from typing import List, Dict, Optional, Tuple, Any
from data_source import CLIENT_SLA_RULES


# --- Constants ---
class DocTypes:
    """Document type constants to avoid hardcoded strings"""
    INACTIVE_LOAN = "INACTIVE LOAN"
    TAX_SALE = "TAX SALE"
    FORECLOSURES = "FORECLOSURES"
    LEGAL_CORRESPONDENCE = "LEGAL CORRESPONDENCE"
    LIEN_RELATED = "LIEN RELATED"
    CODE_VIOLATION = "CODE VIOLATION"
    DELINQUENT_TAX_BILL = "DELINQUENT TAX BILL"
    SUPPLEMENTAL_DELINQUENT = "SUPPLEMENTAL - DELINQUENT"
    PROPERTY_TAX_RESEARCH = "PROPERTY TAX RESEARCH"
    AUTHORIZATION_LETTER = "AUTHORIZATION LETTER"
    REFUND_RECOVERY = "REFUND - RECOVERY RELATED"
    CORRESPONDENCE = "CORRESPONDENCE"
    NJ_CERTIFICATES = "NJ CERTIFICATES"
    ASSESSMENTS = "ASSESSMENTS"
    ESCROW_ANALYSIS = "ESCROW ANALYSIS"
    EXEMPTION = "EXEMPTION"
    WI_PAYMENT_OPTION = "WI PAYMENT OPTION"
    OPTION_LETTER_NOT_WI = "OPTION LETTER - NOT WI"
    FIRE_DISTRICT = "FIRE DISTRICT RELATED"
    INSURANCE = "INSURANCE"
    PROOF_OF_PAYMENT = "PROOF OF PAYMENT"
    HOA = "HOA"
    UNSECURED_BILL = "UNSECURED BILL"
    NON_TAX_CORRESPONDENCE = "NON TAX CORRESPONDENCE"
    TAX_INFO_SHEET = "TAX INFORMATION SHEET"
    CORRECTED_BILL = "CORRECTED BILL"
    SUPPLEMENTAL_CURRENT = "SUPPLEMENTAL - CURRENT"
    UTILITY = "UTILITY"
    GROUND_RENT = "GROUND RENT"
    CURRENT_BILL_ONLY = "CURRENT BILL ONLY"
    UNABLE_TO_ID = "UNABLE TO ID"


class Config:
    """Configuration constants"""
    AI_FORWARDING_MIN_CONFIDENCE = 7
    FIELD_MIN_CONFIDENCE = 5
    HIGH_CONFIDENCE_THRESHOLD = 8
    FORWARDING_DETECTION_MIN_CONFIDENCE = 9  # For strict forwarding scenarios


# --- Classification Priority List (Source of Truth) ---
# USING ORIGINAL PRIORITY LIST
CLASSIFICATION_PRIORITY = {
    DocTypes.INACTIVE_LOAN: 1,
    DocTypes.TAX_SALE: 2,
    DocTypes.FORECLOSURES: 3, 
    DocTypes.LEGAL_CORRESPONDENCE: 4, 
    DocTypes.LIEN_RELATED: 5, 
    DocTypes.CODE_VIOLATION: 6,
    DocTypes.DELINQUENT_TAX_BILL: 7, 
    DocTypes.SUPPLEMENTAL_DELINQUENT: 8, 
    DocTypes.PROPERTY_TAX_RESEARCH: 9, 
    DocTypes.AUTHORIZATION_LETTER: 10, 
    DocTypes.REFUND_RECOVERY: 11, 
    DocTypes.CORRESPONDENCE: 12,
    DocTypes.NJ_CERTIFICATES: 13, 
    DocTypes.ASSESSMENTS: 14, 
    DocTypes.ESCROW_ANALYSIS: 15, 
    DocTypes.EXEMPTION: 16, 
    DocTypes.WI_PAYMENT_OPTION: 17, 
    DocTypes.OPTION_LETTER_NOT_WI: 18, 
    DocTypes.FIRE_DISTRICT: 19, 
    DocTypes.INSURANCE: 20,
    DocTypes.PROOF_OF_PAYMENT: 21, 
    DocTypes.HOA: 22,
    DocTypes.UNSECURED_BILL: 23,
    DocTypes.NON_TAX_CORRESPONDENCE: 24,
    DocTypes.TAX_INFO_SHEET: 25,
    DocTypes.CORRECTED_BILL: 26,
    DocTypes.SUPPLEMENTAL_CURRENT: 27,
    DocTypes.UTILITY: 28,
    DocTypes.GROUND_RENT: 29,
    DocTypes.CURRENT_BILL_ONLY: 30,
    DocTypes.UNABLE_TO_ID: 31,
}


# --- Expanded Regex Patterns for Forwarding Detection (Unchanged) ---
CORRESPONDENCE_DEMOTION_PATTERNS = [
    re.compile(r'\bplease\s*,?\s+(pay|handle|process|take\s+care\s+of)', re.IGNORECASE),
    re.compile(r'\b(kindly|could\s+you)\s+pay', re.IGNORECASE),
    re.compile(r'\bpay\s+(my|the|this)\s+tax', re.IGNORECASE),
    re.compile(r'\battached\s+is\s+(my|the|a)\s+.*\b(tax\s+)?bill', re.IGNORECASE),
    re.compile(r'\bsee\s+attachment', re.IGNORECASE),
    re.compile(r'\bplease\s+see\s+(attached|the\s+attached)', re.IGNORECASE),
    re.compile(r'\brun\s+escrow\s+analysis', re.IGNORECASE),
    re.compile(r'\bescrow\s+analysis', re.IGNORECASE),
    re.compile(r'\bupdate.*escrow', re.IGNORECASE),
    re.compile(r'\bfor\s+your\s+(review|attention|action)', re.IGNORECASE),
    re.compile(r'\bplease\s*,?\s+(review|process|handle)', re.IGNORECASE),
    re.compile(r'\bhave\s+this\s+updated', re.IGNORECASE),
    re.compile(r'\bkindly\s+(review|process|handle)', re.IGNORECASE),
    re.compile(r'\btake\s+care\s+of\s+this', re.IGNORECASE),
]


# --- Helper Functions ---

def get_highest_priority_document(
    documents_list: List[Dict[str, Any]]
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Given a list of document objects, returns the SINGLE object
    that has the highest priority (lowest number) classification.
    """
    if not documents_list:
        return None, DocTypes.UNABLE_TO_ID

    documents_list = [doc for doc in documents_list if doc is not None and doc.get('classification')]
    if not documents_list:
        return None, DocTypes.UNABLE_TO_ID
        
    winner = min(
        documents_list,
        key=lambda doc: CLASSIFICATION_PRIORITY.get(doc.get('classification'), 99)
    )
    
    return winner, winner.get('classification')

# Re-aliasing for internal use
_get_highest_priority_document = get_highest_priority_document


def _detect_forwarding_with_hybrid_approach(
    email_body_text: Optional[str],
    ai_forwarding_analysis: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """ (function remains unchanged) """
    if not email_body_text:
        logging.info("No email body text found. Not a forwarding scenario.")
        return False, None
    
    email_text = email_body_text.lower()
    
    # --- Step 1: Check regex patterns (fast) ---
    for pattern in CORRESPONDENCE_DEMOTION_PATTERNS:
        if pattern.search(email_text):
            logging.warning(f"✅ REGEX MATCH: Found forwarding pattern: {pattern.pattern}")
            forwarding_doc_type = ai_forwarding_analysis.get('forwarding_document_type')
            return True, forwarding_doc_type
    
    # --- Step 2: No regex match, check AI's analysis ---
    ai_is_forwarding = ai_forwarding_analysis.get('is_forwarding', False)
    ai_forwarding_doc = ai_forwarding_analysis.get('forwarding_document_type')
    ai_confidence = ai_forwarding_analysis.get('confidence', 0)
    
    if ai_is_forwarding and ai_confidence >= Config.AI_FORWARDING_MIN_CONFIDENCE:
        logging.warning(f"✅ AI DETECTED FORWARDING: type={ai_forwarding_doc}, confidence={ai_confidence}")
        return True, ai_forwarding_doc
    
    logging.info("No forwarding detected (neither regex nor AI).")
    return False, None


def _handle_email_forwarding_logic(
    documents_list: List[Dict[str, Any]],
    email_body_text: Optional[str],
    ai_forwarding_analysis: Dict[str, Any]
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Implements the email forwarding business logic:
    If forwarding detected, the referenced document type MUST win, 
    regardless of its numerical priority rank.
    """
    
    # --- Check for CORRESPONDENCE (Your Logic Check 1 Entry) ---
    has_correspondence = any(
        doc.get('classification') == DocTypes.CORRESPONDENCE 
        for doc in documents_list
    )
    
    if not has_correspondence:
        logging.info("No CORRESPONDENCE found. Using normal priority rules.")
        return _get_highest_priority_document(documents_list)
    
    logging.warning("📧 CORRESPONDENCE detected. Checking for email forwarding scenario...")
    
    # --- Use hybrid detection (Your Logic Check 2 Entry) ---
    is_forwarding, forwarding_doc_type = _detect_forwarding_with_hybrid_approach(
        email_body_text, 
        ai_forwarding_analysis
    )
    
    if not is_forwarding:
        logging.info("Not a forwarding email. Using normal priority rules (Your Logic Case B).")
        return _get_highest_priority_document(documents_list)
    
    # --- Forwarding detected! (Your Logic Case A Entry) ---
    logging.warning(f"🎯 EMAIL FORWARDING DETECTED! Referenced document: {forwarding_doc_type}. MUST WIN.")
    
    # Find the document that matches the forwarding type
    if forwarding_doc_type:
        found_doc = None
        for doc in documents_list:
            if doc.get('classification') == forwarding_doc_type:
                found_doc = doc
                break

        if found_doc:
            # FIX: ABSOLUTE OVERRIDE. If found, it wins (Your Logic Case 3a).
            logging.warning(f"✅ Found matching document: {forwarding_doc_type}. OVERRIDING NUMERICAL PRIORITY.")
            return found_doc, forwarding_doc_type
        
        # FIX: M-FORWARDING-MISMATCH. If the document type is named but not found (Your Logic Case 3b).
        logging.error(
            f"⚠️ CRITICAL: Forwarding detected to '{forwarding_doc_type}' but no matching document found in the list. FLAG M-FORWARDING-MISMATCH."
        )
        # Return a special marker for the orchestrator to catch the Mismatch Flag
        return None, f"REVIEW_NEEDED_{forwarding_doc_type}"

    # FIX: M-FORWARDING-MISMATCH for NULL attachment type (Your Logic Case 3b - Null Type).
    # If forwarding is detected but forwarding_doc_type is Null (AI error), it must be a Mismatch.
    logging.error("⚠️ Forwarding detected but target document type is NULL. FLAG M-FORWARDING-MISMATCH.")
    
    # We return a specific flag indicating the target was null, the orchestrator handles the Mismatch status.
    return None, f"REVIEW_NEEDED_ATTACHMENT_NULL"


def _validate_property_address(address_value: Optional[str]) -> bool:
    # ... (omitted helper implementation)
    if not address_value: return True
    address_lower = address_value.lower()
    invalid_indicators = ['tax collector', 'treasurer', 'county office', 'tax office', 'p.o. box', 'po box', 'return service', 'official business', 'tax assessor', 'revenue department', 'revenue dept', 'county of', 'city of', 'remit to', 'remittance']
    for indicator in invalid_indicators:
        if indicator in address_lower:
            logging.warning(f"⚠️ Address validation failed: Found '{indicator}' in address")
            return False
    return True

def _extract_value_and_confidence(data: Any) -> Tuple[Any, int]:
    # ... (omitted helper implementation)
    if isinstance(data, dict): return data.get('value'), data.get('confidence', 0)
    return data, 10

def _normalize_text(text: Any) -> str:
    # ... (omitted helper implementation)
    if not isinstance(text, str): return ''
    return re.sub(r'[\s\W_]+', '', text).lower()

def _update_field_status(
    report: Dict[str, Any], field_key: str, ai_data: Any, status: str, reason: Optional[str] = None
) -> None:
    # ... (omitted helper implementation)
    value, confidence = _extract_value_and_confidence(ai_data)
    display_value = value if value is not None else ''
    if field_key not in report['fields']:
        report['fields'][field_key] = {
            'value': display_value,
            'confidence': confidence,
            'status': status,
            'reason': reason or (f"AI Confidence: {confidence}/10" if confidence < 10 else "")
        }
    else:
        if status == 'review' and reason:
            report['fields'][field_key]['status'] = 'review'
            report['fields'][field_key]['reason'] = reason

def check_client_validity(ai_data: Dict[str, Any], report: Dict[str, Any]) -> bool:
    # ... (omitted validation function implementations)
    ai_client_data = ai_data.get('client')
    ai_client_value, confidence = _extract_value_and_confidence(ai_client_data)
    if not ai_client_value or not isinstance(ai_client_value, str):
        report["failure_modes"].append("M8"); _update_field_status(report, 'client', ai_client_data, "review", "M8: Client name not found or invalid."); return True
    normalized_ai_client = ai_client_value.lower()
    client_match = None
    for known_client in CLIENT_SLA_RULES.keys():
        if known_client.lower() in normalized_ai_client: client_match = known_client; break
    if not client_match:
        report["failure_modes"].append("M8"); _update_field_status(report, 'client', ai_client_data, "review", f"M8: '{ai_client_value}' not in master list."); return True
    status = "trusted" if confidence >= Config.FIELD_MIN_CONFIDENCE else "review"
    _update_field_status(report, 'client', ai_client_data, status)
    return confidence < Config.FIELD_MIN_CONFIDENCE

def check_confidence(ai_data: Dict[str, Any], report: Dict[str, Any]) -> bool:
    # ... (omitted validation function implementations)
    any_low_confidence = False
    excluded_fields = {'classification', 'document_text', 'email_body'}
    for field, data in ai_data.items():
        if field in excluded_fields: continue
        _value, confidence = _extract_value_and_confidence(data)
        if confidence < Config.FIELD_MIN_CONFIDENCE:
            any_low_confidence = True
            _update_field_status(report, field, data, "review", f"Low AI Confidence: {confidence}/10")
    return any_low_confidence

def check_doc_type_mismatch_M2(
    final_classification: str, ground_truth: Dict[str, Any], report: Dict[str, Any]
) -> bool:
    # ... (omitted validation function implementations)
    expected_doc_type = ground_truth.get('expected_document_type')
    if not final_classification:
        report["failure_modes"].append("M2"); _update_field_status(report, 'classification', {'value': 'AI FAILED', 'confidence': 0}, "review", "M2: AI failed to provide a valid classification."); return True
    if expected_doc_type and expected_doc_type.lower() not in final_classification.lower():
        report["failure_modes"].append("M2")
        if 'classification' in report['fields']:
            report['fields']['classification']['status'] = 'review'
            report['fields']['classification']['reason'] = f"M2: Expected '{expected_doc_type}'."
        return True
    return False

def check_situs_parcel_mismatch_M4(
    ai_data: Dict[str, Any], ground_truth: Dict[str, Any], report: Dict[str, Any]
) -> bool:
    # ... (omitted validation function implementations)
    mismatch_found = False
    ai_address_data = ai_data.get('property_address')
    ai_address_value, _ = _extract_value_and_confidence(ai_address_data)
    expected_address = ground_truth.get('situs_address')
    if ai_address_value and not _validate_property_address(ai_address_value):
        report["failure_modes"].append("M4"); _update_field_status(report, 'property_address', ai_address_data, "review", "M4: Extracted address appears to be Tax Collector/Office address, not property location."); mismatch_found = True
    if expected_address: 
        expected_address_core = expected_address.split(',')[0]
        if not ai_address_value or not isinstance(ai_address_value, str) or _normalize_text(expected_address_core) not in _normalize_text(ai_address_value):
            if "M4" not in report["failure_modes"]: report["failure_modes"].append("M4")
            _update_field_status(report, 'property_address', ai_address_data, "review", "M4: Situs address mismatch."); mismatch_found = True
    ai_parcel_data = ai_data.get('parcel_number')
    ai_parcel_value, _ = _extract_value_and_confidence(ai_parcel_data)
    expected_parcel = ground_truth.get('parcel_number')
    if expected_parcel:
        if not ai_parcel_value or _normalize_text(ai_parcel_value) != _normalize_text(expected_parcel):
            if "M4" not in report["failure_modes"]: report["failure_modes"].append("M4")
            _update_field_status(report, 'parcel_number', ai_parcel_data, "review", "M4: Parcel number mismatch."); mismatch_found = True
    return mismatch_found

def check_sla_breach_M7(
    ai_data: Dict[str, Any], ground_truth: Dict[str, Any], report: Dict[str, Any]
) -> bool:
    # ... (omitted validation function implementations)
    ai_client_data = ai_data.get('client')
    ai_client_value, _ = _extract_value_and_confidence(ai_client_data)
    if not ai_client_value: return False
    client_match = None
    for known_client in CLIENT_SLA_RULES.keys():
        if known_client.lower() in ai_client_value.lower(): client_match = known_client; break
    if not client_match: return False
    sla_days = CLIENT_SLA_RULES[client_match].get("SLA_DAYS")
    received_date_str = ground_truth.get("received_date")
    if not sla_days or not received_date_str:
        logging.warning(f"SLA check skipped for {client_match}: Missing SLA_DAYS or received_date."); return False
    try:
        received_date = datetime.strptime(received_date_str, "%Y-%m-%d").date()
        today = date.today()
        days_passed = (today - received_date).days
        if days_passed > sla_days:
            report["failure_modes"].append("M7"); logging.warning(f"SLA Breach (M7): {days_passed} days > {sla_days} day SLA for {client_match}."); return True
    except ValueError:
        logging.error(f"Could not parse received_date: '{received_date_str}'")
    return False

# --- Main Validation Orchestrator ---

def run_all_validations(
    ai_data: Dict[str, Any],
    ground_truth: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Orchestrates all validation checks with email forwarding logic.
    """
    logging.warning("--- 🔍 Starting Validation Process with Email Forwarding Logic ---")
    report = {"overall_status": "Success", "failure_modes": [], "fields": {}}

    # --- 1. Extract data from AI response ---
    documents_list = ai_data.get('documents_found')
    email_body_obj = ai_data.get('email_body', {})
    email_body_text = email_body_obj.get('value') if email_body_obj else ""
    email_forwarding_analysis = ai_data.get('email_forwarding_analysis', {})
    
    if not documents_list or not isinstance(documents_list, list):
        logging.error("❌ AI Response was empty or invalid.")
        report["overall_status"] = "Needs Manual Review"
        report["failure_modes"].append("M-AI-ERROR")
        _update_field_status(
            report, 
            'classification', 
            {'value': 'AI ERROR', 'confidence': 0}, 
            "review", 
            "AI did not return valid data."
        )
        return report

    # --- 2. Apply the Email Forwarding Logic (Priority Override) ---
    logging.warning(f"AI found classifications: {[doc.get('classification') for doc in documents_list]}")
    
    winning_data, final_classification = _handle_email_forwarding_logic(
        documents_list, 
        email_body_text, 
        email_forwarding_analysis
    )
    
    # --- 3. Check for the M-FORWARDING-MISMATCH Flag ---
    if final_classification and final_classification.startswith("REVIEW_NEEDED_"):
        
        # Determine the source and message for the Mismatch
        if final_classification == "REVIEW_NEEDED_ATTACHMENT_NULL":
            # Case: Forwarding detected, but AI failed to name the attachment type (NULL)
            expected_doc_reason = "Attachment type could not be determined."
            display_classification = "CORRESPONDENCE" # Default display for the classification field
        else:
            # Case: Forwarding detected, attachment type named but not found in the list
            expected_doc = final_classification.replace("REVIEW_NEEDED_", "").split('_')[0]
            expected_doc_reason = f"Expected '{expected_doc}' attachment not found in classified documents."
            display_classification = expected_doc
            
        logging.error(f"❌ Forwarding Mismatch detected. Setting M-FORWARDING-MISMATCH.")
        
        report["overall_status"] = "Needs Manual Review"
        report["failure_modes"].append("M-FORWARDING-MISMATCH")
        
        # Use the intended document as the classification, but mark it for review
        _update_field_status(
            report,
            'classification',
            {'value': display_classification, 'confidence': 0},
            "review",
            f"M-FORWARDING-MISMATCH: {expected_doc_reason}"
        )
        return report # Terminate validation immediately
    
    logging.warning(f"✅ Final classification: '{final_classification}'")
    
    # --- 4. Add classification to report ---
    _update_field_status(
        report, 
        'classification', 
        {'value': final_classification, 'confidence': 10}, 
        "trusted"
    )

    # --- 5. Run all validation checks on the winning data ---
    if winning_data is None:
        logging.error("❌ No winning document data available.")
        report["overall_status"] = "Needs Manual Review"
        return report
    
    logging.warning("--- Running all checks on the 'winning' data object ---")
    needs_review_confidence = check_confidence(winning_data, report)
    needs_review_client = check_client_validity(winning_data, report)

    if ground_truth:
        logging.info("✅ Ground truth data found. Running detailed checks...")
        needs_review_m2 = check_doc_type_mismatch_M2(final_classification, ground_truth, report)
        needs_review_m4 = check_situs_parcel_mismatch_M4(winning_data, ground_truth, report)
        needs_review_m7 = check_sla_breach_M7(winning_data, ground_truth, report) 
    else:
        logging.warning("⚠️ No ground truth data for this loan. Skipping M2, M4, M7 checks.")
        needs_review_m2 = needs_review_m4 = needs_review_m7 = False

    # --- 6. Determine final status ---
    if any([needs_review_confidence, needs_review_client, needs_review_m2, needs_review_m4, needs_review_m7]):
        report["overall_status"] = "Needs Manual Review"
    
    # --- 7. Populate all other fields from the winning object ---
    for field, data in winning_data.items():
        if field in ['classification', 'document_text']:
            continue
        if field not in report["fields"]:
            confidence = _extract_value_and_confidence(data)[1]
            status = "trusted" if confidence >= Config.FIELD_MIN_CONFIDENCE else "review"
            _update_field_status(report, field, data, status)

    logging.info(f"✅ Validation complete. Final status: {report['overall_status']}")
    return report


