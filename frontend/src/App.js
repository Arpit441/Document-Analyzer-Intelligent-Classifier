

// import React, { useState } from 'react';
// import Header from './components/Header';
// import Stepper from './components/Stepper';
// import ResultsDisplay from './components/ResultsDisplay';
// import { analyzeDocument } from './api/analyzerService';
// import IdInputForm from './components/IdInputForm'; // <-- New Component

// function App() {
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);
//   const [result, setResult] = useState(null);
//   const [currentStep, setCurrentStep] = useState(1);

//   // --- FIX: handleAnalyze now takes IDs, not a file ---
//   const handleAnalyze = async ({ documentId, loanId, clientNumber }) => {
//     if (!documentId || !loanId || !clientNumber) {
//       setError("Please fill in all ID fields.");
//       return;
//     }
//     setLoading(true);
//     setError(null);
//     setResult(null);
//     try {
//       // Pass the IDs to the API service
//       const data = await analyzeDocument({ documentId, loanId, clientNumber });
//       setResult(data);
//       setCurrentStep(2); // Move to the review step
//     } catch (e) {
//       console.error("Analysis failed:", e);
//       setError(`Analysis failed: ${e.message}`);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleReset = () => {
//       setResult(null);
//       setError(null);
//       setCurrentStep(1);
//   }

//   return (
//     <div className="bg-gray-50 min-h-screen font-sans text-gray-800">
//       <Header />
//       <div className="container mx-auto p-4 sm:p-8 max-w-6xl">
//         <Stepper currentStep={currentStep} />
//         <main className="mt-8">
//             {/* --- FIX: Uploader is replaced with the new IdInputForm --- */}
//             {currentStep === 1 && (
//                 <IdInputForm
//                     onAnalyze={handleAnalyze}
//                     loading={loading}
//                 />
//             )}

//             {error && (
//                 <div className="mt-6 p-4 bg-red-100 text-red-800 border-l-4 border-red-500 rounded-r-lg shadow" role="alert">
//                     <strong className="font-bold">Error: </strong>
//                     <span>{error}</span>
//                 </div>
//             )}
            
//             {currentStep === 2 && result && (
//                 <ResultsDisplay resultData={result} onReset={handleReset} />
//             )}
//         </main>
//       </div>
//     </div>
//   );
// }

// export default App;
import React, { useState } from 'react';
import Header from './components/Header';
import Stepper from './components/Stepper';
import IdInputForm from './components/IdInputForm';
import ResultsDisplay from './components/ResultsDisplay';
import { analyzeDocument } from './api/analyzerService';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);
  // State to hold the documentId for the current session
  const [currentDocumentId, setCurrentDocumentId] = useState(null);

  const handleAnalyze = async (documentId, loanId, clientNumber) => {
    setLoading(true);
    setError(null);
    setResult(null);
    // Store the documentId when analysis starts
    setCurrentDocumentId(documentId); 
    try {
      const data = await analyzeDocument( documentId, loanId, clientNumber );
      setResult(data);
      setCurrentStep(2);
    } catch (e) {
      console.error("Analysis failed:", e);
      setError(`Analysis failed: ${e.message}`);
      // If analysis fails, reset so user can try again
      setCurrentStep(1); 
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
      setResult(null);
      setError(null);
      setCurrentStep(1);
      // Clear the documentId on reset
      setCurrentDocumentId(null);
  }

  return (
    <div className="bg-gray-50 min-h-screen font-sans text-gray-800">
      <Header />
      <div className="container mx-auto p-4 sm:p-8 max-w-7xl">
        <Stepper currentStep={currentStep} />
        <main className="mt-8">
            {currentStep === 1 && (
                <IdInputForm onAnalyze={handleAnalyze} loading={loading} />
            )}

            {error && (
                <div className="mt-6 p-4 bg-red-100 text-red-800 border-l-4 border-red-500 rounded-r-lg shadow" role="alert">
                    <strong className="font-bold">Error: </strong>
                    <span>{error}</span>
                </div>
            )}
            
            {currentStep === 2 && result && (
                <ResultsDisplay 
                  resultData={result} 
                  onReset={handleReset} 
                  // Pass the stored documentId down to the results component
                  documentId={currentDocumentId}
                />
            )}
        </main>
      </div>
    </div>
  );
}

export default App;

