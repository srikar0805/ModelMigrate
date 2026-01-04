import React, { useState } from 'react';
import axios from 'axios';
import { Download, Loader2, AlertCircle, FileCheck } from 'lucide-react';
import clsx from 'clsx';

export default function DecryptStep() {
    const [files, setFiles] = useState({
        encrypted: null,
        log: null,
        original: null
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handleFileChange = (type) => (e) => {
        setFiles(prev => ({ ...prev, [type]: e.target.files[0] }));
        setError(null);
    };

    const handleDecrypt = async () => {
        if (!files.encrypted || !files.log || !files.original) {
            setError("Please upload all three required files.");
            return;
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('encrypted_file', files.encrypted);
        formData.append('log_file', files.log);
        formData.append('original_file', files.original);

        try {
            const response = await axios.post('http://localhost:8000/api/decrypt', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            // Download Decrypted BIM
            const bimBlob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
            const bimUrl = URL.createObjectURL(bimBlob);
            const bimLink = document.createElement('a');
            bimLink.href = bimUrl;
            bimLink.download = 'Restored_Model.bim';
            document.body.appendChild(bimLink);
            bimLink.click();
            document.body.removeChild(bimLink);

            setSuccess(true);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "An error occurred during decryption.");
        } finally {
            setLoading(false);
        }
    };

    const FileInput = ({ label, type, accept, currentFile }) => (
        <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">{label}</label>
            <div className="flex items-center gap-3">
                <label className="flex-1 cursor-pointer">
                    <input type="file" accept={accept} onChange={handleFileChange(type)} className="hidden" />
                    <div className="border border-slate-300 rounded-lg px-4 py-2 hover:bg-slate-50 text-sm truncate flex items-center justify-between">
                        <span className={currentFile ? "text-slate-900" : "text-slate-400"}>
                            {currentFile ? currentFile.name : "Choose file..."}
                        </span>
                        {currentFile && <FileCheck size={16} className="text-green-500" />}
                    </div>
                </label>
            </div>
        </div>
    );

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <div className="bg-green-100 text-green-600 p-2 rounded-lg">
                    <Download size={20} />
                </div>
                Step 3: Decrypt & Restore
            </h2>

            <p className="text-slate-600 mb-6">
                Upload the modified model from your external tool, the changes log, and the original file to restore names and hierarchies.
            </p>

            <div className="space-y-4">
                <FileInput
                    label="Modified Model (from Tabular/Fabric)"
                    type="encrypted"
                    accept=".bim,.json"
                    currentFile={files.encrypted}
                />
                <FileInput
                    label="Changes Log (CSV)"
                    type="log"
                    accept=".csv"
                    currentFile={files.log}
                />
                <FileInput
                    label="Original Model (for hierarchies)"
                    type="original"
                    accept=".bim,.json"
                    currentFile={files.original}
                />

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded-lg flex items-center gap-2 text-sm">
                        <AlertCircle size={16} />
                        {error}
                    </div>
                )}

                <button
                    onClick={handleDecrypt}
                    disabled={loading || !files.encrypted || !files.log || !files.original}
                    className={clsx(
                        "w-full py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-all mt-4",
                        loading || !files.encrypted
                            ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                            : "bg-green-600 text-white hover:bg-green-700 shadow-md hover:shadow-lg"
                    )}
                >
                    {loading ? <><Loader2 className="animate-spin" /> Restoring...</> : "Restore Model"}
                </button>

                {success && (
                    <div className="bg-green-50 text-green-700 p-4 rounded-lg mt-4">
                        <strong>Success!</strong> Your restored model has been downloaded.
                    </div>
                )}
            </div>
        </div>
    );
}
