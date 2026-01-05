# SonicStream - Premium Music Discovery Frontend

## 🎵 Overview
This directory contains the features for the **SonicStream** music discovery platform. It is built with a focus on high-performance rendering, a premium dark-mode aesthetic, and fluid animations.

## 🛠️ Tech Stack
*   **Framework**: [Next.js 14](https://nextjs.org/) (App Router, TypeScript)
*   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
*   **Component Library**: [Shadcn/UI](https://ui.shadcn.com/) (Radix UI primitives)
*   **Animations**: [Framer Motion](https://www.framer.com/motion/)
*   **Icons**: [Lucide React](https://lucide.dev/)

## ✨ Key Features

### 1. Premium Design System
*   **Dark Mode Core**: The UI is built on a strict dark background (`#0a0a0a`) to make content pop.
*   **Neon Accents**: Uses a signature Neon Green (`#1ed760`) for primary actions and energetic highlights.
*   **Glassmorphism**: Navbar and cards utilize backdrop blurs (`backdrop-blur-md`) for a modern, layered feel.

### 2. Core Components
*   **`Navbar.tsx`**: A sticky, glass-effect navigation bar with a responsive layout and animated logo.
*   **`Hero.tsx`**: The landing page centerpiece, featuring:
    *   Animated entry sequences (fade-in, slide-up).
    *   Dynamic gradient text.
    *   Ambient background "blob" effects.
*   **`Features.tsx`**: A responsive grid layout displaying value propositions with hover-reactive cards.

### 3. Architecture
*   **`layout.tsx`**: Enforces the dark theme and font (Inter) globally.
*   **`globals.css`**: Defines CSS variables for Shadcn/UI and custom scrollbar styles for a polished feel.

## 🚀 Getting Started

### Prerequisites
*   Node.js v18+
*   npm

### Installation

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run the development server:**
    ```bash
    npm run dev
    ```

4.  **Open the app:**
    Visit [http://localhost:3000](http://localhost:3000) to see the application.

## 🤝 Contributing
*   **Components**: Place reusable UI elements in `src/components/ui`.
*   **Layouts**: Feature-specific layouts go in `src/components/layout`.
*   **Pages**: routing handles by `src/app`.
