// import React, { useState } from 'react';

// const Icon = ({ name, className }) => {
//     const icons = {
//         spinner: <svg className={`animate-spin ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>,
//         search: <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
//     };
//     return icons[name] || null;
// };

// const InputField = ({ id, label, value, onChange, placeholder }) => (
//     <div>
//         <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
//         <input
//             type="text"
//             id={id}
//             value={value}
//             onChange={onChange}
//             placeholder={placeholder}
//             className="w-full p-3 border border-gray-300 rounded-lg shadow-sm transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500"
//         />
//     </div>
// );


// export default function IdInputForm({ onAnalyze, loading }) {
//     const [documentId, setDocumentId] = useState('');
//     const [loanId, setLoanId] = useState('');
//     const [clientNumber, setClientNumber] = useState('');

//     const handleSubmit = (e) => {
//         e.preventDefault();
//         onAnalyze({ documentId, loanId, clientNumber });
//     };

//     const canAnalyze = documentId && loanId && clientNumber && !loading;

//     return (
//         <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-lg border border-gray-200/80">
//             <h2 className="text-xl font-semibold text-gray-800 mb-2">Fetch Document for Review</h2>
//             <p className="text-gray-500 mb-6">Enter the identifiers for the document you wish to analyze.</p>
//             <form onSubmit={handleSubmit}>
//                 <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//                     <InputField 
//                         id="documentId"
//                         label="Document ID"
//                         value={documentId}
//                         onChange={(e) => setDocumentId(e.target.value)}
//                         placeholder="e.g., 1039977909"
//                     />
//                     <InputField 
//                         id="loanId"
//                         label="Loan ID"
//                         value={loanId}
//                         onChange={(e) => setLoanId(e.target.value)}
//                         placeholder="e.g., 775308166"
//                     />
//                     <InputField 
//                         id="clientNumber"
//                         label="Client Number"
//                         value={clientNumber}
//                         onChange={(e) => setClientNumber(e.target.value)}
//                         placeholder="e.g., 12301"
//                     />
//                 </div>
//                 <div className="mt-8 text-center">
//                     <button
//                         type="submit"
//                         disabled={!canAnalyze}
//                         className="w-full sm:w-auto px-12 py-3 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 flex items-center justify-center mx-auto"
//                     >
//                         {loading ? <Icon name="spinner" className="-ml-1 mr-3 h-5 w-5"/> : <><Icon name="search" className="mr-2 h-5 w-5" />Fetch & Analyze Document</>}
//                     </button>
//                 </div>
//             </form>
//         </div>
//     );
// }
import React, { useState } from 'react';

const Icon = ({ name, className }) => {
    const icons = {
        spinner: <svg className={`animate-spin ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
    };
    return icons[name] || null;
};

export default function IdInputForm({ onAnalyze, loading }) {
    const [documentId, setDocumentId] = useState('');
    const [loanId, setLoanId] = useState('');
    const [clientNumber, setClientNumber] = useState('');
    const [formError, setFormError] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!documentId || !loanId) {
            setFormError('Document ID and Loan ID are required.');
            return;
        }
        setFormError('');
        // --- FIX: Pass the IDs as three separate arguments, not as a single object ---
        onAnalyze(documentId, loanId, clientNumber);
    };

    return (
        <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-lg border border-gray-200/80 max-w-2xl mx-auto">
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Start a New Review</h2>
            <p className="text-gray-500 mb-6">Enter the document identifiers to fetch and analyze the file.</p>
            <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                    <label htmlFor="documentId" className="block text-sm font-medium text-gray-700 mb-1">Document ID</label>
                    <input
                        type="text" id="documentId" value={documentId}
                        onChange={(e) => setDocumentId(e.target.value)}
                        className="w-full p-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="e.g., 775308166"
                    />
                </div>
                <div>
                    <label htmlFor="loanId" className="block text-sm font-medium text-gray-700 mb-1">Loan ID</label>
                    <input
                        type="text" id="loanId" value={loanId}
                        onChange={(e) => setLoanId(e.target.value)}
                        className="w-full p-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="e.g., 775308166"
                    />
                </div>
                <div>
                    <label htmlFor="clientNumber" className="block text-sm font-medium text-gray-700 mb-1">Client Number (Optional)</label>
                    <input
                        type="text" id="clientNumber" value={clientNumber}
                        onChange={(e) => setClientNumber(e.target.value)}
                        className="w-full p-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="e.g., 12301"
                    />
                </div>

                {formError && <p className="text-sm text-red-600 font-semibold">{formError}</p>}

                <div className="pt-2 text-center">
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full sm:w-auto px-16 py-3 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 flex items-center justify-center mx-auto"
                    >
                        {loading ? <Icon name="spinner" className="-ml-1 mr-3 h-5 w-5"/> : 'Fetch & Analyze Document'}
                    </button>
                </div>
            </form>
        </div>
    );
}

