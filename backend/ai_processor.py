

import os
import re
import json
import io
import hashlib
import logging
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image


# --- Configuration ---
class Config:
    """AI Configuration constants"""
    AI_MODEL = "gemini-2.5-flash"
    TEMPERATURE = 0.0
    JSON_DELIMITER = "---JSON_DELIMITER---"
    MAX_CACHE_SIZE = 100


# Load environment variables
script_dir = os.path.dirname(__file__)
dotenv_path = os.path.join(script_dir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

API_KEY = os.getenv("GOOGLE_API_KEY")


# --- Security & Validation ---

def sanitize_loan_id(loan_id: Optional[str]) -> str:
    """
    Sanitizes loan_id to prevent format string injection and other issues.
    
    Args:
        loan_id: Raw loan ID string
        
    Returns:
        Sanitized loan ID containing only alphanumeric, dash, and underscore
    """
    if not loan_id:
        return "UNKNOWN"
    
    # Remove any special characters except alphanumeric, dash, underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', str(loan_id))
    
    if not sanitized:
        logging.warning(f"Loan ID '{loan_id}' sanitized to empty string, using 'UNKNOWN'")
        return "UNKNOWN"
    
    return sanitized


def configure_ai() -> None:
    """Configures the generative AI model with the API key."""
    if not API_KEY:
        logging.critical("CRITICAL ERROR: GOOGLE_API_KEY not set.")
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    
    genai.configure(api_key=API_KEY)
    logging.info("🤖 AI Model configured successfully.")
    # Mask API key in logs for security
    logging.debug(f"API Key configured: {'*' * len(API_KEY)}")


# Initialize AI configuration
configure_ai()


# --- Prompt Templates (Modularized) ---

class PromptSections:
    """Modularized prompt sections for better maintainability"""
    
    @staticmethod
    def get_objective() -> str:
        return """
🎯 OBJECTIVE
Scan all pages. For *each* distinct document type you identify (e.g., an email, a bill, a receipt), create *one* self-contained, FLAT JSON object for it.
If you find an email, also create a *separate* JSON object for the "email_body" AND a separate JSON object for "email_forwarding_analysis".

--- 1. Document Object (FLAT) ---
(Create one of these for EACH document type found)
{{"classification": "CURRENT BILL ONLY", "loan_id": "{loan_id_placeholder}", "client": "Mr Cooper", "property_address": "123 Main St", "total_tax_paid": null, ...}}

--- 2. Email Body Object (FLAT) ---
(Create this *only if* an email is present)
{{"email_body": "Hello, please pay this bill..."}}

--- 3. Email Forwarding Analysis Object (FLAT) ---
(Create this *only if* an email is present)
{{"is_forwarding": "true", "forwarding_document_type": "CURRENT BILL ONLY", "forwarding_confidence": "9"}}
"""
    
    @staticmethod
    def get_required_fields() -> str:
        return """
⚙️ REQUIRED FIELDS FOR "Document Objects"
- classification (string)
- loan_id (string or null)
- client (string or null)
- property_address (string or null)
- total_tax_paid (string or null)
- parcel_number (string or null)
- tax_year (string or null)
- base_tax_amount (string or null)
- date_paid (string or null)
- check_number (string or null)

**CRITICAL FORMATTING RULE**: Do NOT nest fields. The *only* value for each key should be a simple string or null.
"""
    
    @staticmethod
    def get_negative_constraints() -> str:
        return """
🚫 NEGATIVE CONSTRAINTS & FIELD TUNING (CRITICAL)

**property_address**
- MUST be the "Situs Address" or "Property Location" - the PHYSICAL location of the taxed property.
- **NEVER** extract:
  * Tax Collector's address (e.g., "Joan E. North, Tax Collector", "113 South Ridge Street")
  * Return Address or Mailing Address
  * Remittance Address (where payments are sent)
  * PO Box addresses
  * Any address with "Treasurer", "Tax Office", "County Office"
  * Addresses near "Return Service Requested" or "Official Business"
  * Any address with "County of...", "City of...", "Remit to..."
- **LOOK FOR THESE LABELS**: "Situs Address", "Property Location", "Property Address", "Parcel Location", "Site Address"
- The property address is typically:
  * Near the parcel number
  * In a section labeled "Property Information" or "Parcel Details"
  * The SUBJECT of the tax bill, not the recipient or office location
  * In the TOP THIRD of the first page
  * In a box or section labeled "Property Information"
  * ABOVE or NEAR the parcel number
  * Will NOT include office names, titles, or "Return Service Requested"

**base_tax_amount**
- MUST be the final "Total Amount Due", "Face Amount", or "Net Amount".
- **NEVER** extract a single line item from a "Tax Distribution" or "Levy" table.
- Look for the aggregate total.

**parcel_number**
- Look specifically for labels: "Parcel #", "APN", "Map/Lot", "Control Number", "Property ID".
- Often near the top or on the payment coupon.

**loan_id**
1. Primary source → use the filename: '{loan_id_placeholder}' for ALL document objects by default.
2. Fallback → If you find a *different* "Loan #" on a specific document, override the default for that object *only*.
"""
    
    @staticmethod
    def get_classification_rules() -> str:
        return """
📌 FIELD RULES

**classification**
- Single string value from the 31 priority classifications listed below.

**Data Scoping (CRITICAL)**
- Data found on a "CURRENT BILL ONLY" (e.g., `base_tax_amount`) must ONLY go in the "CURRENT BILL ONLY" object.
- A "CORRESPONDENCE" object will have `null` for most tax fields.

**loan_id**
1. Primary source → use filename: '{loan_id_placeholder}' for ALL documents by default.
2. Fallback → If different "Loan #" found on specific document, override for that object only.
"""
    
    @staticmethod
    def get_classification_priority_list() -> str:
        return """
🧾 CLASSIFICATION PRIORITY LIST (1 = highest, 31 = lowest):

1.  `INACTIVE LOAN`: Notice/System Info. Keywords: "Inactive Loan Status in OneView", "Loan closed", "Paid in full"
2.  `TAX SALE`: Notice. Keywords: "Tax Sale Notice", "Lien Sale", "Public Auction", "Certificate of Sale"
3.  `FORECLOSURES`: Notice. Keywords: "Notice of Default", "Trustee's Sale", "Foreclosure"
4.  `LEGAL CORRESPONDENCE`: Letter from law office/attorney/court
5.  `LIEN RELATED`: Notice. Keywords: "Tax Lien", "Lien Release", "Certificate of Discharge"
6.  `CODE VIOLATION`: Notice. Keywords: "Code Violation", "Municipal Citation", "Fine"
7.  `DELINQUENT TAX BILL`: Bill with "Delinquent", "Overdue", "Penalty", "Interest Charged"
8.  `SUPPLEMENTAL - DELINQUENT`: Bill that is both "Supplemental" and "Delinquent"
9.  `PROPERTY TAX RESEARCH`: Internal research/verification request
10. `AUTHORIZATION LETTER`: "Authorization", "Permission", "Third Party Access"
11. `REFUND - RECOVERY RELATED`: Formal refund notice or check
12. `CORRESPONDENCE`: Email/Letter/Fax (format-based classification)
13. `NJ CERTIFICATES`: New Jersey specific certificates
14. `ASSESSMENTS`: Formal "Notice of Appraised Value", "Assessment Notice", "TRIM Notice"
15. `ESCROW ANALYSIS`: Formal "Escrow Review Statement", "Escrow Analysis"
16. `EXEMPTION`: Formal "Exemption Application", "Exemption Granted", "Homestead"
17. `WI PAYMENT OPTION`: Wisconsin-specific payment option letter
18. `OPTION LETTER - NOT WI`: Payment plan from non-Wisconsin state
19. `FIRE DISTRICT RELATED`: Fire District bill/notice
20. `INSURANCE`: "Proof of Insurance", "Hazard Insurance", "Insurance Policy"
21. `PROOF OF PAYMENT`: Receipt with "Paid", "Receipt", "$0.00 balance"
22. `HOA`: "Homeowner's Association", "HOA Dues", "Condo Fees"
23. `UNSECURED BILL`: Personal property/unsecured taxes
24. `NON TAX CORRESPONDENCE`: Non-tax-related letter/email
25. `TAX INFORMATION SHEET`: Informational document with tax rates/schedules
26. `CORRECTED BILL`: "Corrected Bill", "Revised Tax Statement"
27. `SUPPLEMENTAL - CURRENT`: "Supplemental" bill for current period (not delinquent)
28. `UTILITY`: "Water", "Sewer", "Electric" as separate bill
29. `GROUND RENT`: "Ground Rent", "Ground Lease"
30. `CURRENT BILL ONLY`: Standard current-year tax bill with no penalty
31. `UNABLE TO ID`: Use only if no other category fits
"""
    
    @staticmethod
    def get_email_forwarding_analysis() -> str:
        return """
📧 EMAIL FORWARDING ANALYSIS (CRITICAL)

**IF AN EMAIL IS PRESENT**, create "email_forwarding_analysis" object:

- **is_forwarding** (string: "true" or "false")
  Set to "true" if email:
  * Contains: "please pay", "attached is", "see attachment", "kindly process", "please handle", "take care of", "for your review"
  * Is very short (< 100 words) with minimal explanation
  * Primary purpose is to transmit an attached document
  * Contains: "run escrow analysis", "pay my taxes", "process this bill"
  
  Set to "false" if email:
  * Discusses complex issues or has substantive questions
  * Is from attorney/legal office
  * Contains detailed explanations or negotiations
  * Is longer and conversational

- **forwarding_document_type** (string or null)
  If is_forwarding = "true", identify WHICH document the email forwards.
  Look for clues: "attached is my CURRENT bill", "see the DELINQUENT notice"
  Match to one of the document classifications.
  If is_forwarding = "false", set to null.

- **forwarding_confidence** (string: "1" to "10")
  Your confidence in the forwarding analysis.

**EXAMPLE:**
Email: "Hi, please pay my current tax bill. Attached."
Documents: DELINQUENT TAX BILL, CURRENT BILL ONLY, CORRESPONDENCE

Analysis: {{"is_forwarding": "true", "forwarding_document_type": "CURRENT BILL ONLY", "forwarding_confidence": "9"}}
"""
    
    @staticmethod
    def get_final_instruction() -> str:
        return """
⛔️ FINAL INSTRUCTION
Your response MUST contain ONLY minified, FLAT JSON objects, separated by `---JSON_DELIMITER---`.
Do NOT add ANY conversational text, introductions, explanations, or apologies.
Your entire response must be parseable.

Example Output:
{{"classification": "CORRESPONDENCE", "loan_id": "{loan_id_placeholder}", "client": "Mr Cooper", "property_address": null, ...}}
---JSON_DELIMITER---
{{"classification": "CURRENT BILL ONLY", "loan_id": "{loan_id_placeholder}", "client": "Mr Cooper", "property_address": "123 Main St", ...}}
---JSON_DELIMITER---
{{"email_body": "Hello, Please see attachment..."}}
---JSON_DELIMITER---
{{"is_forwarding": "true", "forwarding_document_type": "CURRENT BILL ONLY", "forwarding_confidence": "9"}}
"""
    
    @staticmethod
    def build_complete_prompt(loan_id: str) -> str:
        """
        Builds the complete prompt from modular sections.
        
        Args:
            loan_id: Sanitized loan ID to insert into prompt
            
        Returns:
            Complete formatted prompt string
        """
        intro = """You are a hyper-precise document-analysis expert. Your task is to analyze the provided images and return a series of **SIMPLE, FLAT, MINIFIED JSON OBJECTS**.
Do NOT use nested objects for fields. All values must be strings or null.
You MUST separate each JSON object with a unique delimiter:
---JSON_DELIMITER---

──────────────────────────────────────────────"""
        
        sections = [
            intro,
            PromptSections.get_objective(),
            "──────────────────────────────────────────────",
            PromptSections.get_required_fields(),
            "──────────────────────────────────────────────",
            PromptSections.get_negative_constraints(),
            "──────────────────────────────────────────────",
            PromptSections.get_classification_rules(),
            "──────────────────────────────────────────────",
            PromptSections.get_classification_priority_list(),
            "──────────────────────────────────────────────",
            PromptSections.get_email_forwarding_analysis(),
            "──────────────────────────────────────────────",
            PromptSections.get_final_instruction()
        ]
        
        complete_prompt = "\n".join(sections)
        
        # Replace loan_id placeholder
        complete_prompt = complete_prompt.replace("{loan_id_placeholder}", loan_id)
        
        return complete_prompt


# --- Response Parsing (FIXED AND ENHANCED) ---

def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """
    Parses AI response with fallback mechanisms and robust cleaning.
    
    Args:
        response_text: Raw response text from AI
        
    Returns:
        Structured dictionary with documents_found, email_body, email_forwarding_analysis
    """
    documents_found = []
    email_body = {"value": None, "confidence": 10}
    email_forwarding_analysis = {
        "is_forwarding": False, 
        "forwarding_document_type": None, 
        "confidence": 10
    }
    
    # 1. Initial cleanup of code fences
    response_text = response_text.strip()
    response_text = re.sub(r'```(json)?', '', response_text, flags=re.IGNORECASE)
    response_text = response_text.replace('```', '')
    
    # 2. Robust fix for the AI sometimes wrapping delimited output in extra braces, 
    # which causes the initial parsing failure for malformed chunks like {{...
    response_text = response_text.strip() 
    if response_text.startswith('{') and Config.JSON_DELIMITER in response_text:
        stripped_response = response_text.strip('{').strip('}').strip()
        if Config.JSON_DELIMITER in stripped_response:
             response_text = stripped_response
    
    # Try delimiter parsing first
    if Config.JSON_DELIMITER in response_text:
        json_strings = response_text.split(Config.JSON_DELIMITER)
        logging.info(f"AI response contained {len(json_strings)} JSON chunks (delimiter method).")
    else:
        json_strings = [response_text]
        logging.info(f"AI response is single chunk (no delimiter found).")

    
    # Parse each JSON chunk
    for idx, json_str in enumerate(json_strings):
        json_str = json_str.strip()
        
        # Skip empty chunks
        if not json_str:
            continue
        
        # Store original for debugging/regex fallback
        original_str = json_str
        
        # === COMPREHENSIVE JSON CLEANING PIPELINE (Attempt 1) ===
        
        # Step 1: Remove any wrapping quotes or extra braces
        json_str = json_str.strip('\"\'{}').strip()
        
        # Step 2: Ensure it begins and ends with proper JSON braces
        if not json_str.startswith('{'):
            json_str = '{' + json_str
        if not json_str.endswith('}'):
            json_str = json_str + '}'
            
        # Step 3: Replace single quotes with double quotes (invalid JSON)
        json_str = json_str.replace("'", '"')
        
        # Step 4: Fix unquoted property names (e.g., classification: "VALUE" -> "classification": "VALUE")
        # Finds words followed by a colon but not preceded by a quote, and wraps the word in quotes.
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_]+)\s*:', r'\1"\2":', json_str)
        
        
        # === TRY JSON PARSING ===
        parsing_successful = False
        try:
            parsed_flat = json.loads(json_str)
            parsing_successful = True
            
            # --- Document Object Parsing ---
            if 'classification' in parsed_flat:
                nested_doc = {}
                for key, value in parsed_flat.items():
                    if key == 'classification':
                        nested_doc['classification'] = value
                    else:
                        # Convert AI's flat structure to nested {value, confidence} structure
                        confidence = 10 if value is None else 9
                        
                        # Handle confidence specifically if AI provided it
                        if key.endswith('_confidence'):
                            try:
                                confidence = int(value)
                            except (ValueError, TypeError):
                                confidence = 10
                                
                        nested_doc[key] = {"value": value, "confidence": confidence}
                documents_found.append(nested_doc)
                logging.info(f"✅ Successfully parsed document chunk {idx}: {parsed_flat.get('classification')}")
            
            # --- Email Body Parsing ---
            elif 'email_body' in parsed_flat:
                email_body = {"value": parsed_flat['email_body'], "confidence": 10}
                logging.info(f"✅ Successfully parsed email_body chunk {idx}")
            
            # --- Forwarding Analysis Parsing ---
            elif 'is_forwarding' in parsed_flat:
                is_forwarding_str = parsed_flat.get('is_forwarding', 'false').lower()
                is_forwarding = is_forwarding_str == 'true'
                forwarding_doc_type = parsed_flat.get('forwarding_document_type')
                
                forwarding_confidence_raw = parsed_flat.get('forwarding_confidence', '10')
                try:
                    forwarding_confidence = int(forwarding_confidence_raw)
                except (ValueError, TypeError):
                    forwarding_confidence = 10
                
                email_forwarding_analysis = {
                    "is_forwarding": is_forwarding,
                    "forwarding_document_type": forwarding_doc_type,
                    "confidence": forwarding_confidence
                }
                logging.info(f"✅ Successfully parsed forwarding analysis chunk {idx}: is_forwarding={is_forwarding}")
        
        except json.JSONDecodeError as e:
            logging.error(f"❌ JSON parsing failed for chunk {idx}: {e}")
            parsing_successful = False
        except Exception as e:
            logging.error(f"❌ Unexpected error parsing chunk {idx}: {e}")
            parsing_successful = False
        
        # === REGEX SALVAGE FALLBACK (Layer 3) ===
        if not parsing_successful:
            logging.warning(f"⚠️ Attempting regex extraction for chunk {idx}...")
            
            # Check if this malformed chunk contains a classification field
            classification_match = re.search(r'"classification"\s*:\s*"([^"]+)"', original_str)
            
            if classification_match:
                classification = classification_match.group(1)
                logging.warning(f"⚠️ Extracted classification via regex: {classification}")
                
                # Create a minimal document with demoted confidence
                minimal_doc = {'classification': classification}
                
                fields_to_extract = [
                    'loan_id', 'client', 'property_address', 'parcel_number', 
                    'tax_year', 'base_tax_amount', 'total_tax_paid', 'date_paid', 'check_number'
                ]
                
                for field in fields_to_extract:
                    # Match patterns for both "field": "value" and "field": null
                    field_match = re.search(rf'"{field}"\s*:\s*"([^"]*)"', original_str)
                    null_match = re.search(rf'"{field}"\s*:\s*(null|none)', original_str, re.IGNORECASE)
                    
                    if field_match:
                        value = field_match.group(1)
                        # Use confidence 6 to flag this salvaged data for review
                        minimal_doc[field] = {"value": value if value else None, "confidence": 6} 
                    elif null_match:
                        minimal_doc[field] = {"value": None, "confidence": 10}
                    else:
                        # Field not found, set to lowest confidence for review
                        minimal_doc[field] = {"value": None, "confidence": 5}
                
                documents_found.append(minimal_doc)
                logging.warning(f"✅ Regex extraction successful for chunk {idx}: {classification}")
            
            # Try to salvage email_body (last ditch effort)
            elif re.search(r'email_body', original_str):
                body_match = re.search(r'"email_body"\s*:\s*"([^"]*)"', original_str)
                if body_match:
                    email_body = {"value": body_match.group(1), "confidence": 6}
                    logging.warning(f"✅ Regex extracted email_body for chunk {idx}")
                
            # Try to salvage forwarding analysis
            elif re.search(r'is_forwarding', original_str):
                is_forwarding_match = re.search(r'"is_forwarding"\s*:\s*"([^"]*)"', original_str)
                type_match = re.search(r'"forwarding_document_type"\s*:\s*"([^"]*)"', original_str)
                conf_match = re.search(r'"forwarding_confidence"\s*:\s*"([^"]*)"', original_str)
                
                if is_forwarding_match:
                    is_forwarding_str = is_forwarding_match.group(1).lower()
                    email_forwarding_analysis = {
                        "is_forwarding": is_forwarding_str == 'true',
                        "forwarding_document_type": type_match.group(1) if type_match else None,
                        "confidence": int(conf_match.group(1)) if conf_match and conf_match.group(1).isdigit() else 6
                    }
                    logging.warning(f"✅ Regex extracted forwarding analysis for chunk {idx}")

            else:
                logging.error(f"❌ Could not salvage any data from malformed chunk {idx}")
    
    # Final validation
    if not documents_found:
        logging.error("❌ No valid documents were parsed from AI response")
    else:
        logging.info(f"✅ Total documents parsed: {len(documents_found)}")
    
    return {
        "documents_found": documents_found,
        "email_body": email_body,
        "email_forwarding_analysis": email_forwarding_analysis
    }


