import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../services/api";

const ReceiptPreviewPage: React.FC = () => {
  const { receipt_session_id } = useParams<{ receipt_session_id: string }>();
  const navigate = useNavigate();
  
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Editable state
  const [editForm, setEditForm] = useState<any>({});

  useEffect(() => {
    const fetchPreview = async () => {
      try {
        setLoading(true);
        // Automatically attempt to process the endpoint securely generating unified outputs
        const res = await api.post(`/api/receipts/${receipt_session_id}/process`);
        setData(res.data);
        
        const parsed = JSON.parse(res.data.parsed_data || "{}");
        setEditForm({
          merchant_name: parsed.merchant_name || "",
          transaction_date: parsed.transaction_date || "",
          subtotal: parsed.subtotal || 0,
          tax: parsed.tax || 0,
          total: parsed.total || 0,
          currency: parsed.currency || "USD"
        });
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load receipt preview.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchPreview();
  }, [receipt_session_id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditForm({ ...editForm, [e.target.name]: e.target.value });
  };

  const handleConfirm = () => {
    // Phase 17.5 blocks persistence; UI just fakes confirmation 
    alert("Receipt Data Ready for Import Confirmation!");
    navigate("/dashboard");
  };

  if (loading) return <div className="text-white p-8">Processing AI Intelligence...</div>;
  if (error) return <div className="text-red-500 p-8">{error}</div>;

  const aiSuggestions = JSON.parse(data.ai_suggestions || "{}");
  const warnings = JSON.parse(data.warnings || "[]");
  const reviewFlags = JSON.parse(data.review_flags || "[]");

  return (
    <div className="bg-gray-900 min-h-screen text-white p-8">
      <h1 className="text-3xl font-bold mb-6">Receipt Preview & Validation</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Receipt Visualizer (Placeholder box mimicking visual storage mapping safely) */}
        <div className="bg-gray-800 p-6 rounded border border-gray-700 flex flex-col items-center justify-center min-h-[500px]">
          <span className="text-gray-400 block mb-4">Receipt Image Render bounds</span>
          <div className="w-full h-full bg-gray-700/50 rounded flex items-center justify-center">
             [Image Rendering Placeholder]
          </div>
        </div>

        {/* Data Validation Form */}
        <div className="bg-gray-800 p-6 rounded border border-gray-700">
          <div className="mb-6 flex justify-between items-center">
            <h2 className="text-xl font-semibold text-blue-400">Extracted Values</h2>
            
            {data.confidence_score > 0 && (
              <span className={`px-3 py-1 rounded text-sm font-bold ${data.confidence_score > 0.8 ? 'bg-green-600' : 'bg-yellow-600'}`}>
                Confidence: {(data.confidence_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
          
          <div className="mb-4">
            <p className="text-sm text-gray-400 mb-1">AI Category Prediction</p>
            <p className="text-lg font-bold text-purple-400">{aiSuggestions.category || "Uncategorized"}</p>
          </div>
          
          <form className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400">Merchant Name</label>
              <input name="merchant_name" value={editForm.merchant_name} onChange={handleChange} className="w-full bg-gray-900 border border-gray-700 p-2 rounded text-white" />
              {aiSuggestions.corrections?.merchant_name && <p className="text-xs text-green-400 mt-1">AI Suggestion: {aiSuggestions.corrections.merchant_name}</p>}
            </div>
            
            <div>
              <label className="block text-sm text-gray-400">Date</label>
              <input type="date" name="transaction_date" value={editForm.transaction_date} onChange={handleChange} className="w-full bg-gray-900 border border-gray-700 p-2 rounded text-white" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400">Total Amount</label>
                <input type="number" name="total" value={editForm.total} onChange={handleChange} className="w-full bg-gray-900 border border-gray-700 p-2 rounded text-white font-bold" />
              </div>
              <div>
                <label className="block text-sm text-gray-400">Currency</label>
                <input name="currency" value={editForm.currency} onChange={handleChange} className="w-full bg-gray-900 border border-gray-700 p-2 rounded text-white" />
              </div>
            </div>
            
             <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400">Subtotal</label>
                <input type="number" name="subtotal" value={editForm.subtotal} onChange={handleChange} className="w-full bg-gray-900 border border-gray-700 p-2 rounded text-white" />
              </div>
              <div>
                <label className="block text-sm text-gray-400">Tax</label>
                <input type="number" name="tax" value={editForm.tax} onChange={handleChange} className="w-full bg-gray-900 border border-gray-700 p-2 rounded text-white" />
              </div>
            </div>
          </form>

          {/* Warnings Panel */}
          {(warnings.length > 0 || reviewFlags.length > 0) && (
            <div className="mt-6 bg-red-900/20 border border-red-500/50 p-4 rounded text-sm text-red-400">
               <h3 className="font-bold mb-2">Validation Warnings</h3>
               <ul className="list-disc pl-5 space-y-1">
                 {warnings.map((w: string, i: number) => <li key={`w-${i}`}>{w}</li>)}
                 {reviewFlags.map((w: string, i: number) => <li key={`r-${i}`}>{w}</li>)}
               </ul>
            </div>
          )}

          <div className="mt-8 flex justify-end">
            <button onClick={handleConfirm} className="bg-blue-600 hover:bg-blue-500 px-6 py-2 rounded font-bold text-white transition-colors shadow-[0_0_15px_rgba(37,99,235,0.5)]">
              Approve Receipt
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReceiptPreviewPage;
