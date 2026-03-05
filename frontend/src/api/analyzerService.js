

// const API_BASE_URL = 'http://127.0.0.1:5000/api';

// // --- FIX: This function now sends IDs instead of a file ---
// export const analyzeDocument = async ({ documentId, loanId, clientNumber }) => {
  
//   const response = await fetch(`${API_BASE_URL}/analyze`, {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify({
//       documentId,
//       loanId,
//       clientNumber,
//     }),
//   });

//   if (!response.ok) {
//     // Try to get a meaningful error message from the backend
//     const errData = await response.json().catch(() => ({})); // Gracefully handle non-json errors
//     throw new Error(errData.error || `Server responded with status: ${response.status}`);
//   }

//   return response.json();
// };

/**
 * This file centralizes all API calls to the backend.
 */
const API_BASE_URL = 'http://127.0.0.1:5000/api';

/**
 * Fetches a document from the backend using IDs and gets the AI analysis.
 */
export const analyzeDocument = async (documentId, loanId, clientNum) => {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ documentId, loanId, clientNum }),
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || `Server responded with status: ${response.status}`);
    }

    return response.json();
};

/**
 * Sends the final, corrected review data to the backend to be saved.
 */
export const saveDocumentReview = async (reviewData) => {
    const response = await fetch(`${API_BASE_URL}/save_document`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(reviewData),
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || `Server responded with status: ${response.status}`);
    }

    return response.json();
}


