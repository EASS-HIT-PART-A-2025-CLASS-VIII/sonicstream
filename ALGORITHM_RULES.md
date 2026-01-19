# Recommendation Algorithm Rules

This document outlines the rules and logic used by the Music Discovery recommendation engine.

## Overview
The goal of the recommendation system is to help users discover *new* music that is sonically similar to tracks they already like, while actively encouraging exploration by excluding artists they are already familiar with (based on their input).

## Core Rules

1.  **Sonic Similarity**: Recommendations are primarily based on the audio characteristics of the tracks. We use 5-dimensional vectors (audio embeddings) representing features like acousticness, danceability, energy, instrumentalness, and valence.
    *   **Logic**: Calculate the cosine similarity (or inverted L2 distance) between the average embedding of the user's selected tracks and the embeddings of all other tracks in the database.
    *   **Scoring**: `Score = 1.0 / (1.0 + L2_Distance)`

2.  **Artist Exclusion (Discovery Mode)**: To forcefully promote discovery, the system **strictly excludes** tracks from any artist present in the user's input/liked tracks selection.
    *   **Logic**: If a user selects a track by "Adele", the result set will contain *zero* tracks by "Adele", ensuring they find similar sounding music from *different* artists.

3.  **Input Exclusion**: The specific tracks selected by the user are naturally excluded from the recommendations.

## Technical Implementation

### Steps
1.  **Input Analysis**:
    *   Calculate the **Average Embedding** vector of all input tracks components `(avg[1]...avg[5])`.
    *   Extract a list of **Liked Artists** from the input tracks.

2.  **Candidate Selection Query**:
    *   Select tracks from the database.
    *   **Filter 1**: `track_id` is NOT in Input Track IDs.
    *   **Filter 2**: `artist` is NOT loosely matched (ILIKE) against any of the Liked Artists.
    *   **Ordering**: Order by `Score` (Audio Similarity) descending.
    *   **Limit**: Return the top N results (default 12).

### Reasoning Labels
The system assigns a reason label to each recommendation to explain why it was chosen:
*   **"Perfect Match"**: Usage of `Score > 0.8`. Indicates extremely high sonic similarity.
*   **"Sonic Match"**: Default label for other recommendations based on vector distance.

## Future Improvements
*   **Genre Filtering**: Allow users to filter recommendations by specific genres.
*   **Popularity Weighting**: optionally allow mixing in popularity to find "hidden gems" vs "popular hits".
