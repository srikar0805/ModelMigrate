import React from 'react';
import { ArrowRight, CloudCog } from 'lucide-react';

export default function Instructions() {
    return (
        <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <div className="bg-purple-100 text-purple-600 p-2 rounded-lg">
                    <CloudCog size={20} />
                </div>
                Step 2: External Workflow
            </h2>

            <div className="space-y-4 text-slate-700">
                <p>
                    After encrypting your model in Step 1, perform your external migration tasks:
                </p>
                <ol className="list-decimal list-inside space-y-2 ml-4">
                    <li>Open <strong>Tabular Editor</strong> or your <strong>Fabric</strong> workspace.</li>
                    <li>Import the <code>Encrypted.bim</code> file.</li>
                    <li>Perform your migration or data source updates.</li>
                    <li>The system will handle the renamed tables (no spaces) correctly.</li>
                    <li>Save/Export the resulting model as a new <code>.bim</code> file.</li>
                </ol>
                <div className="flex items-center gap-2 text-sm text-slate-500 mt-4 bg-white p-3 rounded-lg border border-slate-200">
                    <ArrowRight size={16} />
                    <span>Once you have the new model, proceed to Step 3 below.</span>
                </div>
            </div>
        </div>
    );
}
