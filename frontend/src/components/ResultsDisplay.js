
import React, { useState, useEffect, useRef } from 'react';
import EditableField from './EditableField';
import SummaryModal from './SummaryModal';
import { saveDocumentReview } from '../api/analyzerService';

// --- PDF.js setup ---
const PDFJS_URL = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js';
const PDF_WORKER_URL = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js`;

// --- Icons ---
const Icon = ({ name, className }) => {
    const icons = {
        warning: <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>,
        success: <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
        zoomIn: <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" /></svg>,
        zoomOut: <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" /></svg>,
        spinner: <svg className={`animate-spin ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
    };
    return icons[name] || null;
};

const fieldNameMapping = {
    client: 'Client', classification: 'Classification', parcel_number: 'Parcel Number',
    loan_id: 'Loan ID', property_address: 'Property Address', tax_year: 'Tax Year',
    base_tax_amount: 'Base Tax Amount', total_tax_paid: 'Total Tax Paid',
    date_paid: 'Date Paid', check_number: 'Check Number',
};


export default function ResultsDisplay({ resultData, onReset, documentId }) {
    const [fields, setFields] = useState(resultData.fields);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState('');
    const [pdfDoc, setPdfDoc] = useState(null);
    const [isPdfLoading, setIsPdfLoading] = useState(true);
    const [pageNum, setPageNum] = useState(1);
    const [numPages, setNumPages] = useState(0);
    const [scale, setScale] = useState(1.5);
    const [highlightedField, setHighlightedField] = useState(null);
    const canvasRef = useRef(null);

    useEffect(() => {
        const loadPdfLibrary = () => {
            if (window.pdfjsLib) {
                initializePdf();
            } else {
                const script = document.createElement('script');
                script.src = PDFJS_URL;
                script.async = true;
                script.onload = () => {
                    window.pdfjsLib.GlobalWorkerOptions.workerSrc = PDF_WORKER_URL;
                    initializePdf();
                };
                document.body.appendChild(script);
                return () => {
                    if (document.body.contains(script)) { document.body.removeChild(script); }
                };
            }
        };

        const initializePdf = () => {
            try {
                const pdfData = atob(resultData.document_pdf);
                const loadingTask = window.pdfjsLib.getDocument({ data: pdfData });
                loadingTask.promise.then(doc => {
                    setPdfDoc(doc);
                    setNumPages(doc.numPages);
                    setIsPdfLoading(false);
                }).catch(error => { console.error("Error loading PDF document:", error); setIsPdfLoading(false); });
            } catch (error) { console.error("Error decoding PDF data:", error); setIsPdfLoading(false); }
        };
        loadPdfLibrary();
    }, [resultData.document_pdf]);

    useEffect(() => {
        if (!pdfDoc || isPdfLoading) return;
        pdfDoc.getPage(pageNum).then(page => {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            const viewport = page.getViewport({ scale });
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            const renderContext = { canvasContext: ctx, viewport };
            page.render(renderContext).promise.then(() => {
                if (highlightedField && fields[highlightedField]?.bounding_box) {
                    const bbox = fields[highlightedField].bounding_box;
                    if (bbox && bbox.every(coord => typeof coord === 'number')) {
                        const [x1, y1, x2, y2] = bbox;
                        const pageView = page.view;
                        const imageWidth = pageView[2];
                        const imageHeight = pageView[3];
                        const viewportScaleX = viewport.width / imageWidth;
                        const viewportScaleY = viewport.height / imageHeight;
                        ctx.fillStyle = 'rgba(255, 255, 0, 0.3)';
                        ctx.strokeStyle = 'rgba(255, 215, 0, 0.7)';
                        ctx.lineWidth = 2;
                        const rectX = x1 * viewportScaleX;
                        const rectY = y1 * viewportScaleY;
                        const rectWidth = (x2 - x1) * viewportScaleX;
                        const rectHeight = (y2 - y1) * viewportScaleY;
                        ctx.fillRect(rectX, rectY, rectWidth, rectHeight);
                        ctx.strokeRect(rectX, rectY, rectWidth, rectHeight);
                    }
                }
            });
        });
    }, [pdfDoc, pageNum, scale, highlightedField, fields, isPdfLoading]);

    const handleFieldUpdate = (fieldKey, newValue) => {
        setFields(prev => ({ ...prev, [fieldKey]: { ...prev[fieldKey], value: newValue }}));
    };
    
    const handleFieldFocus = (fieldKey) => setHighlightedField(fieldKey);
    const handleSave = () => {
        setSaveMessage(''); 
        setIsModalOpen(true);
    };
    const handleCloseModal = () => setIsModalOpen(false);

    const handleConfirmSave = async () => {
        if (!documentId) {
            setSaveMessage('Error: Document ID is missing. Cannot save.');
            return;
        }
        setIsSaving(true);
        setSaveMessage('');
        const payload = {
            documentId: documentId,
            loanId: fields.loan_id?.value || '',
            overall_status: resultData.overall_status,
            failure_modes: resultData.failure_modes,
            fields: fields,
        };
        try {
            const response = await saveDocumentReview(payload);
            setSaveMessage(response.message || 'Save successful!');
            setTimeout(() => {
                setIsModalOpen(false);
                onReset();
            }, 2000);
        } catch (error) {
            console.error("Save failed:", error);
            setSaveMessage(`Error: ${error.message}`);
        } finally {
            setIsSaving(false);
        }
    };

    const isReviewNeeded = resultData.overall_status === 'Needs Manual Review';
    const filteredFields = Object.fromEntries(
        Object.entries(fields).filter(([key]) => !key.endsWith('_confidence'))
    );
    
    return (
        <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-lg border border-gray-200 flex flex-col">
             {isModalOpen && (
                <SummaryModal
                    finalData={{ fields: filteredFields, failure_modes: resultData.failure_modes }}
                    onClose={handleCloseModal}
                    onConfirm={handleConfirmSave}
                    isSaving={isSaving}
                    saveMessage={saveMessage}
                />
            )}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 flex-grow">
                {/* Document Viewer Column */}
                <div className="bg-gray-100 p-4 rounded-lg shadow-inner h-[80vh] flex flex-col">
                    <div className="flex-shrink-0 flex justify-center items-center space-x-4 mb-2 p-2 bg-gray-200 rounded-md">
                        <button disabled={pageNum <= 1} onClick={() => setPageNum(p => p - 1)} className="font-bold disabled:opacity-50">&lt;</button>
                        <span>Page {pageNum} of {numPages}</span>
                        <button disabled={pageNum >= numPages} onClick={() => setPageNum(p => p + 1)} className="font-bold disabled:opacity-50">&gt;</button>
                        <div className="w-px h-5 bg-gray-400"></div>
                        <button onClick={() => setScale(s => s * 1.2)}><Icon name="zoomIn" className="h-5 w-5"/></button>
                        <button onClick={() => setScale(s => s / 1.2)}><Icon name="zoomOut" className="h-5 w-5"/></button>
                    </div>
                    <div className="flex-grow overflow-auto text-center">
                        {isPdfLoading ? (
                            <div className="flex items-center justify-center h-full">
                                <Icon name="spinner" className="h-8 w-8 text-indigo-600" />
                                <span className="ml-3 text-gray-600">Loading document...</span>
                            </div>
                        ) : ( <canvas ref={canvasRef} /> )}
                    </div>
                </div>
                {/* Data Column */}
                <div className="h-[80vh] overflow-y-auto pr-2">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Validation Verdict</h3>
                    <div className={`p-4 rounded-lg flex items-start ${isReviewNeeded ? 'bg-yellow-50 text-yellow-800' : 'bg-green-50 text-green-800'}`}>
                        <Icon name={isReviewNeeded ? 'warning' : 'success'} className="h-6 w-6 mr-3 mt-1 flex-shrink-0" />
                        <div>
                            <h4 className="font-bold text-lg">{resultData.overall_status}</h4>
                            {isReviewNeeded && resultData.failure_modes.length > 0 && (
                                <div className="mt-2 text-sm">
                                    <p className="font-semibold">Failure Codes:</p>
                                    <ul className="list-disc list-inside">
                                        {resultData.failure_modes.map(code => <li key={code} className="font-mono">{code}</li>)}
                                    </ul>
                                </div>
                            )}
                            {!isReviewNeeded && <p className="text-sm text-green-700">All validation checks passed.</p>}
                        </div>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800 my-4">Extracted Data</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-6">
                        {Object.entries(filteredFields).map(([key, fieldData]) => (
                            <EditableField key={key} fieldKey={key} label={fieldNameMapping[key] || key} fieldData={fieldData} onUpdate={handleFieldUpdate} onFocus={handleFieldFocus} />
                        ))}
                    </div>
                </div>
            </div>
            {/* Action Buttons */}
            <div className="mt-10 pt-6 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
                <button onClick={onReset} className="px-6 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-200 rounded-lg transition-colors">
                    Analyze Another Document
                </button>
                <button onClick={handleSave} className="px-10 py-3 bg-indigo-600 text-white font-bold rounded-lg shadow-md hover:bg-indigo-700 transition-all duration-300 transform hover:scale-105">
                    Approve & Save
                </button>
            </div>
        </div>
    );
}


