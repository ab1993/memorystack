"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api"; // Adjust path if your api.ts is elsewhere
import { BrainCircuit } from "lucide-react";

export default function AuthPage() {
    const router = useRouter();
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            if (isLogin) {
                const data = await api.login(email, password);
                localStorage.setItem("access_token", data.access_token);
                router.push("/");
            } else {
                await api.signup(email, password);
                const data = await api.login(email, password);
                localStorage.setItem("access_token", data.access_token);
                router.push("/");
            }
        } catch (err: any) {
            setError(err.message || "Something went wrong.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">

            {/* --- NEW LOGO HEADER --- */}
            <div className="flex items-center gap-3 mb-8">
                <div className="p-3 bg-blue-600 rounded-xl shadow-lg shadow-blue-600/20">
                    <BrainCircuit className="text-white" size={32} />
                </div>
                <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">
                    MemoryStack
                </h1>
            </div>

            <div className="max-w-md w-full p-8 bg-white rounded-2xl shadow-xl border border-gray-100">
                <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
                    {isLogin ? "Welcome Back" : "Create Your Account"}
                </h2>

                {error && <p className="text-red-500 text-sm mb-4 text-center bg-red-50 p-2 rounded">{error}</p>}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Email</label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black outline-none transition-all"
                            placeholder="you@example.com"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Password</label>
                        <input
                            type="password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black outline-none transition-all"
                            placeholder="••••••••"
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 text-white font-bold p-3 rounded-lg hover:bg-blue-700 transition-all active:scale-[0.98]"
                    >
                        {loading ? "Processing..." : (isLogin ? "Log In" : "Sign Up")}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-gray-600">
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <button
                        onClick={() => setIsLogin(!isLogin)}
                        className="text-blue-600 font-bold hover:underline"
                    >
                        {isLogin ? "Sign Up" : "Log In"}
                    </button>
                </p>
            </div>

            {/* --- NEW COPYRIGHT FOOTER --- */}
            <footer className="mt-12 text-sm text-gray-400">
                &copy; {new Date().getFullYear()} MemoryStack. All rights reserved.
            </footer>
        </div>
    );
}