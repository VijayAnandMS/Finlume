import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";

const ReceiptHistoryPage: React.FC = () => {
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            setLoading(true);
            const res = await api.get("/api/receipts/history");
            setHistory(res.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to load audit timelines.");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (!window.confirm("Are you sure you want to permanently delete this receipt audit?")) return;
        try {
            await api.delete(`/api/receipts/history/${id}`);
            fetchHistory();
        } catch (err) {
            alert("Error deleting receipt tracking boundaries");
        }
    };

    return (
        <div className="bg-gray-900 min-h-screen text-white p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                    Receipt Processing History
                </h1>
                <Link to="/import/workflow" className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded text-sm font-bold shadow-[0_0_10px_rgba(37,99,235,0.5)]">
                    Upload New Receipt
                </Link>
            </div>

            {loading ? (
                <div>Loading history grids...</div>
            ) : error ? (
                <div className="text-red-500">{error}</div>
            ) : history.length === 0 ? (
                <div className="text-gray-400">No processing history found.</div>
            ) : (
                <div className="overflow-x-auto bg-gray-800 rounded border border-gray-700 shadow-xl">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-gray-900 text-gray-400 text-sm border-b border-gray-700">
                                <th className="p-4">Timestamps</th>
                                <th className="p-4">Status</th>
                                <th className="p-4">Confidence</th>
                                <th className="p-4">Alerts</th>
                                <th className="p-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.map((record) => (
                                <tr key={record.id} className="border-b border-gray-700 hover:bg-gray-750 transition-colors">
                                    <td className="p-4 text-sm text-gray-300">
                                        <div className="mb-1"><span className="text-blue-400 text-xs">UPLOAD:</span> {record.upload_timestamp?.slice(0, 19).replace("T", " ") || "N/A"}</div>
                                        <div className="mb-1"><span className="text-purple-400 text-xs">OCR:</span> {record.ocr_timestamp?.slice(0, 19).replace("T", " ") || "N/A"}</div>
                                        <div><span className="text-green-400 text-xs">AI:</span> {record.ai_timestamp?.slice(0, 19).replace("T", " ") || "N/A"}</div>
                                    </td>
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${record.processing_status === 'PREVIEW_READY' ? 'bg-blue-600 text-white' :
                                            record.processing_status === 'FAILED' ? 'bg-red-600 text-white' : 'bg-gray-600 text-white'
                                            }`}>
                                            {record.processing_status}
                                        </span>
                                    </td>
                                    <td className="p-4 text-sm font-bold">
                                        {record.confidence_summary > 0 ? (record.confidence_summary * 100).toFixed(0) + '%' : 'N/A'}
                                    </td>
                                    <td className="p-4">
                                        {JSON.parse(record.manual_review_flags || "[]").length > 0 ? (
                                            <span className="text-yellow-400 text-xs flex items-center gap-1">
                                                ⚠️ Review Needed
                                            </span>
                                        ) : <span className="text-gray-500 text-xs">None</span>}
                                    </td>
                                    <td className="p-4 flex gap-3">
                                        <Link to={`/receipts/${record.receipt_session_id}/preview`} className="text-blue-400 hover:text-blue-300 text-sm underline">
                                            View Preview
                                        </Link>
                                        <button onClick={() => handleDelete(record.receipt_session_id)} className="text-red-400 hover:text-red-300 text-sm underline">
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default ReceiptHistoryPage;
