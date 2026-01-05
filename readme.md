# Music Discovery App 🎵

## Overview
This project is a sophisticated **Song Suggestion Engine** designed to recommend music based on a user's favorite albums. It utilizes a Kaggle dataset to analyze recommendations and presents them in a premium, aesthetically pleasing web interface.

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/EASS-HIT-PART-A-2025-CLASS-VIII/music-discovery.git
   cd music-discovery
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Setup Dataset:**
   - Download the music dataset from Kaggle.
   - Place the CSV file in the `public/` directory and rename it to `dataset.csv`.

4. **Run the development server:**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## 🛠️ Technology Stack
- **Framework**: [Next.js 14](https://nextjs.org/) (App Router)
- **Styling**: Vanilla CSS / CSS Modules (focused on high-end, dynamic aesthetics)
- **Data Parsing**: PapaParse (for CSV handling)
- **Animations**: Framer Motion

## 📂 Project Structure
- `/src/app`: Application routes and pages.
- `/src/components`: Reusable UI components (AlbumSelector, SuggestionList).
- `/src/utils`: Helper functions and recommendation logic (`recommendationEngine.ts`).
- `/public`: Static assets and dataset.

## 🤝 Contribution
1. Create a feature branch (`git checkout -b feature/amazing-feature`).
2. Commit your changes.
3. Push to the branch.
4. Open a Pull Request.

## 📝 License
[MIT](https://choosealicense.com/licenses/mit/)
