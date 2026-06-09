"use client";

import { useState, useRef, useEffect } from 'react';
import { Terminal, Play, MessageSquare, Trash2, FileCode2, Edit3 } from 'lucide-react';
import Editor from '@monaco-editor/react';

type Message = { role: 'user' | 'assistant', content: string };

export default function Dashboard() {
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [generatedCode, setGeneratedCode] = useState("");
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  
  // NEW: Explicit Mode State
  const [mode, setMode] = useState<'fresh' | 'iterate'>('iterate');
  
  const wsRef = useRef<WebSocket | null>(null);
  const terminalEndRef = useRef<HTMLDivElement>(null);
  const isInitialized = useRef(false);

  useEffect(() => {
    const hydrateStorage = async () => {
      const saved = localStorage.getItem("ale_history");
      if (saved) setChatHistory(JSON.parse(saved));
      isInitialized.current = true;
    };
    hydrateStorage();
  }, []);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [terminalLogs]);

  useEffect(() => {
    if (isInitialized.current) {
      localStorage.setItem("ale_history", JSON.stringify(chatHistory));
    }
  }, [chatHistory]);

  const startEngine = () => {
    if (!prompt.trim() || isProcessing) return;
    setIsProcessing(true);
    setTerminalLogs([`[ALE] Executing in ${mode.toUpperCase()} mode...`]);
    setChatHistory(prev => [...prev, { role: 'user', content: prompt }]);
    
    wsRef.current = new WebSocket("ws://127.0.0.1:8000/ws/stream");
    
    wsRef.current.onopen = () => {
      wsRef.current?.send(JSON.stringify({ 
        history: chatHistory, 
        prompt: prompt,
        current_code: generatedCode,
        mode: mode // NEW: Send explicit mode to Python
      }));
      setPrompt("");
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'node_update') {
        setTerminalLogs(prev => [...prev, `[PIPELINE] Booting node: ${data.node}`]);
        if (data.state.generated_code) setGeneratedCode(data.state.generated_code);
        if ((data.node === 'EXECUTOR' || data.node === 'GENERAL') && data.state.terminal_output) {
            setTerminalLogs(prev => [...prev, `[EXECUTION OUTPUT]\n${data.state.terminal_output}`]);
        }
      } else if (data.type === 'complete') {
        setIsProcessing(false);
        setTerminalLogs(prev => [...prev, "[SYSTEM] Pipeline execution terminated successfully."]);
        setChatHistory(prev => [...prev, { role: 'assistant', content: "Task handled." }]);
        wsRef.current?.close();
      } else if (data.type === 'error') {
        setIsProcessing(false);
        setTerminalLogs(prev => [...prev, `[FATAL ERROR] ${data.message}`]);
        wsRef.current?.close();
      }
    };

    wsRef.current.onerror = () => {
      setIsProcessing(false);
      setTerminalLogs(prev => [...prev, "[SYSTEM] WebSocket Connection Failed."]);
    };
    wsRef.current.onclose = () => setIsProcessing(false);
  };

  const clearHistory = () => {
    localStorage.removeItem("ale_history");
    setChatHistory([]);
    setGeneratedCode("");
    setTerminalLogs([]);
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) setGeneratedCode(value);
  };

  return (
    <div className="h-screen bg-[#0d1117] text-[#c9d1d9] font-mono flex">
      <div className="w-1/5 border-r border-[#30363d] bg-[#161b22] flex flex-col">
        <div className="p-4 border-b border-[#30363d] font-bold flex justify-between items-center text-green-500">
          ALE Workspace <button onClick={clearHistory} className="text-gray-500 hover:text-red-500"><Trash2 size={16}/></button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {chatHistory.map((msg, i) => (
            <div key={i} className={`text-xs p-2 rounded border border-[#30363d] ${msg.role === 'user' ? 'bg-[#21262d]' : 'text-blue-400'}`}>
              {msg.content}
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <div className="p-4 border-b border-[#30363d] bg-[#161b22] flex items-center gap-4">
          
          {/* NEW: Mode Toggle Switch */}
          <div className="flex items-center gap-1 bg-[#0d1117] p-1 rounded border border-[#30363d]">
            <button 
              onClick={() => setMode('fresh')} 
              className={`flex items-center gap-1 px-3 py-1.5 text-xs font-bold rounded ${mode === 'fresh' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-200'}`}
            >
              <FileCode2 size={14} /> Fresh
            </button>
            <button 
              onClick={() => setMode('iterate')} 
              className={`flex items-center gap-1 px-3 py-1.5 text-xs font-bold rounded ${mode === 'iterate' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-200'}`}
            >
              <Edit3 size={14} /> Iterate
            </button>
          </div>

          <input 
            value={prompt} 
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && startEngine()}
            className="flex-1 bg-[#0d1117] border border-[#30363d] rounded p-2 text-sm focus:border-green-500 outline-none"
            placeholder={mode === 'fresh' ? "Describe a new script to write..." : "Describe how to modify the current code..."}
            disabled={isProcessing}
          />
          <button onClick={startEngine} disabled={isProcessing} className="bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:text-gray-500 px-4 py-2 rounded text-sm font-bold flex items-center gap-2">
            <Play size={14} /> Execute
          </button>
        </div>

        <div className="flex-1">
          <Editor height="100%" language="python" theme="vs-dark" value={generatedCode} onChange={handleEditorChange} options={{ readOnly: false, minimap: { enabled: false } }} />
        </div>

        <div className="h-1/3 border-t border-[#30363d] bg-[#0a0c10] p-4 overflow-y-auto">
          <div className="text-xs text-green-500 font-bold mb-2 uppercase flex items-center gap-2">
            <Terminal size={12} /> Sandbox Logs
          </div>
          {terminalLogs.map((log, i) => <div key={i} className="text-xs text-[#7ee787] whitespace-pre-wrap">{log}</div>)}
          <div ref={terminalEndRef} />
        </div>
      </div>
    </div>
  );
}