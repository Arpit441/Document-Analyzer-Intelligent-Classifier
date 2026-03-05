
import React from 'react';

const Step = ({ number, title, isActive }) => {
    return (
        <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${isActive ? 'bg-indigo-600' : 'bg-gray-300'}`}>
                {number}
            </div>
            <span className={`ml-3 font-medium ${isActive ? 'text-indigo-600' : 'text-gray-500'}`}>{title}</span>
        </div>
    );
};

export default function Stepper({ currentStep }) {
    return (
        <div className="w-full max-w-md mx-auto mb-10 flex justify-between items-center">
            {/* --- FIX: Updated step 1 title --- */}
            <Step number={1} title="Fetch Document" isActive={currentStep >= 1} />
            <div className="flex-1 h-0.5 bg-gray-300 mx-4"></div>
            <Step number={2} title="Review & Approve" isActive={currentStep >= 2} />
        </div>
    );
}
