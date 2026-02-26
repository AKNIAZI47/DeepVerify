# Implementation Plan: UI Improvements and Chatbot Restoration

## Overview

This plan implements UI improvements and chatbot restoration for the VeriGlow application. The implementation relocates the News Analyzer component from the home page to the dashboard, adds a logo and "DeepVerify Assistant" link to the navbar, re-enables the chat router with Ollama-only integration (no Gemini fallback), and verifies the statistics endpoint accuracy.

## Tasks

- [x] 1. Create Logo component
  - Create `frontend/src/components/Logo.tsx` with SVG implementation
  - Design: magnifying glass + detective hat + checkmark (32x32px)
  - Make clickable with onClick handler support
  - Use currentColor for stroke to inherit text color
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7_

- [x] 2. Update Navbar component
  - [x] 2.1 Import and integrate Logo component
    - Import Logo component in `frontend/src/components/Navbar.tsx`
    - Add Logo before "DeepVerify" text in nav-brand section
    - Add flex layout styling for logo + text alignment
    - _Requirements: 6.1, 6.6_
  
  - [x] 2.2 Add "DeepVerify Assistant" navigation link
    - Add link to /chat route in navigation links section
    - Position between "Signup" and "Dashboard" links
    - Change text from "AI Assistant" to "DeepVerify Assistant"
    - Display for both authenticated and unauthenticated users
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. Relocate News Analyzer from Home to Dashboard
  - [x] 3.1 Remove News Analyzer from index.tsx
    - Remove SearchBar component and related imports
    - Remove statistics display section
    - Remove results rendering (AuthMeter, SourceCards, HTML explanation)
    - Remove state variables: input, html, verdict, prob, sources, loading, language
    - Remove handleAnalyze function and API calls
    - Keep only hero section with title, subtitle, and navigation
    - _Requirements: 1.1, 1.2_
  
  - [x] 3.2 Add News Analyzer to dashboard.tsx
    - Import SearchBar, AuthMeter, SourceCards components
    - Add state variables for analysis: input, html, verdict, prob, sources, loading, language
    - Implement handleAnalyze function with API call to /api/v1/analyze
    - Add statistics display section (Users, Analyses, Real, Fake, Uncertain, Accuracy)
    - Add results rendering section below statistics
    - Position News Analyzer above the history list
    - _Requirements: 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 4. Re-enable chat router in backend
  - [x] 4.1 Uncomment chat router in main.py
    - Uncomment `from chat import router as chat_router` import
    - Uncomment `app.include_router(chat_router)` registration
    - Verify rate limit config for /api/v1/chat endpoint exists
    - _Requirements: 3.1, 3.2_
  
  - [x] 4.2 Remove Gemini fallback from chat.py
    - Remove all Gemini API imports and configuration
    - Remove fallback logic in chat endpoint
    - Keep only Ollama integration (http://localhost:11434, llama3.2)
    - Return clear error message if Ollama is unavailable: "Ollama service is not available. Please ensure Ollama is running on localhost:11434"
    - Update health endpoint to report Ollama-only status
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 5. Update chat interface branding
  - Modify `frontend/src/pages/chat.tsx` to use "DeepVerify Assistant" instead of "AI Assistant"
  - Update welcome message and page title
  - Update any references in the chat UI
  - _Requirements: 2.1, 4.1_

- [x] 6. Verify statistics endpoint accuracy
  - Review `backend/stats.py` to confirm it queries User_Collection directly
  - Review `backend/auth.py` signup endpoint to confirm single document insertion
  - Verify no duplicate user creation logic exists
  - Add logging if needed to track user creation
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 7. Checkpoint - Test all changes
  - Verify home page displays only hero section
  - Verify dashboard displays News Analyzer with full functionality
  - Verify navbar displays logo and "DeepVerify Assistant" link
  - Verify chat page loads and displays correct branding
  - Verify /api/v1/chat endpoint is accessible
  - Test Ollama integration (requires Ollama running)
  - Verify error message when Ollama is unavailable
  - Verify statistics display correct counts
  - Ensure all tests pass, ask the user if questions arise

## Notes

- All tasks reference specific requirements for traceability
- The chat router requires Ollama to be running on localhost:11434 with llama3.2 model
- No Gemini fallback - users must have Ollama running
- Statistics endpoint likely already correct, verification task confirms implementation
- Logo uses SVG for scalability and theme compatibility
- News Analyzer maintains all existing functionality when relocated
