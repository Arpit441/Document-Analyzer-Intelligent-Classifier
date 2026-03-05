import React from 'react';

const Icon = ({ name, className }) => {
    const icons = {
        spinner: <svg className={`animate-spin ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>,
        success: <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
    };
    return icons[name] || null;
};


export default function SummaryModal({ finalData, onClose, onConfirm, isSaving, saveMessage }) {
    if (!finalData) return null;

    const { fields, failure_modes } = finalData;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center p-4 z-50 animate-fade-in">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-8 transform transition-all">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Final Submission Summary</h2>
                <p className="text-gray-600 mb-6">Please review the final data before completing the process.</p>
                
                <div className="bg-gray-50 rounded-lg p-4 max-h-80 overflow-y-auto border">
                    <h3 className="text-lg font-semibold text-gray-700 mb-3">Validated Fields</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 text-sm">
                        {Object.entries(fields).map(([key, data]) => (
                            <div key={key}>
                                <strong className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}:</strong>
                                <p className="text-gray-800 font-medium break-words">{data.value || 'N/A'}</p>
                            </div>
                        ))}
                    </div>
                    
                    {failure_modes && failure_modes.length > 0 && (
                         <div className="mt-4 pt-4 border-t">
                             <h3 className="text-lg font-semibold text-gray-700 mb-2">Original Failure Codes</h3>
                             <div className="flex flex-wrap gap-2">
                                {failure_modes.map(code => (
                                     <span key={code} className="bg-yellow-100 text-yellow-800 text-xs font-mono font-bold px-2 py-1 rounded-full">{code}</span>
                                 ))}
                             </div>
                         </div>
                    )}
                </div>

                <div className="mt-6 h-6">
                    {saveMessage && (
                        <div className={`flex items-center justify-center text-sm font-semibold ${saveMessage.includes('Error') ? 'text-red-600' : 'text-green-600'}`}>
                           {saveMessage.includes('successful') && <Icon name="success" className="h-5 w-5 mr-2"/>}
                           {saveMessage}
                        </div>
                    )}
                </div>

                <div className="mt-4 flex justify-end space-x-4">
                    <button 
                        onClick={onClose}
                        disabled={isSaving}
                        className="px-6 py-2 text-sm font-semibold text-gray-600 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors disabled:opacity-50"
                    >
                        Cancel
                    </button>
                     <button 
                        onClick={onConfirm}
                        disabled={isSaving || (saveMessage && saveMessage.includes('successful'))}
                        className="px-8 py-2 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-700 transition-all duration-300 flex items-center justify-center disabled:bg-indigo-300"
                    >
                        {isSaving ? <Icon name="spinner" className="h-5 w-5"/> : 'Confirm & Submit'}
                    </button>
                </div>
            </div>
        </div>
    );
}

