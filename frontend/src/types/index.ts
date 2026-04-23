export interface Topic {
    id: number;
    topic: string;
    category: string;
    layer_1_gist: string;
    layer_2_pattern: string;
    layer_3_questions: string[];
}

export interface SprintDay {
    topic: string;
    focus: string;
    layers: number[];
}

export interface SprintPlan {
    metadata: {
        days_allocated: number;
        total_topics: number;
        intensity: string;
    };
    schedule: Record<string, SprintDay[]>;
}