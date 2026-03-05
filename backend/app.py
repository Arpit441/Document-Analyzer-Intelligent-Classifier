


# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from pdf2image import convert_from_bytes
# import ai_processor
# import validator
# import data_source
# import io
# import json
# import logging
# import base64
# import csv
# from datetime import datetime
# from PIL import Image

# # --- App Setup ---
# app = Flask(__name__)
# # NOTE: The origins should match your frontend URL (e.g., "http://localhost:3000")
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
# logging.basicConfig(level=logging.INFO)

# # --- Path Setup ---
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DOCUMENT_STORAGE_PATH = os.path.join(BASE_DIR, 'document_storage')
# RESULTS_JSON_PATH = os.path.join(BASE_DIR, 'results_storage', 'json_results')
# RESULTS_CSV_PATH = os.path.join(BASE_DIR, 'results_storage', 'csv_results')
# MASTER_CSV_FILE = os.path.join(RESULTS_CSV_PATH, 'approved_results.csv')

# # --- Constants ---
# # Use <= 7 for single call, > 7 for chunked calls
# MAX_PAGES_SINGLE_CALL = 7 
# # Use 8 pages per chunk for large documents to be safe against API size limits
# MAX_PAGES_PER_CHUNK = 8    

# # --- Create result storage directories if they don't exist ---
# os.makedirs(RESULTS_JSON_PATH, exist_ok=True)
# os.makedirs(RESULTS_CSV_PATH, exist_ok=True)

# # --- Helper Function for Chunking ---
# def _chunk_list(data_list, chunk_size):
#     """Yield successive n-sized chunks from a list."""
#     for i in range(0, len(data_list), chunk_size):
#         yield data_list[i:i + chunk_size]

# # --- API Endpoint for Analysis ---
# @app.route('/api/analyze', methods=['POST'])
# def analyze_document_route():
#     try:
#         data = request.get_json()
#         doc_id = data.get('documentId')
#         loan_id = data.get('loanId')

#         if not doc_id or not loan_id:
#             return jsonify({"error": "Document ID and Loan ID are required."}), 400

#         pdf_path = os.path.join(DOCUMENT_STORAGE_PATH, f"{doc_id}.pdf")
#         if not os.path.exists(pdf_path):
#             return jsonify({"error": f"Document with ID '{doc_id}' not found."}), 404
        
#         with open(pdf_path, 'rb') as f:
#             pdf_bytes = f.read()

#         poppler_path = r"C:\Users\agupta\Downloads\Release-23.11.0-0\poppler-23.11.0\Library\bin"
        
#         # 1. Convert PDF to a LIST of PIL images (one image object per page)
#         images = convert_from_bytes(pdf_bytes, dpi=200, poppler_path=poppler_path)
        
#         if not images:
#             return jsonify({"error": "Could not convert PDF to image."}), 400

#         total_pages = len(images)
#         logging.info(f"PDF has {total_pages} pages. Preparing for AI analysis.")
        
#         # 2. Convert PIL images to bytes (with compression logic)
#         image_bytes_list = []
#         for image in images:
#             if image.mode != 'RGB':
#                 image = image.convert('RGB')
#             img_byte_arr = io.BytesIO()
            
#             # Optimization: Use JPEG compression for all documents > 7 pages to keep payload size down
#             if total_pages > MAX_PAGES_SINGLE_CALL:
#                  image.save(img_byte_arr, format='JPEG', quality=85) 
#             else:
#                  image.save(img_byte_arr, format='PNG')
                 
#             image_bytes_list.append(img_byte_arr.getvalue())
        
#         logging.info(f"Successfully converted all {total_pages} pages to bytes.")
        
        
#         # --- CONDITIONAL AI PROCESSING LOGIC ---
#         all_ai_extracted_documents = [] # Aggregated list of all extracted documents
        
#         # Initialize final_ai_data with default empty values for non-document fields
#         final_ai_data = {
#             'documents_found': [], 
#             'email_body': {'value': None, 'confidence': 10},
#             'email_forwarding_analysis': {'is_forwarding': False, 'forwarding_document_type': None, 'confidence': 10}
#         }
        
#         # Flag to track if we've found the email data yet
#         email_data_found = False

