import React from 'react';

const Logo = () => (
    <svg className="h-8 w-auto" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 30L24 18L36 30" stroke="#4F46E5" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 18L24 6L36 18" stroke="#A5B4FC" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
);

export default function Header() {
    return (
        <header className="bg-white shadow-sm">
            <div className="container mx-auto px-4 sm:px-8 py-4 flex items-center">
                <Logo />
                <h1 className="text-xl font-bold text-gray-800 ml-3">Document Review AI</h1>
            </div>
        </header>
    );
}
