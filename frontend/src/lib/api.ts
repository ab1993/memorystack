import { Topic, SprintPlan } from '../types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const api = {
    // Get all existing topics
    getTopics: async (): Promise<Topic[]> => {
        const res = await fetch(`${BASE_URL}/topics`);
        if (!res.ok) throw new Error("Failed to fetch topics");
        return res.json();
    },

    // Trigger AI to learn a new topic
    generateTopic: async (name: string): Promise<Topic> => {
        const res = await fetch(`${BASE_URL}/topics/generate/${name}`, {
            method: 'POST',
        });
        if (!res.ok) throw new Error("AI generation failed");
        return res.json();
    },

    // Create the Sprint logic plan
    generateSprint: async (date: string, topics: string[]): Promise<SprintPlan> => {
        const res = await fetch(`${BASE_URL}/generate-sprint`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ interview_date: date, selected_topics: topics }),
        });
        if (!res.ok) throw new Error("Failed to generate sprint");
        return res.json();
    },

    // Submit the FSRS review
    submitReview: async (id: number, rating: number): Promise<{ next_review_days: number }> => {
        const res = await fetch(`${BASE_URL}/review/${id}?rating=${rating}`, {
            method: 'POST',
        });
        if (!res.ok) throw new Error("Review submission failed");
        return res.json();
    }
};