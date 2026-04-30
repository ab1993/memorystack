"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Topic, SprintPlan } from '@/types';
import { useRouter } from 'next/navigation';
import {Send, CheckCircle, ExternalLink, BrainCircuit, Loader2} from "lucide-react";

export default function Dashboard() {
    const [topics, setTopics] = useState<Topic[]>([]);
    const [selected, setSelected] = useState<string[]>([]);
    const [interviewDate, setInterviewDate] = useState("");
    const [newTopicName, setNewTopicName] = useState("");
    const [isLearning, setIsLearning] = useState(false);
    const router = useRouter();
    const [isLinked, setIsLinked] = useState(false);
    const [isPolling, setIsPolling] = useState(false);
    const TELEGRAM_BOT_NAME = "MemoryStackBot";
    const userId = 929325646; // This would come from your Auth context later

    // Load initial topics from DB
    useEffect(() => {
        api.getTopics().then(setTopics).catch(console.error);
    }, []);

    const handleTeachMe = async () => {
        if (!newTopicName) return;
        setIsLearning(true);
        try {
            const addedTopic = await api.generateTopic(newTopicName);
            setTopics([...topics, addedTopic]);
            setNewTopicName("");
        } catch (err) {
            alert("AI failed to learn this topic. Check backend logs.");
        } finally {
            setIsLearning(false);
        }
    };

    const toggleSelection = (name: string) => {
        setSelected(prev =>
            prev.includes(name) ? prev.filter(t => t !== name) : [...prev, name]
        );
    };

    const startSprint = async () => {
        if (!interviewDate || selected.length === 0) {
            alert("Please select topics and a date!");
            return;
        }
        try {
            const plan = await api.generateSprint(interviewDate, selected);
            // For now, we'll store the plan in localStorage to pass it to the next page
            localStorage.setItem('currentSprint', JSON.stringify(plan));
            router.push('/sprint');
        } catch (err) {
            alert("Failed to generate plan.");
        }
    };

    const checkStatus = async () => {
        try {
            const res = await fetch('http://localhost:8000/user/1/status');
            const data = await res.json();
            if (data.telegram_chat_id) {
                setIsLinked(true);
                setIsPolling(false);
            }
        } catch (e) { console.error("Handshake pending..."); }
    };

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isPolling && !isLinked) {
            interval = setInterval(checkStatus, 3000);
        }
        return () => clearInterval(interval);
    }, [isPolling, isLinked]);

    const handleConnect = () => {
        setIsPolling(true);
        // Replace with your actual bot name from @BotFather
        window.open(`https://t.me/${TELEGRAM_BOT_NAME}?start=${userId}`, '_blank');
    };

    const connectTelegram = () => {
        // Deep link with the internal user ID as a parameter
        window.open(`https://t.me/${TELEGRAM_BOT_NAME}?start=${userId}`, '_blank');
    };
    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">

            {/* --- 2. THE HEADER (Put the Link Here) --- */}
            <header className="sticky top-0 z-50 flex justify-between items-center px-8 py-4 bg-black/40 backdrop-blur-xl border-b border-white/5">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/20 rounded-lg">
                        <BrainCircuit className="text-blue-400" size={24} />
                    </div>
                    <div>
                        <h1 className="font-bold text-lg tracking-tight">MemoryStack</h1>
                        <p className="text-[10px] text-slate-500 uppercase tracking-widest">v1.0 Beta</p>
                    </div>
                </div>

                {/* --- TELEGRAM STATUS AREA --- */}
                <div className="flex items-center gap-4">
                    {isLinked ? (
                        <div className="flex items-center gap-2 px-4 py-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-xs font-semibold shadow-[0_0_15px_rgba(16,185,129,0.1)]">
                            <CheckCircle size={14} />
                            Bot Active
                        </div>
                    ) : (
                        <button
                            onClick={handleConnect}
                            className="group relative flex items-center gap-2 px-5 py-2 bg-[#229ED9] hover:bg-[#229ED9]/90 text-white text-xs font-bold rounded-full transition-all active:scale-95 shadow-lg shadow-blue-500/20"
                        >
                            {isPolling ? <Loader2 className="animate-spin" size={14} /> : <Send size={14} />}
                            {isPolling ? "Awaiting Handshake..." : "Sync Telegram"}
                        </button>
                    )}
                </div>
            </header>


            <div className="max-w-5xl mx-auto">
                <header className="mb-12">
                    <h1 className="text-5xl font-extrabold tracking-tight mb-3 bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                        MemoryStack
                    </h1>
                    <p className="text-slate-400 text-lg">Focus on patterns, not just problems.</p>
                </header>

                <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column: Topic Selection */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                placeholder="Topic name (e.g. Heaps)"
                                className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={newTopicName}
                                onChange={(e) => setNewTopicName(e.target.value)}
                            />
                            <button
                                onClick={handleTeachMe}
                                disabled={isLearning}
                                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 px-6 py-3 rounded-lg font-bold transition-all"
                            >
                                {isLearning ? "AI Thinking..." : "Add to Stack"}
                            </button>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {topics.map(t => (
                                <div
                                    key={t.id}
                                    onClick={() => toggleSelection(t.topic)}
                                    className={`p-5 rounded-2xl border-2 cursor-pointer transition-all ${
                                        selected.includes(t.topic)
                                            ? 'border-blue-500 bg-blue-500/10 shadow-[0_0_15px_rgba(59,130,246,0.3)]'
                                            : 'border-slate-800 bg-slate-900 hover:border-slate-700'
                                    }`}
                                >
                                    <span className="text-[10px] font-black uppercase tracking-widest text-blue-400">{t.category}</span>
                                    <h3 className="text-xl font-bold mt-1">{t.topic}</h3>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Right Column: Sprint Settings */}
                    <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl h-fit sticky top-8">
                        <h2 className="text-2xl font-bold mb-6">Sprint Settings</h2>

                        <label className="block text-sm font-semibold text-slate-400 mb-2">INTERVIEW DATE</label>
                        <input
                            type="date"
                            className="w-full bg-slate-800 border-none rounded-xl px-4 py-3 mb-8 text-white focus:ring-2 focus:ring-emerald-500"
                            value={interviewDate}
                            onChange={(e) => setInterviewDate(e.target.value)}
                        />

                        <div className="space-y-4 mb-8">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-400">Topics Selected</span>
                                <span className="font-bold text-blue-400">{selected.length}</span>
                            </div>
                        </div>
                        <button
                            onClick={startSprint}
                            className="w-full py-4 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black rounded-xl transition-all uppercase tracking-tight"
                        >
                            Generate Revision Path
                        </button>
                    </div>
                </section>
            </div>
        </div>
    );
}