#         if total_pages <= MAX_PAGES_SINGLE_CALL:
#             # --- Scenario A: Small Document (Single Call) ---
#             logging.warning("Scenario A: Small document (<= 7 pages). Using single API call.")
            
#             json_response_string = ai_processor.get_ai_response(image_bytes_list, loan_id)
#             chunk_data = json.loads(json_response_string)
            
#             if 'error' in chunk_data:
#                 return jsonify({"error": f"AI analysis failed: {chunk_data['error']}"}), 500
            
#             final_ai_data = chunk_data
            
#         else:
#             # --- Scenario B: Large Document (Chunked Calls) ---
#             logging.warning(f"Scenario B: Large document (> 7 pages). Splitting into chunks of {MAX_PAGES_PER_CHUNK}.")
            
#             page_chunks = list(_chunk_list(image_bytes_list, MAX_PAGES_PER_CHUNK))
            
#             for idx, chunk in enumerate(page_chunks):
#                 logging.warning(f"🚀 Processing Chunk {idx + 1}/{len(page_chunks)} ({len(chunk)} pages)...")
                
#                 # Send the chunk (list of images) to the AI processor
#                 json_response_string = ai_processor.get_ai_response(chunk, loan_id)
#                 chunk_data = json.loads(json_response_string)
                
#                 if 'error' in chunk_data:
#                     return jsonify({"error": f"AI analysis failed on chunk {idx+1}: {chunk_data['error']}"}), 500
                
#                 # 3. Aggregate documents found in this chunk
#                 all_ai_extracted_documents.extend(chunk_data.get('documents_found', []))
                
#                 # 4. NEW: Check if this chunk contains the email/forwarding analysis
#                 if not email_data_found:
#                     email_body = chunk_data.get('email_body')
#                     forwarding_analysis = chunk_data.get('email_forwarding_analysis')
                    
#                     # If the email body has a non-empty value, we've found the primary email data
#                     if email_body and email_body.get('value'):
#                         final_ai_data['email_body'] = email_body
#                         final_ai_data['email_forwarding_analysis'] = forwarding_analysis
#                         email_data_found = True
#                         logging.info(f"📧 Email data successfully found in Chunk {idx + 1}.")

        
#         # --- FINAL AGGREGATION AND VALIDATION ---
        
#         # Overwrite documents_found with the aggregated list
#         final_ai_data['documents_found'] = all_ai_extracted_documents
        
#         if not final_ai_data.get('documents_found'):
#              return jsonify({"error": "AI failed to extract any documents from the analysis. Please check file content."}), 500
             
        
#         pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

#         # Run validation and final reporting on the combined data
#         ground_truth = data_source.LOAN_DATA_GROUND_TRUTH.get(loan_id)
#         final_report = validator.run_all_validations(final_ai_data, ground_truth)
#         final_report['document_pdf'] = pdf_base64
        
#         logging.info("✅ Final analysis prepared successfully.")
#         return jsonify(final_report)

#     except Exception as e:
#         logging.error(f"An error occurred in '/api/analyze': {e}", exc_info=True)
#         return jsonify({"error": "An unexpected server error occurred."}), 500

# # --- API Endpoint for Saving Results (No Change) ---
# @app.route('/api/save_document', methods=['POST'])
# def save_document_route():
#     try:
#         data = request.get_json()
#         doc_id = data.get('documentId')
#         if not doc_id:
#             return jsonify({"error": "Document ID is required for saving."}), 400

#         # --- Save 1: The detailed individual JSON file ---
#         json_filename = f"{doc_id}_result.json"
#         json_filepath = os.path.join(RESULTS_JSON_PATH, json_filename)
#         with open(json_filepath, 'w') as f:
#             json.dump(data, f, indent=4)
#         logging.info(f"Successfully saved detailed result to {json_filepath}")

#         # --- Save 2: The summary row in the master CSV log ---
#         csv_header = ['Document_ID', 'Loan_ID', 'Final_Status', 'Failure_Modes', 'Timestamp']
#         file_exists = os.path.isfile(MASTER_CSV_FILE)

#         with open(MASTER_CSV_FILE, 'a', newline='') as f:
#             writer = csv.DictWriter(f, fieldnames=csv_header)
#             if not file_exists:
#                 writer.writeheader()
            
