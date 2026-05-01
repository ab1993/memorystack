import { Topic, SprintPlan } from '../types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Helper to grab the token from the browser's memory
const getAuthHeader = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const api = {

    // ==========================================
    // NEW: AUTHENTICATION
    // ==========================================
    signup: async (email: string, password: string) => {
        const response = await fetch(`${BASE_URL}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    login: async (email: string, password: string) => {
        // FastAPI OAuth2 strictly requires Form Data (URL Encoded), NOT JSON!
        const formData = new URLSearchParams();
        formData.append('username', email); // It expects 'username', so we pass the email here
        formData.append('password', password);

        const response = await fetch(`${BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString()
        });
        if (!response.ok) throw new Error("Invalid email or password");
        return response.json();
    },

    // Get all existing topics
    getTopics: async () => {
        const response = await fetch(`${BASE_URL}/topics`, {
            method: 'GET',
            headers: {
                ...getAuthHeader()
            }
        });

        // If the token is missing or expired, we can handle it
        if (response.status === 401) {
            console.error("Unauthorized: Please log in again");
            // Optional: You can redirect to /login here if you want
            throw new Error("Unauthorized");
        }

        if (!response.ok) throw new Error("Failed to fetch topics");
        return response.json();
    },

    // Trigger AI to learn a new topic
    generateTopic: async (name: string): Promise<Topic> => {
        const res = await fetch(`${BASE_URL}/topics/generate/${name}`, {
            method: 'POST',
            headers: {
                ...getAuthHeader()
            }
        });
        if (!res.ok) throw new Error("Unauthorized or Failed to generate");
        return res.json();
    },

    getUserStatus: async () => {
        const response = await fetch(`${BASE_URL}/user/status`, {
            method: 'GET',
            headers: {
                ...getAuthHeader()
            }
        });
        if (!response.ok) return null;
        return response.json();
    },

    // Create the Sprint logic plan
    generateSprint: async (date: string, topics: string[]): Promise<SprintPlan> => {
        const res = await fetch(`${BASE_URL}/generate-sprint`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeader()},
            body: JSON.stringify({ interview_date: date, selected_topics: topics }),
        });
        if (!res.ok) throw new Error("Failed to generate sprint");
        return res.json();
    },

    // Submit the FSRS review
    submitReview: async (id: number, rating: number): Promise<{ next_review_days: number }> => {
        const res = await fetch(`${BASE_URL}/review/${id}?rating=${rating}`, {
            method: 'POST',
            headers: {
                ...getAuthHeader()
            }
        });
        if (!res.ok) throw new Error("Review submission failed");
        return res.json();
    }
};