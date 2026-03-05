
// import React, { useState, useEffect } from 'react';

// export default function EditableField({ label, fieldData, onUpdate, fieldKey }) {
//     const [value, setValue] = useState('');

//     useEffect(() => {
//         // This ensures the input updates if the parent data changes
//         setValue(fieldData.value || '');
//     }, [fieldData.value]);

//     const handleBlur = () => {
//         onUpdate(fieldKey, value);
//     };

//     const baseClasses = "w-full p-2.5 border rounded-lg shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 text-gray-800 text-sm";
//     const statusClasses = {
//         trusted: "bg-green-50 border-green-300 focus:ring-green-500",
//         review: "bg-yellow-50 border-yellow-400 focus:ring-yellow-500",
//     };
    
//     return (
//         <div>
//             <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
//             <input 
//                 type="text"
//                 value={value}
//                 onChange={(e) => setValue(e.target.value)}
//                 onBlur={handleBlur}
//                 className={`${baseClasses} ${statusClasses[fieldData.status] || 'bg-gray-50 border-gray-300'}`}
//             />
//             {/* --- FIX: Display dynamic confidence and specific reasons separately --- */}
//             <div className="flex justify-between items-center mt-1 text-xs h-4">
//                 <span className={fieldData.status === 'review' ? 'text-yellow-600 font-semibold' : 'text-gray-500'}>
//                     {/* Show reason only if it's a specific validation error (not the generic confidence one) */}
//                     {(fieldData.reason && !fieldData.reason.includes('Confidence')) ? fieldData.reason : ''}
//                 </span>
//                 <span className="text-gray-400 font-mono ml-2">
//                     {`Score: ${fieldData.confidence}/10`}
//                 </span>
//             </div>
//         </div>
//     );
// }
import React, { useState, useEffect } from 'react';

export default function EditableField({ label, fieldData, onUpdate, onFocus, fieldKey }) {
    const [value, setValue] = useState('');

    useEffect(() => {
        setValue(fieldData.value || '');
    }, [fieldData.value]);

    const handleBlur = () => {
        onUpdate(fieldKey, value);
    };

    const baseClasses = "w-full p-2.5 border rounded-lg shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 text-gray-800 text-sm";
    const statusClasses = {
        trusted: "bg-green-50 border-green-300 focus:ring-green-500",
        review: "bg-yellow-50 border-yellow-400 focus:ring-yellow-500",
    };
    
    // Call the onFocus handler when the input is clicked or focused
    const handleFocus = () => {
        if (onFocus) {
            onFocus(fieldKey);
        }
    };

    return (
        <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
            <input 
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onBlur={handleBlur}
                onFocus={handleFocus}
                onClick={handleFocus} // Also handle click for reliability
                className={`${baseClasses} ${statusClasses[fieldData.status] || 'bg-gray-50 border-gray-300'}`}
            />
             <div className="text-xs mt-1 h-8 flex flex-col">
                <span className="font-mono text-gray-500">
                    Score: {fieldData.confidence || 'N/A'}/10
                </span>
                {fieldData.reason && fieldData.status === 'review' && (
                     <span className="font-semibold text-yellow-600 truncate">{fieldData.reason}</span>
                )}
            </div>
        </div>
    );
}

