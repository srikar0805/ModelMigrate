import React from 'react';
import EncryptStep from './components/EncryptStep';
import DecryptStep from './components/DecryptStep';
import Instructions from './components/Instructions';
import { Layers } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <div className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg text-white shadow-lg shadow-blue-200">
            <Layers size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">ModelMigrate</h1>
            <p className="text-xs text-slate-500 font-medium">Tabular to Fabric Semantic Model Migration Tool</p>
          </div>
        </div>
      </div>

      <main className="max-w-3xl mx-auto px-6 py-12 space-y-8">
        <EncryptStep />

        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-slate-200 -z-10 hidden md:block"></div>
        </div>

        <Instructions />

        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-slate-200 -z-10 hidden md:block"></div>
        </div>

        <DecryptStep />
      </main>

      <footer className="max-w-5xl mx-auto px-6 py-12 text-center text-slate-400 text-sm">
        <p>&copy; {new Date().getFullYear()} ModelMigrate. Built with React & FastAPI.</p>
      </footer>
    </div>
  );
}

export default App;
