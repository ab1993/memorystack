"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { SprintPlan, Topic } from '@/types';
import {CheckCircle, ArrowRight, BrainCircuit, Sparkles} from 'lucide-react';

export default function SprintPage() {
    const [plan, setPlan] = useState<SprintPlan | null>(null);
    const [allTopics, setAllTopics] = useState<Topic[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [layer, setLayer] = useState(1); // 1: Gist, 2: Pattern, 3: Questions
    const [isDone, setIsDone] = useState(false);
    const router = useRouter();

    useEffect(() => {
        const savedPlan = localStorage.getItem('currentSprint');
        if (!savedPlan) {
            router.push('/');
            return;
        }
        setPlan(JSON.parse(savedPlan));
        api.getTopics().then(setAllTopics);
    }, []);

    // Get the flat list of topics for this sprint
    const sprintTopics = plan?.sprint_plan || [];
    const currentItem = sprintTopics[currentIndex];
    const topicData = allTopics.find(t => t.topic === currentItem?.topic);

    if (!plan || !topicData) return <div className="p-10 text-white">Loading your path...</div>;

    const handleNextLayer = () => {
        if (layer < 3) setLayer(layer + 1);
    };

    const handleRating = async (rating: number) => {
        await api.submitReview(topicData.id, rating);

        if (currentIndex < sprintTopics.length - 1) {
            setCurrentIndex(currentIndex + 1);
            setLayer(1);
        } else {
            setIsDone(true);
        }
    };

    const handleGenerate = async () => {
        if (!topic) return;

        try {
            const response = await fetch(`http://localhost:8000/topics/generate?topic_name=${topic}`, {
                method: 'POST',
            });

            if (response.ok) {
                console.log("Topic generated and pushed!");
                setTopic(""); // Clear the input
                // Optionally: Refresh your topic list here
            }
        } catch (error) {
            console.error("Generation failed", error);
        }
    };

    if (isDone) {
        return (
            <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-center p-6">
                <CheckCircle size={80} className="text-emerald-500 mb-6" />
                <h1 className="text-4xl font-bold text-white mb-4">Sprint Completed!</h1>
                <p className="text-slate-400 mb-8">Your memory stability has been updated. Ready for the next one?</p>
                <button
                    onClick={() => router.push('/')}
                    className="bg-blue-600 px-8 py-3 rounded-xl font-bold text-white"
                >
                    Back to Stack
                </button>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
            <div className="max-w-3xl mx-auto">
                {/* Progress Header */}
                <div className="flex justify-between items-center mb-12">
                    <button onClick={() => router.push('/')} className="text-slate-500 hover:text-white">Exit Sprint</button>
                    <div className="text-sm font-mono text-slate-500">
                        Topic {currentIndex + 1} of {sprintTopics.length}
                    </div>
                </div>

                <button
                    onClick={handleGenerate}
                    className="absolute right-2 top-2 p-3 bg-blue-600 hover:bg-blue-500 rounded-xl transition-colors"
                >
                    <Sparkles size={20} />
                </button>

                {/* The Card */}
                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 md:p-12 shadow-2xl">
          <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-bold uppercase tracking-widest">
            {topicData.category}
          </span>
                    <h2 className="text-4xl font-black mt-4 mb-8">{topicData.topic}</h2>

                    {/* Layer 1: Gist */}
                    <div className="space-y-8">
                        <div className={`transition-opacity duration-500 ${layer >= 1 ? 'opacity-100' : 'opacity-0'}`}>
                            <h4 className="text-emerald-400 font-bold text-sm uppercase mb-2">Layer 1: The Gist</h4>
                            <p className="text-xl leading-relaxed text-slate-300">{topicData.layer_1_gist}</p>
                        </div>

                        {/* Layer 2: Pattern */}
                        {layer >= 2 && (
                            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <h4 className="text-blue-400 font-bold text-sm uppercase mb-2">Layer 2: The Pattern</h4>
                                <p className="text-lg leading-relaxed text-slate-300">{topicData.layer_2_pattern}</p>
                            </div>
                        )}

                        {/* Layer 3: Questions */}
                        {layer >= 3 && (
                            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <h4 className="text-purple-400 font-bold text-sm uppercase mb-2">Layer 3: Top Challenges</h4>
                                <ul className="space-y-3">
                                    {(() => {
                                        const rawQuestions = topicData?.layer_3_questions;

                                        // 1. If it's already a valid array, use it
                                        if (Array.isArray(rawQuestions) && rawQuestions.length > 0) {
                                            return rawQuestions.map((q, i) => (
                                                <li key={i} className="flex gap-3 items-start bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                                                    <BrainCircuit className="text-purple-400 shrink-0 mt-1" size={18} />
                                                    <span className="text-slate-200">{q}</span>
                                                </li>
                                            ));
                                        }

                                        // 2. If it's a string that looks like a JSON array, parse it
                                        if (typeof rawQuestions === 'string' && rawQuestions.startsWith('[')) {
                                            try {
                                                const parsed = JSON.parse(rawQuestions);
                                                return parsed.map((q: string, i: number) => (
                                                    <li key={i} className="flex gap-3 items-start bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                                                        <BrainCircuit className="text-purple-400 shrink-0 mt-1" size={18} />
                                                        <span className="text-slate-200">{q}</span>
                                                    </li>
                                                ));
                                            } catch (e) {
                                                console.error("Failed to parse questions string", e);
                                            }
                                        }

                                        return <p className="text-slate-500 italic">No practice questions available for this topic yet.</p>;
                                    })()}
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* Action Area */}
                    <div className="mt-12 pt-8 border-t border-slate-800">
                        {layer < 3 ? (
                            <button
                                onClick={handleNextLayer}
                                className="w-full py-4 bg-white text-slate-950 font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-slate-200 transition-all"
                            >
                                Reveal Next Layer <ArrowRight size={20} />
                            </button>
                        ) : (
                            <div>
                                <p className="text-center text-sm text-slate-500 mb-4">How well did you recall this?</p>
                                <div className="grid grid-cols-4 gap-3">
                                    {[
                                        { val: 1, label: "Forgot", color: "hover:bg-red-500" },
                                        { val: 2, label: "Hard", color: "hover:bg-orange-500" },
                                        { val: 3, label: "Good", color: "hover:bg-emerald-500" },
                                        { val: 4, label: "Easy", color: "hover:bg-blue-500" }
                                    ].map(r => (
                                        <button
                                            key={r.val}
                                            onClick={() => handleRating(r.val)}
                                            className={`py-3 rounded-lg bg-slate-800 font-bold transition-colors ${r.color}`}
                                        >
                                            {r.label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </main>
    );
}