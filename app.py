import streamlit as st
import json
import os
from google import genai
from google.genai import types

# --- STAGE 1: APP CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="CareerNexus AI | Smart Pathfinding",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 700; color: #1E293B; }
    .card {
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        background-color: #FFFFFF;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- STAGE 2: INITIALIZE AI CLIENT & CAPTURE SESSION ---
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

# Build a persistent configuration utility in the sidebar early
with st.sidebar:
    st.markdown("### 👋 Workspace Setup")
    if not os.environ.get("GEMINI_API_KEY"):
        st.markdown("#### 🔑 AI Authentication")
        user_key = st.text_input("Enter GEMINI_API_KEY", type="password", value=st.session_state.gemini_api_key)
        if user_key != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = user_key
            st.rerun()

# Determine active key source
api_key = os.environ.get("GEMINI_API_KEY") or st.session_state.gemini_api_key

client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        client = None

# --- STAGE 3: SESSION STATE MANAGEMENT & USER DB ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# In-memory user registration ledger
if "user_database" not in st.session_state:
    st.session_state.user_database = {
        "student_demo": {
            "password": "password123",
            "profile": {
                "degree": "B.Tech (Computer Science)",
                "skills": ["Python", "SQL"],
                "hobbies": "Building Discord bots",
                "responses": ["Building/coding software", "The Builder (Executing production code/designs)"]
            }
        }
    }

# --- STAGE 4: ADVANCED AUTHENTICATION PORTAL (With Account Creation) ---
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("<p style='text-align:center; font-size:3rem;'>🎯</p>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>CareerNexus AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Bridging the gap between graduation and employment.</p>", unsafe_allow_html=True)
        st.write("---")
        
        # Split options between signing in and registering a new user
        auth_mode = st.tabs(["🔒 Sign In", "📝 Create Account"])
        
        # --- SUB-VIEW 1: SIGN IN FLOW ---
        with auth_mode[0]:
            with st.form("login_form"):
                login_user = st.text_input("Username / Email", placeholder="e.g., student_demo")
                login_pass = st.text_input("Password", type="password", placeholder="••••••••")
                
                if st.form_submit_button("Sign In"):
                    if login_user in st.session_state.user_database:
                        if st.session_state.user_database[login_user]["password"] == login_pass:
                            st.session_state.authenticated = True
                            st.session_state.current_user = login_user
                            st.session_state.user_profile = st.session_state.user_database[login_user]["profile"]
                            st.success("Successfully logged in!")
                            st.rerun()
                        else:
                            st.error("Incorrect password. Please try again.")
                    else:
                        st.error("Username not found. Please click 'Create Account' to sign up.")
                        
        # --- SUB-VIEW 2: SIGN UP FLOW ---
        with auth_mode[1]:
            with st.form("signup_form"):
                new_user = st.text_input("Choose a Username", placeholder="e.g., don_jose")
                new_pass = st.text_input("Create a Password", type="password", placeholder="Minimum 6 characters")
                confirm_pass = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                
                if st.form_submit_button("Register Account"):
                    if not new_user.strip() or len(new_pass) < 6:
                        st.error("Username cannot be blank, and password must be at least 6 characters.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match!")
                    elif new_user in st.session_state.user_database:
                        st.error("This username is already taken. Try another one!")
                    else:
                        # Write the credentials to our data dictionary
                        st.session_state.user_database[new_user] = {
                            "password": new_pass,
                            "profile": None
                        }
                        # Set active authentication states
                        st.session_state.authenticated = True
                        st.session_state.current_user = new_user
                        st.session_state.user_profile = None  # Redirects straight to questionnaire
                        st.success("Account created successfully!")
                        st.rerun()
    st.stop()

# --- STAGE 5: AI BACKEND ENGINES ---
def generate_ai_job_matches(profile_data):
    if not client:
        return {"error": "API Client not configured. Please paste your key into the sidebar."}

    prompt = f"""
    You are an advanced corporate career strategist and psychometric placement engine.
    Analyze this student's profile:
    - Degree: {profile_data['degree']}
    - Current Skills: {', '.join(profile_data['skills'])}
    - Hobbies/Passions: {profile_data['hobbies']}
    - Survey Answers: {', '.join(profile_data['responses'])}

    Suggest exactly 2 highly customized career roles that perfectly match this user. 
    You must respond ONLY with a valid JSON object matching this structure exactly:
    {{
        "matches": [
            {{
                "title": "Exact Job Title",
                "domain": "Industry Domain",
                "match_reason": "Brief explanation of why their skills and hobbies fit this exact role.",
                "min_skills_met": ["Skill From User List They Have", "Another Skill They Have"],
                "advanced_skills_needed": ["Skill 1 to learn", "Skill 2 to learn", "Skill 3 to learn"]
            }}
        ]
    }}
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Failed to generate AI matches: {str(e)}"}

def generate_ai_roadmap(target_job, profile_data):
    if not client:
        return {"error": "API Client not configured."}

    prompt = f"""
    You are an expert career pathfinder. The student's current profile is:
    - Degree: {profile_data['degree']}
    - Current Skills: {', '.join(profile_data['skills'])}
    
    They want to become a: "{target_job}"
    
    Generate a highly actionable 3-phase roadmap personalized to bridge their current gaps to reach this dream job.
    You must respond ONLY with a valid JSON object matching this structure exactly:
    {{
        "roadmap_steps": [
            {{"title": "Phase 1: Title", "desc": "Actionable milestone description targeting their missing gaps."}},
            {{"title": "Phase 2: Title", "desc": "Actionable milestone description."}},
            {{"title": "Phase 3: Title", "desc": "Actionable milestone description."}}
        ],
        "learning_modules": ["Specific Course or Certification 1", "Specific Course 2"],
        "upcoming_gateways": ["Relevant Industry Entrance Exam or Target Internship Type 1", "Gateway 2"]
    }}
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Failed to generate AI roadmap: {str(e)}"}


# --- STAGE 6: ONBOARDING DIAGNOSTIC QUESTIONNAIRE ---
if st.session_state.user_profile is None:
    st.markdown("## 📋 Student Diagnostic Profile")
    st.info("Your answers will be analyzed in real-time by our AI alignment model to construct your career path.")
    
    if not api_key:
        st.warning("⚠️ Heads up! Please enter your GEMINI_API_KEY in the left sidebar configuration panel so the matching system can run.")

    with st.form("onboarding_form"):
        c1, c2 = st.columns(2)
        with c1:
            degree = st.selectbox("Current Academic Stream / Degree", ["B.Tech (Computer Science)", "B.Com", "BBA", "B.Sc Design", "Other"])
            skills = st.multiselect("Select your current skills", ["Python", "SQL", "Statistics", "Figma", "Excel", "Public Speaking", "Agile"])
        with c2:
            hobbies = st.text_input("What do you actively spend time on outside classes?", placeholder="e.g., building Discord bots, painting, trading stocks")
        
        st.write("---")
        st.markdown("### 🔍 Psychometric Interest Mapping")
        q1 = st.selectbox("What type of technical tasks feel most rewarding to you?", ["Building/coding software", "Designing visuals/layouts", "Analyzing data/numbers", "Managing teams/events"])
        q2 = st.selectbox("In high-pressure group environments, where do you sit naturally?", ["The Architect (Planning structures)", "The Builder (Executing production code/designs)", "The Manager (Keeping people organized)"])
        
        if st.form_submit_button("Complete Diagnosis & Unlock AI Engine"):
            profile_payload = {
                "degree": degree,
                "skills": skills,
                "hobbies": hobbies,
                "responses": [q1, q2]
            }
            # Save into the session cache
            st.session_state.user_profile = profile_payload
            
            # Save permanently back into user history database entry
            st.session_state.user_database[st.session_state.current_user]["profile"] = profile_payload
            st.rerun()
    st.stop()


# --- STAGE 7: MAIN WORKSPACE INTERFACE ---
profile = st.session_state.user_profile

with st.sidebar:
    st.markdown(f"**Track:** {profile['degree']}")
    st.markdown("#### 🛠️ Your Current Skills")
    for s in profile['skills']:
        st.markdown(f"• `{s}`")
    st.write("---")
    if st.button("Reset / Log Out"):
        st.session_state.authenticated = False
        st.session_state.user_profile = None
        st.rerun()

st.markdown("<h1 style='margin-bottom:0;'>CareerNexus AI Workspace</h1>", unsafe_allow_html=True)
tab_job, tab_path = st.tabs(["🔍 FIND JOB (AI Skill Matcher)", "🚀 FIND PATH (AI Roadmap Builder)"])

# ==========================================
# 🔍 ENGINE VIEW 1: FIND JOB (AI Powered)
# ==========================================
with tab_job:
    st.markdown("## AI Skill-to-Role Matching Engine")
    st.caption("The AI model dynamically scans your background and generates customized target roles.")
    
    if not api_key:
        st.error("⚠️ Please configure your `GEMINI_API_KEY` in the sidebar to enable active AI matching.")
    else:
        if st.button("✨ Run AI Career Analysis", key="run_analysis"):
            with st.spinner("AI is analyzing your profile vectors..."):
                results = generate_ai_job_matches(profile)
                
                if "error" in results:
                    st.error(results["error"])
                else:
                    for job in results.get("matches", []):
                        with st.container():
                            st.markdown(f"""
                            <div class='card'>
                                <span style='background-color:#E0F2FE; color:#0369A1; padding:0.25rem 0.6rem; border-radius:4px; font-size:0.8rem; font-weight:bold;'>{job.get('domain', 'General')}</span>
                                <h3 style='margin-top:0.5rem;'>{job.get('title')}</h3>
                                <p style='color:#475569; font-size:0.95rem;'><b>AI Fit Analysis:</b> {job.get('match_reason')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown("**Core Requirements Met:**")
                                for skill in job.get("min_skills_met", []):
                                    st.markdown(f"✅ <span style='color:green;'>{skill}</span>", unsafe_allow_html=True)
                                    
                            with c2:
                                st.markdown("<div style='background-color:#F8FAFC; padding:1rem; border-radius:6px; border-left:4px solid #2563EB;'>", unsafe_allow_html=True)
                                st.markdown("⚡ **Advanced Track Skills to Acquire:**")
                                for adv in job.get("advanced_skills_needed", []):
                                    st.markdown(f"- `{adv}`")
                                st.markdown("</div>", unsafe_allow_html=True)
                            st.write("---")

# ==========================================
# 🚀 ENGINE VIEW 2: FIND PATH (AI Powered)
# ==========================================
with tab_path:
    st.markdown("## AI Vision-Driven Pathway Builder")
    st.caption("Tell the AI your exact dream job, and it will build a step-by-step master plan to help you achieve it.")
    
    dream_job = st.text_input("Enter your absolute target dream career:", placeholder="e.g., Quantum Computing Software Developer, Senior Fintech Product Manager")
    
    if dream_job:
        if not api_key:
            st.error("⚠️ Please configure your `GEMINI_API_KEY` in the sidebar to build a trajectory path.")
        else:
            if st.button("🔮 Generate My Custom AI Roadmap"):
                with st.spinner(f"Constructing strategic pathway to become a {dream_job}..."):
                    roadmap_res = generate_ai_roadmap(dream_job, profile)
                    
                    if "error" in roadmap_res:
                        st.error(roadmap_res["error"])
                    else:
                        st.markdown(f"### 🗺️ Custom Strategic Pathway to: *{dream_job}*")
                        
                        for i, step in enumerate(roadmap_res.get("roadmap_steps", []), 1):
                            st.markdown(f"""
                            <div style='background-color:#FFFFFF; padding:1.2rem; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:1rem; border-left:5px solid #10B981;'>
                                <h4 style='margin:0; color:#059669;'>{step.get('title', f'Phase {i}')}</h4>
                                <p style='margin:0.5rem 0 0 0; color:#475569;'>{step.get('desc')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        col_m1, col_m2 = st.columns(2)
                        with col_m1:
                            st.markdown("<div style='background-color:#FFFBEB; padding:1rem; border-radius:6px; border:1px solid #FDE68A; height:100%;'>", unsafe_allow_html=True)
                            st.markdown("<h5 style='margin:0; color:#B45309;'>📚 Suggested Learning Resources</h5>", unsafe_allow_html=True)
                            for item in roadmap_res.get("learning_modules", []):
                                st.markdown(f"- {item}")
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                        with col_m2:
                            st.markdown("<div style='background-color:#EFF6FF; padding:1rem; border-radius:6px; border:1px solid #BFDBFE; height:100%;'>", unsafe_allow_html=True)
                            st.markdown("<h5 style='margin:0; color:#1E40AF;'>🎯 Action Gateways & Exams</h5>", unsafe_allow_html=True)
                            for item in roadmap_res.get("upcoming_gateways", []):
                                st.markdown(f"- {item}")
                            st.markdown("</div>", unsafe_allow_html=True)