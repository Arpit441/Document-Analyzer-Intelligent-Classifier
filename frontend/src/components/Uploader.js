import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const Icon = ({ name, className }) => {
    const icons = {
        upload: <svg className={className} stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true"><path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>,
        pdf: <svg className={className} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4 2a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V8.414a1 1 0 00-.293-.707l-4.414-4.414A1 1 0 0011.586 3H4zm3 8a1 1 0 001 1h4a1 1 0 100-2H8a1 1 0 00-1 1zm0 4a1 1 0 100-2h4a1 1 0 100 2H7z" clipRule="evenodd" /></svg>,
        spinner: <svg className={`animate-spin ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
    };
    return icons[name] || null;
};

export default function Uploader({ onFileSelect, onAnalyze, loading, file }) {
  const onDrop = useCallback(acceptedFiles => {
    const acceptedFile = acceptedFiles[0];
    if (acceptedFile && acceptedFile.type === 'application/pdf') {
      onFileSelect(acceptedFile);
    } else {
      alert("Please upload a valid PDF file.");
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: { 'application/pdf': ['.pdf'] } });

  return (
    <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-lg border border-gray-200/80">
      <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors duration-300 ${isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'}`}>
        <input {...getInputProps()} />
        <div className="flex flex-col items-center">
          <Icon name="upload" className="mx-auto h-12 w-12 text-gray-400"/>
          {isDragActive ?
            <p className="mt-4 text-indigo-600 font-medium">Drop the PDF here...</p> :
            <p className="mt-4 text-gray-500">Drag & drop a PDF file here, or click to select</p>
          }
        </div>
      </div>
      {file && (
        <div className="mt-6 p-4 bg-gray-100 rounded-lg flex items-center justify-between animate-fade-in">
          <div className="flex items-center">
            <Icon name="pdf" className="h-6 w-6 text-red-500"/>
            <span className="ml-3 font-medium text-gray-700">{file.name}</span>
          </div>
          <button onClick={() => onFileSelect(null)} className="text-sm text-red-600 hover:text-red-800 font-semibold">Remove</button>
        </div>
      )}
      <div className="mt-8 text-center">
        <button
          onClick={onAnalyze}
          disabled={!file || loading}
          className="w-full sm:w-auto px-12 py-3 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 flex items-center justify-center mx-auto"
        >
          {loading ? <Icon name="spinner" className="-ml-1 mr-3 h-5 w-5"/> : 'Analyze Document'}
        </button>
      </div>
    </div>
  );
}