# --- Main AI Processing Function ---

def get_ai_response(
    image_bytes_list: List[bytes],
    filename_loan_id: Optional[str] = None
) -> str:
    """
    Analyzes multiple document images using AI.
    
    Args:
        image_bytes_list: List of image byte arrays
        filename_loan_id: Loan ID from filename (will be sanitized)
        
    Returns:
        JSON string with structured analysis results
    """
    try:
        # Sanitize loan_id for security
        sanitized_loan_id = sanitize_loan_id(filename_loan_id)
        logging.info(f"Processing document with loan_id: {sanitized_loan_id}")
        
        # Initialize model
        model = genai.GenerativeModel(Config.AI_MODEL)
        
        # Build prompt with sanitized loan_id
        final_prompt = PromptSections.build_complete_prompt(sanitized_loan_id)
        
        # Start prompt with text
        prompt_parts = [final_prompt]
        
        # Add all images to prompt
        for image_bytes in image_bytes_list:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            prompt_parts.append(Image.open(img_byte_arr))
        
        # Configure generation
        generation_config = genai.types.GenerationConfig(
            temperature=Config.TEMPERATURE
        )
        
        logging.info(f"🚀 Sending request to {Config.AI_MODEL} with {len(image_bytes_list)} images...")
        
        # Generate response
        response = model.generate_content(
            prompt_parts,
            generation_config=generation_config
        )
        
        logging.debug(f"Raw AI Response Text:\n{response.text[:500]}...")  # Log first 500 chars
        
        # Parse response
        final_json_payload = parse_ai_response(response.text)
        
        if not final_json_payload["documents_found"]:
            logging.error("AI returned no valid 'classification' objects.")
        
        logging.info("✅ Successfully parsed and built final nested JSON payload.")
        return json.dumps(final_json_payload)
    
    except Exception as e:
        logging.error(f"Error in get_ai_response: {e}", exc_info=True)
        error_message = {"error": f"An error occurred during AI processing: {str(e)}"}
        return json.dumps(error_message)


# --- Utility Functions ---

def get_pdf_hash(image_bytes_list: List[bytes]) -> str:
    """
    Generates a hash for a list of image bytes for caching purposes.
    
    Args:
        image_bytes_list: List of image byte arrays
        
    Returns:
        MD5 hash string
    """
    hasher = hashlib.md5()
    for img_bytes in image_bytes_list:
        hasher.update(img_bytes)
    return hasher.hexdigest()