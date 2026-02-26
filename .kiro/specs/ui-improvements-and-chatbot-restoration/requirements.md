# Requirements Document

## Introduction

This document specifies requirements for UI improvements and chatbot restoration in the VeriGlow fake news detection application. The feature includes relocating the news analyzer component from the home page to the dashboard, restoring the AI chatbot functionality with Ollama integration, fixing a signup count bug in statistics, and adding a logo to the navigation bar.

## Glossary

- **Home_Page**: The landing page (index.tsx) that serves as the entry point for all users
- **Dashboard_Page**: The authenticated user page (dashboard.tsx) that displays analysis history and statistics
- **News_Analyzer**: The text input component with analysis functionality, statistics display, and results visualization
- **AI_Chatbot**: The conversational assistant feature that integrates with Ollama for natural language interactions
- **Navbar**: The navigation bar component displayed across all pages
- **Stats_Endpoint**: The backend API endpoint (/api/v1/stats) that returns application statistics
- **Ollama_Service**: The local LLM service running on http://localhost:11434 with llama3.2 model
- **Signup_Endpoint**: The backend API endpoint (/api/v1/auth/signup) that handles user registration
- **User_Collection**: The MongoDB collection storing registered user documents
- **Chat_Router**: The FastAPI router (chat.py) that handles chatbot API requests
- **Logo_Component**: The visual brand identifier displayed in the Navbar before the "DeepVerify" text

## Requirements

### Requirement 1: Relocate News Analyzer to Dashboard

**User Story:** As a user, I want the news analyzer to be on the dashboard page, so that the home page is cleaner and the analyzer is available where I manage my analysis history.

#### Acceptance Criteria

1. THE Home_Page SHALL display only the hero section with title, subtitle, and navigation links
2. THE Home_Page SHALL NOT display the News_Analyzer component or statistics
3. THE Dashboard_Page SHALL display the News_Analyzer component with full functionality
4. THE Dashboard_Page SHALL display statistics including Users, Analyses, Real, Fake, Uncertain, and Accuracy metrics
5. WHEN a user submits text for analysis on the Dashboard_Page, THE News_Analyzer SHALL display results including verdict, confidence scores, HTML explanation, and sources
6. THE Dashboard_Page SHALL display the News_Analyzer above the analysis history list
7. THE News_Analyzer SHALL maintain all existing functionality including language detection, authentication meter, and source cards

### Requirement 2: Restore AI Chatbot Navigation

**User Story:** As a user, I want to access the AI chatbot from the navigation bar, so that I can ask questions about news verification and get AI-powered assistance.

#### Acceptance Criteria

1. THE Navbar SHALL display an "AI Assistant" navigation link
2. THE "AI Assistant" link SHALL be positioned between the "Signup" and "Dashboard" links in the navigation order
3. WHEN a user clicks the "AI Assistant" link, THE Navbar SHALL navigate to the /chat route
4. THE Navbar SHALL display the "AI Assistant" link to both authenticated and unauthenticated users

### Requirement 3: Integrate Ollama Chatbot Backend

**User Story:** As a user, I want to interact with an AI chatbot powered by Ollama, so that I can get intelligent responses about news verification.

#### Acceptance Criteria

1. THE Chat_Router SHALL be enabled in the main.py application
2. THE Chat_Router SHALL register the /api/v1/chat endpoint
3. WHEN a user sends a message to /api/v1/chat, THE Chat_Router SHALL forward the request to the Ollama_Service at http://localhost:11434
4. THE Chat_Router SHALL use the llama3.2 model for generating responses
5. WHEN the Ollama_Service returns a response, THE Chat_Router SHALL return the response to the client
6. IF the Ollama_Service is unavailable, THEN THE Chat_Router SHALL return an error message indicating the service is offline
7. THE Chat_Router SHALL include the /api/v1/chat/health endpoint for service health checks

### Requirement 4: Create Chat Page Interface

**User Story:** As a user, I want a chat interface page, so that I can have conversations with the AI assistant.

#### Acceptance Criteria

1. THE application SHALL provide a /chat route that renders a chat interface page
2. THE chat interface page SHALL display a message input field
3. THE chat interface page SHALL display a conversation history showing user messages and AI responses
4. WHEN a user submits a message, THE chat interface SHALL send the message to the /api/v1/chat endpoint
5. WHEN a response is received, THE chat interface SHALL append the AI response to the conversation history
6. THE chat interface SHALL display a loading indicator while waiting for AI responses
7. THE chat interface SHALL display error messages when the chatbot service is unavailable

### Requirement 5: Fix Signup Count Statistics

**User Story:** As an administrator, I want the user count to reflect actual registered users, so that statistics accurately represent application usage.

#### Acceptance Criteria

1. THE Stats_Endpoint SHALL count documents in the User_Collection to determine total_users
2. THE Stats_Endpoint SHALL NOT count signup button clicks or failed signup attempts
3. WHEN the Signup_Endpoint successfully creates a user, THE User_Collection SHALL contain exactly one new document
4. THE Stats_Endpoint SHALL return the count of documents in the User_Collection as total_users
5. WHEN multiple signup attempts occur for the same email, THE User_Collection SHALL contain only one document for that email
6. THE total_users statistic SHALL increment only when a new user document is successfully inserted into the User_Collection

### Requirement 6: Add Logo to Navigation Bar

**User Story:** As a user, I want to see a logo in the navigation bar, so that I can visually identify the VeriGlow brand.

#### Acceptance Criteria

1. THE Navbar SHALL display a Logo_Component before the "DeepVerify" text
2. THE Logo_Component SHALL feature a magnifying glass symbol combined with a detective or black hat figure
3. THE Logo_Component SHALL be implemented as an SVG icon or image component
4. THE Logo_Component SHALL have a maximum height of 32 pixels to maintain navbar proportions
5. WHEN a user clicks the Logo_Component, THE Navbar SHALL navigate to the home page
6. THE Logo_Component SHALL be visible on all pages where the Navbar is displayed
7. THE Logo_Component SHALL maintain visual clarity at the specified size