#             writer.writerow({
#                 'Document_ID': doc_id,
#                 'Loan_ID': data.get('loanId'),
#                 'Final_Status': data.get('overall_status'),
#                 'Failure_Modes': ','.join(data.get('failure_modes', [])),
#                 'Timestamp': datetime.now().isoformat()
#             })
#         logging.info(f"Successfully appended summary to {MASTER_CSV_FILE}")

#         return jsonify({"message": f"Successfully saved review for Document ID {doc_id}"}), 200

#     except Exception as e:
#         logging.error(f"An error occurred in '/api/save_document': {e}", exc_info=True)
#         return jsonify({"error": "An unexpected server error occurred while saving."}), 500

# # --- Main Execution ---
# if __name__ == '__main__':
#     app.run(debug=True, port=5000, use_reloader=False)

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf2image import convert_from_bytes
import ai_processor
import validator
import data_source
import io
import json
import logging
import base64
from datetime import datetime
import csv
from PIL import Image

# --- App Setup ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
logging.basicConfig(level=logging.INFO)

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENT_STORAGE_PATH = os.path.join(BASE_DIR, 'document_storage')
RESULTS_JSON_PATH = os.path.join(BASE_DIR, 'results_storage', 'json_results')
RESULTS_CSV_PATH = os.path.join(BASE_DIR, 'results_storage', 'csv_results')
MASTER_CSV_FILE = os.path.join(RESULTS_CSV_PATH, 'approved_results.csv')

# --- Constants ---
# Tighter single-call limit based on API payload constraints
MAX_PAGES_SINGLE_CALL = 6 
MAX_PAGES_PER_CHUNK = 6    

# --- Create result storage directories if they don't exist ---
os.makedirs(RESULTS_JSON_PATH, exist_ok=True)
os.makedirs(RESULTS_CSV_PATH, exist_ok=True)

# --- Helper Function for Chunking ---
def _chunk_list(data_list, chunk_size):
    """Yield successive n-sized chunks from a list."""
    for i in range(0, len(data_list), chunk_size):
        yield data_list[i:i + chunk_size]

