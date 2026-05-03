/*
 * Copyright (c) 2026 Abhishek Sharma. All rights reserved.
 * This code is part of the MemoryStack project.
 * Unauthorized copying or distribution of this file via any medium is strictly prohibited.
 * Proprietary and confidential.
 */

import "./globals.css"; // MUST be here
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
        <body className={inter.className}>{children}</body>
        </html>
    );
}