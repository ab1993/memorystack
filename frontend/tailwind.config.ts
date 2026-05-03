/*
 * Copyright (c) 2026 Abhishek Sharma. All rights reserved.
 * This code is part of the MemoryStack project.
 * Unauthorized copying or distribution of this file via any medium is strictly prohibited.
 * Proprietary and confidential.
 */

import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/**/*.{js,ts,jsx,tsx,mdx}", // This covers everything in src
    ],
    theme: {
        extend: {},
    },
    plugins: [],
};
export default config;