# --- API Endpoint for Analysis ---
@app.route('/api/analyze', methods=['POST'])
def analyze_document_route():
    try:
        data = request.get_json()
        doc_id = data.get('documentId')
        loan_id = data.get('loanId')

        if not doc_id or not loan_id:
            return jsonify({"error": "Document ID and Loan ID are required."}), 400

        pdf_path = os.path.join(DOCUMENT_STORAGE_PATH, f"{doc_id}.pdf")
        if not os.path.exists(pdf_path):
            return jsonify({"error": f"Document with ID '{doc_id}' not found."}), 404
        
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        poppler_path = r"C:\Users\agupta\Downloads\Release-23.11.0-0\poppler-23.11.0\Library\bin"
        
        # 1. Convert PDF to a LIST of PIL images (one image object per page)
        images = convert_from_bytes(pdf_bytes, dpi=200, poppler_path=poppler_path)
        
        if not images:
            return jsonify({"error": "Could not convert PDF to image."}), 400

        total_pages = len(images)
        logging.info(f"PDF has {total_pages} pages. Preparing for AI analysis.")
        
        # 2. Convert PIL images to bytes (with compression logic)
        image_bytes_list = []
        for image in images:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            img_byte_arr = io.BytesIO()
            
            # Optimization: Use JPEG compression for all documents > 6 pages
            if total_pages > MAX_PAGES_SINGLE_CALL:
                 image.save(img_byte_arr, format='JPEG', quality=85) 
            else:
                 image.save(img_byte_arr, format='PNG')
                 
            image_bytes_list.append(img_byte_arr.getvalue())
        
        logging.info(f"Successfully converted all {total_pages} pages to bytes.")
        
        
        # --- CONDITIONAL AI PROCESSING LOGIC (Single vs Chunked) ---
        
        all_ai_extracted_documents = [] # Aggregated list of all extracted documents
        
        # Initialize final_ai_data with default empty values for non-document fields
        final_ai_data = {
            'documents_found': [], 
            'email_body': {'value': None, 'confidence': 10},
            'email_forwarding_analysis': {'is_forwarding': False, 'forwarding_document_type': None, 'confidence': 10}
        }
        
        email_data_found = False
        
        
        if total_pages <= MAX_PAGES_SINGLE_CALL:
            # --- Scenario A: Small Document (Single Call) ---
            logging.warning("Scenario A: Small document (<= 6 pages). Using single API call.")
            
            json_response_string = ai_processor.get_ai_response(image_bytes_list, loan_id)
            chunk_data = json.loads(json_response_string)
            
            if 'error' in chunk_data:
                return jsonify({"error": f"AI analysis failed: {chunk_data['error']}"}), 500
            
            final_ai_data = chunk_data
            all_ai_extracted_documents.extend(chunk_data.get('documents_found', []))
            
        else:
            # --- Scenario B: Large Document (Chunked Calls) ---
            logging.warning(f"Scenario B: Large document (> 6 pages). Splitting into chunks of {MAX_PAGES_PER_CHUNK}.")
            
            page_chunks = list(_chunk_list(image_bytes_list, MAX_PAGES_PER_CHUNK))
            
            for idx, chunk in enumerate(page_chunks):
                logging.warning(f"🚀 Processing Chunk {idx + 1}/{len(page_chunks)} ({len(chunk)} pages)...")
                
                json_response_string = ai_processor.get_ai_response(chunk, loan_id)
                chunk_data = json.loads(json_response_string)
                
                if 'error' in chunk_data:
                    return jsonify({"error": f"AI analysis failed on chunk {idx+1}: {chunk_data['error']}"}), 500
                
                # 3. Aggregate documents found in this chunk
                all_ai_extracted_documents.extend(chunk_data.get('documents_found', []))
                
                # 4. Find the email/forwarding analysis from ANY chunk
                if not email_data_found:
                    email_body = chunk_data.get('email_body')
                    forwarding_analysis = chunk_data.get('email_forwarding_analysis')
                    
                    if email_body and email_body.get('value'):
                        final_ai_data['email_body'] = email_body
                        final_ai_data['email_forwarding_analysis'] = forwarding_analysis
                        email_data_found = True
                        logging.info(f"📧 Email data successfully found in Chunk {idx + 1}.")

        
        # --- FINAL AGGREGATION AND VALIDATION ---
        
        # Overwrite documents_found with the aggregated list
        final_ai_data['documents_found'] = all_ai_extracted_documents
        
        if not final_ai_data.get('documents_found'):
             return jsonify({"error": "AI failed to extract any documents from the analysis. Please check file content."}), 500
             
        
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Run validation and final reporting on the combined data
        ground_truth = data_source.LOAN_DATA_GROUND_TRUTH.get(loan_id)
        final_report = validator.run_all_validations(final_ai_data, ground_truth)
        final_report['document_pdf'] = pdf_base64
        
        logging.info("✅ Final analysis prepared successfully.")
        return jsonify(final_report)

    except Exception as e:
        logging.error(f"An error occurred in '/api/analyze': {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred."}), 500

# --- API Endpoint for Saving Results (No Change) ---
@app.route('/api/save_document', methods=['POST'])
def save_document_route():
    try:
        data = request.get_json()
        doc_id = data.get('documentId')
        if not doc_id:
            return jsonify({"error": "Document ID is required for saving."}), 400

        # --- Save 1: The detailed individual JSON file ---
        json_filename = f"{doc_id}_result.json"
        json_filepath = os.path.join(RESULTS_JSON_PATH, json_filename)
        with open(json_filepath, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Successfully saved detailed result to {json_filepath}")

        # --- Save 2: The summary row in the master CSV log ---
        csv_header = ['Document_ID', 'Loan_ID', 'Final_Status', 'Failure_Modes', 'Timestamp']
        file_exists = os.path.isfile(MASTER_CSV_FILE)

        with open(MASTER_CSV_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_header)
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'Document_ID': doc_id,
                'Loan_ID': data.get('loanId'),
                'Final_Status': data.get('overall_status'),
                'Failure_Modes': ','.join(data.get('failure_modes', [])),
                'Timestamp': datetime.now().isoformat()
            })
        logging.info(f"Successfully appended summary to {MASTER_CSV_FILE}")

        return jsonify({"message": f"Successfully saved review for Document ID {doc_id}"}), 200

    except Exception as e:
        logging.error(f"An error occurred in '/api/save_document': {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred while saving."}), 500

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)