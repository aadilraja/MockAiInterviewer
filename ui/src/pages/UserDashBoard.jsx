import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from "react-router-dom";
import { Plus, Clock, BrainCircuit, ArrowRight, Activity, Calendar } from 'lucide-react';
import axios from "axios";

const Dashboard = () => {
    // Grab the logged-in user's ID from the URL
    const { userId } = useParams();
    const navigate = useNavigate();

    const [username, setUsername] = useState("Developer");
    const [sessions, setSessions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                // 1. Fetch User Info
                const userRes = await axios.get(`http://localhost:8080/api/users/${userId}`);
                setUsername(userRes.data.username || "Developer");

                // 2. Fetch User's Past Interview Sessions from the database
                const sessionRes = await axios.get(`http://localhost:8080/api/interview/history/${userId}`);
                setSessions(sessionRes.data.sessions || []);

            } catch (err) {
                console.error("Error fetching dashboard data:", err);
            } finally {
                setIsLoading(false);
            }
        };

        if (userId) {
            fetchDashboardData();
        }
    }, [userId]);

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-4 md:p-8 font-sans">
            
            {/* Header Section */}
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-6 border-b border-slate-800 pb-8">
                <div>
                    <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2">
                        Welcome back, <span className="text-sky-400">{username}</span>
                    </h1>
                    <p className="text-slate-400 flex items-center gap-2">
                        <Activity size={16} className="text-emerald-400" />
                        Ready to improve your technical communication?
                    </p>
                </div>
                <button 
                    // Make sure this points to your Interview Setup Page!
                    onClick={() => navigate(`/Interview/${userId}`)} 
                    className="group flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-sky-500 hover:from-indigo-500 hover:to-sky-400 text-white px-8 py-4 rounded-2xl font-bold transition-all shadow-lg shadow-indigo-500/20 active:scale-95 text-lg"
                >
                    <Plus size={24} />
                    Start New Interview
                </button>
            </header>

            {/* Past Sessions Grid */}
            <main>
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Clock className="text-indigo-400" /> Your Interview History
                    </h2>
                    <span className="bg-slate-900 text-slate-400 px-3 py-1 rounded-full text-sm font-bold border border-slate-800">
                        {sessions.length} Total Sessions
                    </span>
                </div>

                {isLoading ? (
                    <div className="flex flex-col items-center justify-center py-20 text-slate-500">
                        <div className="w-10 h-10 border-4 border-slate-800 border-t-sky-500 rounded-full animate-spin mb-4"></div>
                        <p>Loading your history...</p>
                    </div>
                ) : sessions.length === 0 ? (
                    <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-12 text-center">
                        <BrainCircuit size={64} className="mx-auto text-slate-700 mb-6" />
                        <h3 className="text-2xl font-bold text-white mb-2">No interviews yet!</h3>
                        <p className="text-slate-400 max-w-md mx-auto mb-8">
                            Click the button above to start your first AI mock interview and get detailed feedback on your performance.
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {sessions.map((session, index) => (
                            <div 
                                key={index}
                                // Clicking a card takes you straight to the AI analysis for that session
                                onClick={() => navigate(`/result/${session.session_id}`)}
                                className="bg-slate-900 border border-slate-800 p-6 rounded-3xl hover:border-indigo-500/50 hover:bg-slate-800/80 transition-all cursor-pointer group shadow-xl"
                            >
                                <div className="flex justify-between items-start mb-6">
                                    <div className="bg-slate-950 p-3 rounded-2xl border border-slate-800">
                                        <BrainCircuit className="text-sky-400" size={24} />
                                    </div>
                                    <div className="text-right">
                                        <span className="text-3xl font-black text-white">{session.avg_score || 0}</span>
                                        <span className="text-slate-500">/10</span>
                                        <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mt-1">Avg Score</p>
                                    </div>
                                </div>
                                
                                <div className="space-y-3 mb-6">
                                    <div className="flex items-center gap-3 text-slate-400 text-sm">
                                        <Calendar size={16} />
                                        <span>{new Date(session.created_at).toLocaleDateString()}</span>
                                    </div>
                                    <div className="flex items-center gap-3 text-slate-400 text-sm">
                                        <Clock size={16} />
                                        <span>{session.questions_answered} Questions Answered</span>
                                    </div>
                                </div>

                                <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-indigo-400 font-bold group-hover:text-sky-400 transition-colors">
                                    <span>View AI Analysis</span>
                                    <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
};

export default Dashboard;