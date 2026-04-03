import React, { useState, useEffect } from 'react';
import { useLocation, useParams, useNavigate } from 'react-router-dom';
import { 
    CheckCircle2, XCircle, MessageSquare, Eye, 
    BrainCircuit, Activity, ThumbsUp, TrendingUp, AlertCircle 
} from 'lucide-react';

const ResultPage = () => {
    const { sessionId } = useParams(); 
    const location = useLocation();
    const navigate = useNavigate();
    
    const [results, setResults] = useState(location.state?.results || null);
    const [isLoading, setIsLoading] = useState(!location.state?.results);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (results) return;

        const fetchResults = async () => {
            try {
                const res = await fetch(`http://localhost:8080/api/interview/results/${sessionId}`);
                if (!res.ok) throw new Error("Failed to fetch results from database.");
                
                const data = await res.json();
                setResults(data.results);
            } catch (err) {
                console.error(err);
                setError("Could not load your interview results.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchResults();
    }, [sessionId, results]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
                <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
                <p className="text-slate-500 font-medium animate-pulse">Retrieving your scores from the database...</p>
            </div>
        );
    }

    if (error || !results || results.length === 0) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
                <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
                <h2 className="text-2xl font-bold mb-2">Results not found</h2>
                <p className="text-slate-500 mb-6">{error || "This interview session might not exist."}</p>
                <button onClick={() => navigate('/')} className="bg-slate-900 text-white px-6 py-3 rounded-xl font-bold">Go Home</button>
            </div>
        );
    }

    const totalScore = results.reduce((acc, curr) => acc + (curr.analysis?.grading?.holistic_score || 0), 0);
    const averageScore = Math.round(totalScore / results.length);

    // 👇 FIX 2: Sort the results by question_id before rendering them
    const sortedResults = [...results].sort((a, b) => {
        return Number(a.question_id) - Number(b.question_id);
    });

 
    return (
        <div className="min-h-screen bg-slate-50 font-sans text-slate-900 pb-20">
            {/* Header section */}
            <header className="bg-slate-900 text-white pt-16 pb-24 px-6 text-center">
                <div className="max-w-3xl mx-auto">
                    <div className="w-20 h-20 bg-blue-500 rounded-3xl mx-auto mb-6 flex items-center justify-center shadow-2xl shadow-blue-500/50">
                        <Activity size={40} className="text-white" />
                    </div>
                    <h1 className="text-4xl md:text-5xl font-black mb-4">Interview Analysis Complete</h1>
                    <p className="text-slate-400 text-lg">Session #{sessionId.split('-')[0]}</p>
                </div>
            </header>

            <main className="max-w-5xl mx-auto px-4 -mt-12 space-y-8">
                {/* Overall Score Card */}
                <div className="bg-white rounded-3xl p-8 shadow-xl shadow-slate-200/50 border border-slate-100 flex flex-col md:flex-row items-center gap-8">
                    <div className="shrink-0 text-center">
                        <div className="text-6xl font-black text-blue-600 mb-2">{averageScore}<span className="text-3xl text-slate-300">/10</span></div>
                        <p className="text-xs font-bold uppercase tracking-widest text-slate-400">Average Score</p>
                    </div>
                    <div className="flex-1 space-y-4">
                        <h3 className="text-2xl font-bold">Great effort!</h3>
                        <p className="text-slate-600 leading-relaxed">
                            You demonstrated a solid understanding of the core concepts. Review the detailed breakdown below to see exactly which technical keywords you missed and how your non-verbal communication scored.
                        </p>
                    </div>
                </div>

                {/* Individual Question Breakdown */}
                <h2 className="text-2xl font-black px-4 pt-8">Question Breakdown</h2>
                
                {sortedResults.map((res, index) => {
                    const grading = res.analysis?.grading || {};
                    const vision = res.analysis?.vision || {};
                    const speech = res.analysis?.speech || {};

                    return (
                        <div key={index} className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
                            <div className="bg-slate-50 p-6 border-b border-slate-100 flex justify-between items-center">
                                <div>
                                    <p className="text-xs font-black uppercase tracking-widest text-blue-600 mb-1">Question {index + 1}</p>
                                    <h3 className="text-lg font-bold text-slate-800">"{res.original_question}"</h3>
                                </div>
                                <div className="text-3xl font-black text-slate-900 ml-4">
                                    {grading.holistic_score || 0}<span className="text-lg text-slate-400">/10</span>
                                </div>
                            </div>

                            <div className="p-6 md:p-8 grid md:grid-cols-2 gap-8">
                                {/* Left Col: Tech Accuracy & Transcript */}
                                <div className="space-y-6">
                                    <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                                        <h4 className="font-bold flex items-center gap-2 mb-4"><BrainCircuit size={18} className="text-blue-600"/> Technical Accuracy</h4>
                                        <ul className="space-y-3">
                                            {grading.hit_concepts?.map((concept, i) => (
                                                <li key={`hit-${i}`} className="flex items-start gap-3 text-sm">
                                                    <CheckCircle2 size={18} className="text-green-500 shrink-0 mt-0.5" />
                                                    <span className="text-slate-700 font-medium capitalize">{concept}</span>
                                                </li>
                                            ))}
                                            {grading.missing_concepts?.map((concept, i) => (
                                                <li key={`miss-${i}`} className="flex items-start gap-3 text-sm">
                                                    <XCircle size={18} className="text-red-400 shrink-0 mt-0.5" />
                                                    <span className="text-slate-500 line-through capitalize">{concept}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                    <div>
                                        <h4 className="font-bold flex items-center gap-2 mb-3 text-sm text-slate-500 uppercase tracking-wider"><MessageSquare size={16}/> Transcript</h4>
                                        <p className="text-slate-600 text-sm leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100 italic">
                                            "{speech.transcript || "No audio detected."}"
                                        </p>
                                    </div>
                                </div>

                                {/* Right Col: AI Feedback & Non-Verbals */}
                                <div className="space-y-6">
                                    <div>
                                        <h4 className="font-bold mb-3">AI Evaluator Feedback</h4>
                                        <p className="text-slate-700 text-sm leading-relaxed mb-4">{grading.feedback}</p>
                                        <div className="space-y-3 text-sm">
                                            {grading.strengths?.length > 0 && (
                                                <div className="flex gap-2 text-green-700 bg-green-50 p-3 rounded-lg border border-green-100">
                                                    <ThumbsUp size={16} className="shrink-0 mt-0.5"/> 
                                                    <span>{grading.strengths[0]}</span>
                                                </div>
                                            )}
                                            {grading.improvements?.length > 0 && (
                                                <div className="flex gap-2 text-amber-700 bg-amber-50 p-3 rounded-lg border border-amber-100">
                                                    <TrendingUp size={16} className="shrink-0 mt-0.5"/> 
                                                    <span>{grading.improvements[0]}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-slate-900 text-white p-4 rounded-2xl">
                                            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mb-1 flex items-center gap-1"><Eye size={12}/> Eye Contact</p>
                                            <p className="text-2xl font-black">{vision.eye_contact_percentage || 0}%</p>
                                        </div>
                                        <div className="bg-slate-50 border border-slate-200 p-4 rounded-2xl">
                                            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">Emotion</p>
                                            <p className="text-xl font-bold text-slate-800 capitalize">{vision.dominant_emotion || "Unknown"}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })}

                <div className="pt-8 text-center">
                    <button onClick={() => navigate('/users/1')} className="bg-slate-900 text-white px-8 py-4 rounded-2xl font-bold shadow-xl hover:bg-slate-800 transition-all">
                        Back to Dashboard
                    </button>
                </div>
            </main>
        </div>
    );
};

export default ResultPage;