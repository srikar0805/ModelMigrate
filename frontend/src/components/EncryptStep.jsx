import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileDown, Loader2, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

export default function EncryptStep() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setError(null);
    };

    const handleEncrypt = async () => {
        if (!file) {
            setError("Please select a file first.");
            return;
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/api/encrypt', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            // Handle downloads
            const { modified_bim, changes_log_csv } = response.data;

            // Download Modified BIM
            const bimBlob = new Blob([JSON.stringify(modified_bim, null, 2)], { type: 'application/json' });
            const bimUrl = URL.createObjectURL(bimBlob);
            const bimLink = document.createElement('a');
            bimLink.href = bimUrl;
            bimLink.download = 'Encrypted.bim';
            document.body.appendChild(bimLink);
            bimLink.click();
            document.body.removeChild(bimLink);

            // Download CSV
            const csvBlob = new Blob([changes_log_csv], { type: 'text/csv' });
            const csvUrl = URL.createObjectURL(csvBlob);
            const csvLink = document.createElement('a');
            csvLink.href = csvUrl;
            csvLink.download = 'changes_log.csv';
            document.body.appendChild(csvLink);
            csvLink.click();
            document.body.removeChild(csvLink);

            setSuccess(true);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "An error occurred during encryption.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <div className="bg-blue-100 text-blue-600 p-2 rounded-lg">
                    <Upload size={20} />
                </div>
                Step 1: Encrypt Model
            </h2>

            <p className="text-slate-600 mb-6">
                Upload your original <code>.bim</code> file. We will remove spaces from table and column names
                and generate a log of changes needed for restoration.
            </p>

            <div className="space-y-4">
                <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:bg-slate-50 transition-colors">
                    <input
                        type="file"
                        accept=".bim,.json"
                        onChange={handleFileChange}
                        className="hidden"
                        id="encrypt-upload"
                    />
                    <label htmlFor="encrypt-upload" className="cursor-pointer flex flex-col items-center gap-2 text-slate-500 hover:text-blue-600">
                        <Upload size={32} />
                        <span className="font-medium">{file ? file.name : "Click to upload .bim file"}</span>
                    </label>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded-lg flex items-center gap-2 text-sm">
                        <AlertCircle size={16} />
                        {error}
                    </div>
                )}

                <button
                    onClick={handleEncrypt}
                    disabled={loading || !file}
                    className={clsx(
                        "w-full py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-all",
                        loading || !file
                            ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                            : "bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg"
                    )}
                >
                    {loading ? <><Loader2 className="animate-spin" /> Processing...</> : "Encrypt & Download Files"}
                </button>

                {success && (
                    <div className="bg-green-50 text-green-700 p-4 rounded-lg mt-4">
                        <strong>Success!</strong> Two files (<code>Encrypted.bim</code> and <code>changes_log.csv</code>) have been downloaded.
                    </div>
                )}
            </div>
        </div>
    );
}
