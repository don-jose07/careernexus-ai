[version1.5 .md](https://github.com/user-attachments/files/28441171/version1.5.md)
# CareerNexus AI | Codebase & Version Control Documentation (v1.5)

CareerNexus AI is an interactive, AI-driven corporate career strategist and pathfinding web application. It is designed to assist students and professionals in mapping their academic background, skills, and interests to ideal career roles, and constructing actionable career roadmaps to bridge skill gaps.

This documentation serves as the official reference report for version control, detailing the software architecture, technical stack, user flows, state management, and the changelog from **v1.0 to v1.5**.

---

## 🛠️ Technology Stack & Dependencies

The application is built on top of a streamlined, modern Python web stack designed for rapid development and clean component rendering:

*   **Frontend & Application Framework**: [Streamlit](https://streamlit.io/) (v1.58.0+)
    *   Used for reactive, single-page web rendering, component rendering, form handling, and tabbed workspaces.
*   **LLM Client Library**: [Google GenAI SDK](https://github.com/googleapis/google-genai) (v2.7.0+)
    *   Used to interface with the Gemini models (`gemini-2.5-flash`) for real-time career alignment, classification, and structured JSON parsing.
*   **Core Logic & Utilities**:
    *   `json` for parsing structured JSON output from Gemini models.
    *   `os` for retrieving environment-level API configuration keys.

### Dependency Specification (`requirements.txt`)
```text
streamlit
google-genai
```

---

## 🏗️ Architecture & Component Design

The application operates as a linear multi-stage user flow driven by Streamlit's session state. The script execution is structured into **seven sequential stages**:

```mermaid
graph TD
    A[Start: app.py Run] --> B[Stage 1: Config & Global Custom CSS]
    B --> C[Stage 2: Setup Sidebar & Init AI Client]
    C --> D[Stage 3: Session State Init & User DB Ledger]
    D --> E{Stage 4: Authenticated?}
    E -- No --> F[Auth Portal: Sign In / Create Account] --> G[st.stop]
    E -- Yes --> H{Profile Exists in DB?}
    H -- No --> I[Stage 6: Onboarding Questionnaire] --> J[st.stop]
    H -- Yes --> K[Stage 7: Main Workspace]
    K --> L[Tab 1: Career Role Matcher]
    K --> M[Tab 2: Strategic Pathway Builder]
```

### 1. Global Setup & Theming (Stage 1)
Sets up the browser title, layout constraints, and injects custom vanilla CSS.
*   **Fonts**: Inter (Sans-Serif)
*   **Aesthetic Style**: Premium modern card system, sleek status/badge indicators, and color-coded information callouts.

### 2. Client Initialization & API Authentication (Stage 2)
Authenticates connections to the Gemini API. Supports two authentication flows:
1.  **Environment Configuration**: Directly binds to the `GEMINI_API_KEY` system environment variable.
2.  **Runtime Sidebar Configuration**: For deployments without access to shell environment configurations, users can input their API Key directly in a password-masked field located in the sidebar. This key is stored in Streamlit's `st.session_state` and persists across workspace reruns.

### 3. Session State Schema (Stage 3)
Tracks the user's active session and profiling details across page loads:
*   `st.session_state.authenticated` *(bool)*: Controls entry into the workspace.
*   `st.session_state.user_profile` *(dict | None)*: Stores the active user's diagnostic profile data.
*   `st.session_state.current_user` *(str | None)*: Identifier for the active session.
*   `st.session_state.gemini_api_key` *(str)*: Fallback Gemini API authentication token.
*   `st.session_state.user_database` *(dict)*: Multi-user database ledger holding credentials and diagnostic profiles.

### 4. Advanced Authentication Portal (Stage 4)
Provides a tabbed authentication gateway to restrict access to authorized sessions:
*   **Sign In**: Verifies entered credentials against `st.session_state.user_database`. Logs in existing users, automatically loads their stored profile, and redirects them to the workspace.
*   **Create Account**: Registers new users in the database ledger. Requires a username and password validation (minimum 6 characters), confirms matching passwords, and handles collision detection. Successfully registered users are immediately authenticated and sent to complete their onboarding profile.

### 5. Onboarding Diagnostics (Stage 6)
Collects structured diagnostic vectors from the user via standard input components:
*   **Degree / Academic Stream** (`st.selectbox`)
*   **Skills List** (`st.multiselect`)
*   **Out-of-class Hobbies** (`st.text_input`)
*   **Psychometric Interest Mapping** (`st.selectbox` for task rewarding and group dynamics placement)
*   *Output Behavior*: On completion, the profile is saved to both `st.session_state.user_profile` and persists in the user's registry database ledger (`st.session_state.user_database[user]["profile"]`).

### 6. AI Execution Engines (Stage 5 & Stage 7)
Coordinates prompt engineering schemas and model calls. All prompts require **structured JSON responses** enforced by `response_mime_type="application/json"` parameters in the client.

#### A. Skill-to-Role Matcher
*   **Prompt Architecture**: Instructs the model to act as a corporate career strategist and psychometric engine. Processes the student's onboarding diagnostics, matching them to exactly two target career paths.
*   **JSON Schema Output**:
    ```json
    {
        "matches": [
            {
                "title": "Exact Job Title",
                "domain": "Industry Domain",
                "match_reason": "Explanation of skill/hobby fit",
                "min_skills_met": ["Skill A", "Skill B"],
                "advanced_skills_needed": ["Future Skill 1", "Future Skill 2"]
            }
        ]
    }
    ```

#### B. Pathway Builder
*   **Prompt Architecture**: Models a customized trajectory toward a user-entered dream career, creating a personalized 3-phase roadmap matching their current academic status.
*   **JSON Schema Output**:
    ```json
    {
        "roadmap_steps": [
            {"title": "Phase 1: Title", "desc": "Phase details and gaps targeted"},
            {"title": "Phase 2: Title", "desc": "Phase details"},
            {"title": "Phase 3: Title", "desc": "Phase details"}
        ],
        "learning_modules": ["Course/Cert 1", "Course/Cert 2"],
        "upcoming_gateways": ["Entrance Exam/Internship 1", "Gateway 2"]
    }
    ```

---

## 📈 Version Control Changelog (v1.0 to v1.5)

The codebase has undergone significant structural hardening and user experience refinements:

| Feature/Fix | Description | Version Introduced | Files Modified |
| :--- | :--- | :---: | :--- |
| **Dependency Refactoring** | Cleaned up invalid dependencies (`plain text` typo) from the installation specification. | v1.1 | [requirements.txt](file:///c:/Users/donjo/OneDrive/Desktop/app1/requirements.txt) |
| **Workspace Setup Panel** | Added a persistent `👋 Workspace Setup` config widget in the sidebar early in the execution stack. | v1.2 | [app.py](file:///c:/Users/donjo/OneDrive/Desktop/app1/app.py) |
| **Dynamic API Initialization** | Modified client setup to bind to either the environment key or the sidebar-configured key at runtime. | v1.2 | [app.py](file:///c:/Users/donjo/OneDrive/Desktop/app1/app.py) |
| **Bare Execution Support** | Ensured the script handles import tests and direct command executions safely without crashing on profile extraction. | v1.3 | [app.py](file:///c:/Users/donjo/OneDrive/Desktop/app1/app.py) |
| **Git Setup & Configuration** | Initialized repository tracking and created exclusion patterns for virtual environments and Python cache assets. | v1.4 | [git init](file:///c:/Users/donjo/OneDrive/Desktop/app1/.git), [.gitignore](file:///c:/Users/donjo/OneDrive/Desktop/app1/.gitignore) |
| **Advanced Authentication Portal** | Replaced the single dev login form with a dual-tab "Sign In / Create Account" portal. | v1.5 | [app.py](file:///c:/Users/donjo/OneDrive/Desktop/app1/app.py) |
| **Persistent User Ledger** | Added in-memory user registry dictionary storage in session state, including automatic profile caching on logins. | v1.5 | [app.py](file:///c:/Users/donjo/OneDrive/Desktop/app1/app.py) |
| **Logout Lifecycle Handling** | Changed logic from resetting the session to a cleaner "Reset / Log Out" flow targeting correct authentication parameters. | v1.5 | [app.py](file:///c:/Users/donjo/OneDrive/Desktop/app1/app.py) |
| **Interactive UX Upgrades** | Injected login sub-header banner and localized warning badges for missing API keys directly within forms. | v1.5 | [app.py](file:///c:/Users/donjo/OneDrive/Desktop/app1/app.py) |
