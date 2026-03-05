AI-Powered Document Review & Validation Engine
This project is a full-stack application designed to automate the manual review process for financial and tax documents. It leverages a multimodal AI (Google's Gemini 1.5 Flash) to extract data from PDF documents and then runs a series of business-critical validation checks to ensure data accuracy and compliance with Service Level Agreements (SLAs).

The system is designed to significantly reduce manual effort, increase data accuracy, and flag exceptions for human review in a clear and actionable user interface.

Key Features
Intelligent Data Extraction: Uses a multimodal AI to visually analyze documents, allowing it to extract data from varied layouts, including unstructured text like emails.

Automated Business Rule Validation: Automatically checks extracted data against a "source of truth" to detect common errors and business rule violations.

Failure Mode Detection: Identifies and flags specific failure modes based on a predefined matrix:

M2: Document Type Mismatch

M4: Situs Address / Parcel Number Mismatch

M7: Client SLA Breach

M8: Client Not Found in Master List

Confidence Scoring: Each piece of extracted data is assigned a confidence score, and fields with low confidence are flagged for review.

Interactive Frontend: A user-friendly React interface allows users to upload documents, view the color-coded validation results, correct data in editable fields, and approve documents.

Technology Stack
Frontend: React, Tailwind CSS

Backend: Python, Flask

AI / Machine Learning: Google Gemini 1.5 Flash API

PDF Processing: pdf2image, Poppler

Getting Started
Prerequisites
Node.js and npm (for the frontend)

Python 3.8+ and pip (for the backend)

Poppler: This is a critical dependency for converting PDFs to images.

macOS: brew install poppler

Linux (Ubuntu/Debian): sudo apt-get install poppler-utils

Windows: Download the binaries and add the bin folder to your system's PATH.

Installation & Setup
Clone the repository:

git clone [https://your-repository-url.com/document-review-ai.git](https://your-repository-url.com/document-review-ai.git)
cd document-review-ai

Backend Setup:

cd backend
pip install -r requirements.txt

Create a .env file in the backend directory.

Add your Google Gemini API key to the .env file:

GOOGLE_API_KEY="YOUR_API_KEY_HERE"

Crucially for Windows users, open app.py and update the poppler_path variable to point to your Poppler installation's bin folder.

Frontend Setup:

cd ../frontend
npm install

Running the Application
You will need to run two separate terminal commands simultaneously.

Start the Backend Server:

Open a terminal, navigate to the backend folder, and run:

python app.py

The backend will be running at http://127.0.0.1:5000.

Start the Frontend Application:

Open a second terminal, navigate to the frontend folder, and run:

npm start

The frontend will open in your browser at http://localhost:3000.

How to Use
Open http://localhost:3000 in your web browser.

Drag and drop a PDF document into the upload area or click to select a file.

Click the "Analyze Document" button.

Wait for the processing to complete. The system will display the results.

Review the overall status (Success or Needs Manual Review) and any failure codes.

Inspect the extracted data in the form. Fields are color-coded (green for trusted, yellow for review).

Correct any data as needed and click "Approve & Save".