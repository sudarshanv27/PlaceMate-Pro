import streamlit as st
import pandas as pd
import sqlite3
import os
import json
from datetime import datetime
import base64
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import hashlib

# Optional imports with fallbacks
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

# =========================
# PAGE CONFIGURATION
# =========================
st.set_page_config(
    page_title="PlaceMate Pro - Placement Prediction System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CONSTANTS & CONFIGURATION
# =========================
DB_PATH = "data/placemate.db"
CONFIG_PATH = "data/config.json"
ADMIN_USERNAME = "sudarshan"
ADMIN_PASSWORD = "sudarshan27@"

# Create directories
os.makedirs("data", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Branch Configuration
BRANCH_CONFIG = {
    "Computer Science (CSE)": {
        "coding_required": True,
        "technical_skills": ["Python", "Java", "C++", "JavaScript", "SQL", "Data Structures", "Algorithms", 
                            "Machine Learning", "Web Development", "Django", "React", "AWS", "Docker"],
        "tools": ["VS Code", "Git", "Docker", "AWS", "MySQL", "MongoDB", "Jupyter", "PyCharm"],
        "companies": ["Google", "Microsoft", "Amazon", "Meta", "Adobe", "Oracle", "TCS", "Infosys", 
                     "Accenture", "IBM", "Salesforce", "Netflix"],
        "career_paths": ["Software Engineer", "Data Scientist", "ML Engineer", "DevOps Engineer", 
                        "Cloud Architect", "Full Stack Developer", "Security Analyst"],
        "avg_salary": "8-25 LPA",
        "exam_required": ["GATE", "AMCAT", "eLitmus"]
    },
    "Electronics (ECE)": {
        "coding_required": True,
        "technical_skills": ["Embedded Systems", "VLSI", "MATLAB", "Verilog", "IoT", "Digital Signal Processing",
                            "PCB Design", "ARM Cortex", "FPGA"],
        "tools": ["Cadence", "Xilinx", "Arduino", "Raspberry Pi", "Oscilloscope", "Keil", "Proteus"],
        "companies": ["Intel", "Qualcomm", "Texas Instruments", "Samsung", "NVIDIA", "AMD", "Broadcom", 
                     "Ericsson", "Siemens"],
        "career_paths": ["VLSI Engineer", "Embedded Engineer", "Hardware Engineer", "RF Engineer", 
                        "Signal Processing Engineer", "IoT Specialist"],
        "avg_salary": "6-18 LPA",
        "exam_required": ["GATE EC", "ISE", "VLSI Exam"]
    },
    "Mechanical Engineering": {
        "coding_required": False,
        "technical_skills": ["AutoCAD", "SolidWorks", "CATIA", "ANSYS", "Thermodynamics", "Fluid Mechanics",
                            "Manufacturing Processes", "Finite Element Analysis", "CFD"],
        "tools": ["SolidWorks", "CATIA", "ANSYS", "AutoCAD", "MATLAB", "3D Printer", "CNC Machines"],
        "companies": ["TATA Motors", "Mahindra", "Bosch", "Siemens", "L&T", "General Electric", 
                     "John Deere", "Cummins", "BHEL"],
        "career_paths": ["Design Engineer", "Production Engineer", "Quality Engineer", "R&D Engineer", 
                        "Project Manager", "Thermal Engineer"],
        "avg_salary": "5-12 LPA",
        "exam_required": ["GATE ME", "IES"]
    },
    "Civil Engineering": {
        "coding_required": False,
        "technical_skills": ["AutoCAD Civil", "STAAD Pro", "ETABS", "Primavera", "Construction Management",
                            "Structural Analysis", "Surveying", "Revit", "SAP2000"],
        "tools": ["AutoCAD Civil 3D", "STAAD Pro", "ETABS", "MS Project", "Revit", "Primavera P6"],
        "companies": ["L&T", "Shapoorji Pallonji", "GMR", "DLF", "Jacobs", "AECOM", "Afcons", 
                     "Reliance Infrastructure", "Gammon"],
        "career_paths": ["Structural Engineer", "Site Engineer", "Planning Engineer", "Quantity Surveyor", 
                        "Project Coordinator", "Transportation Engineer"],
        "avg_salary": "4-10 LPA",
        "exam_required": ["GATE CE", "IES", "SSC JE"]
    },
    "Electrical Engineering (EEE)": {
        "coding_required": False,
        "technical_skills": ["Power Systems", "Control Systems", "Electrical Machines", "PLC", "SCADA",
                            "Renewable Energy", "Power Electronics", "Switchgear"],
        "tools": ["MATLAB Simulink", "ETAP", "LabVIEW", "AutoCAD Electrical", "PowerWorld", "PSCAD"],
        "companies": ["Siemens", "ABB", "Schneider Electric", "BHEL", "NTPC", "Power Grid Corporation", 
                     "TATA Power", "Adani Power", "L&T Electrical"],
        "career_paths": ["Power Systems Engineer", "Control Engineer", "Electrical Design Engineer", 
                        "Field Service Engineer", "Renewable Energy Engineer"],
        "avg_salary": "5-14 LPA",
        "exam_required": ["GATE EE", "IES", "UPSC ESE"]
    }
}

COMPANY_TYPES = ["MNC", "Startup", "Government", "Public Sector", "PSU", "Core Company"]
CERTIFICATION_LEVELS = ["Beginner", "Intermediate", "Advanced", "Professional", "Expert"]

# Scoring weights
SCORING_WEIGHTS = {
    "cgpa": 15,
    "technical_skills": 12,
    "tools": 8,
    "projects": 10,
    "internships": 12,
    "certifications": 8,
    "communication": 10,
    "aptitude": 10,
    "problem_solving": 10,
    "coding": 15,
    "internship_type": 8,
    "certification_level": 7
}

# =========================
# DATABASE SETUP
# =========================
def init_database():
    """Initialize database with optimized schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        student_name TEXT NOT NULL,
        branch TEXT NOT NULL,
        cgpa REAL CHECK(cgpa >= 0 AND cgpa <= 10),
        coding_skill INTEGER CHECK(coding_skill >= 0 AND coding_skill <= 10),
        communication_skill INTEGER CHECK(communication_skill >= 0 AND communication_skill <= 10),
        aptitude_skill INTEGER CHECK(aptitude_skill >= 0 AND aptitude_skill <= 10),
        problem_solving INTEGER CHECK(problem_solving >= 0 AND problem_solving <= 10),
        projects_count INTEGER DEFAULT 0,
        internship_count INTEGER DEFAULT 0,
        internship_type TEXT,
        certifications_count INTEGER DEFAULT 0,
        certification_level TEXT,
        technical_skills TEXT,
        tools_known TEXT,
        email TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Predictions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        student_name TEXT,
        branch TEXT,
        status TEXT,
        probability REAL,
        readiness_score INTEGER,
        company_suggestions TEXT,
        career_insights TEXT,
        strengths TEXT,
        improvements TEXT,
        predicted_salary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)
    
    # Feedback table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        feedback_text TEXT,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

# =========================
# HELPER FUNCTIONS
# =========================
def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_readiness_score(student):
    """Enhanced readiness score calculation"""
    branch = student.get('branch', 'Computer Science (CSE)')
    if branch not in BRANCH_CONFIG:
        branch = 'Computer Science (CSE)'
    
    config = BRANCH_CONFIG[branch]
    
    # Parse skills
    tech_skills = [s.strip() for s in str(student.get('technical_skills', '')).split(',') if s.strip()]
    tools = [t.strip() for t in str(student.get('tools_known', '')).split(',') if t.strip()]
    
    # Calculate individual scores
    score_components = {}
    
    # CGPA score (max 15)
    cgpa = student.get('cgpa', 0)
    score_components['CGPA'] = min(cgpa * 1.5, 15)
    
    # Communication score (max 10)
    score_components['Communication'] = student.get('communication_skill', 0)
    
    # Aptitude score (max 10)
    score_components['Aptitude'] = student.get('aptitude_skill', 0)
    
    # Problem solving score (max 10)
    score_components['Problem Solving'] = student.get('problem_solving', 0)
    
    # Projects score (max 10)
    projects = min(student.get('projects_count', 0), 5)
    score_components['Projects'] = projects * 2
    
    # Internships score (max 12)
    internships = min(student.get('internship_count', 0), 3)
    internship_score = internships * 4
    # Internship type bonus
    internship_type = student.get('internship_type', 'None')
    if internship_type == 'MNC':
        internship_score += 4
    elif internship_type == 'Startup':
        internship_score += 2
    elif internship_type == 'PSU':
        internship_score += 3
    score_components['Internships'] = min(internship_score, 12)
    
    # Certifications score (max 8)
    certs = min(student.get('certifications_count', 0), 4)
    cert_score = certs * 1.5
    # Certification level bonus
    cert_level = student.get('certification_level', 'None')
    level_bonus = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2, 'Professional': 3, 'Expert': 4}.get(cert_level, 0)
    cert_score += level_bonus
    score_components['Certifications'] = min(cert_score, 8)
    
    # Technical skills score (max 12)
    skill_count = min(len(tech_skills), 6)
    score_components['Technical Skills'] = skill_count * 2
    
    # Tools score (max 8)
    tool_count = min(len(tools), 4)
    score_components['Tools'] = tool_count * 2
    
    # Coding score (max 15) - only for tech branches
    if config['coding_required']:
        score_components['Coding'] = student.get('coding_skill', 0) * 1.5
    
    # Calculate total
    total_score = sum(score_components.values())
    readiness = min(int(total_score), 100)
    
    return readiness, score_components

def predict_salary(readiness, branch):
    """Predict expected salary based on readiness score"""
    config = BRANCH_CONFIG.get(branch, BRANCH_CONFIG['Computer Science (CSE)'])
    salary_range = config['avg_salary']
    
    if readiness >= 85:
        multiplier = 1.3
    elif readiness >= 75:
        multiplier = 1.1
    elif readiness >= 65:
        multiplier = 0.9
    elif readiness >= 50:
        multiplier = 0.7
    else:
        multiplier = 0.5
    
    return salary_range, multiplier

def generate_detailed_insights(student, readiness, score_components):
    """Generate detailed personalized insights"""
    strengths = []
    improvements = []
    recommendations = []
    
    # CGPA analysis
    cgpa = student.get('cgpa', 0)
    if cgpa >= 8.5:
        strengths.append("🎯 Excellent Academic Record - Top percentile")
    elif cgpa >= 7.5:
        strengths.append("📚 Good Academic Performance")
    elif cgpa >= 6.5:
        improvements.append("📈 Aim for CGPA above 7.5 for better opportunities")
    else:
        improvements.append("⚠️ Critical: Improve CGPA to meet minimum eligibility criteria")
    
    # Skills analysis
    tech_skills = len([s for s in str(student.get('technical_skills', '')).split(',') if s.strip()])
    if tech_skills >= 5:
        strengths.append(f"💻 Strong Technical Foundation ({tech_skills} skills)")
    elif tech_skills >= 3:
        strengths.append(f"🔧 Good Technical Skills ({tech_skills} skills)")
    else:
        improvements.append("📚 Learn more in-demand technical skills")
    
    # Projects analysis
    projects = student.get('projects_count', 0)
    if projects >= 3:
        strengths.append(f"🏗️ Strong Project Portfolio ({projects} projects)")
        recommendations.append("🎯 Showcase your best projects on GitHub/Portfolio")
    elif projects >= 1:
        strengths.append(f"📁 Has Project Experience")
        recommendations.append("🚀 Build more real-time/complex projects")
    else:
        improvements.append("⚠️ No projects found - Build at least 2-3 quality projects")
    
    # Internship analysis
    internships = student.get('internship_count', 0)
    internship_type = student.get('internship_type', 'None')
    if internships >= 2:
        strengths.append(f"💼 Excellent Industry Exposure ({internships} internships)")
    elif internships == 1:
        if internship_type != 'None':
            strengths.append(f"🎯 Good internship at {internship_type}")
        recommendations.append("📊 Consider one more internship for diverse experience")
    else:
        improvements.append("⚠️ No internship experience - Apply for internships immediately")
    
    # Communication skills
    comm = student.get('communication_skill', 0)
    if comm >= 8:
        strengths.append("🗣️ Excellent Communication Skills")
    elif comm >= 6:
        strengths.append("💬 Good Communication Skills")
    else:
        improvements.append("🎙️ Improve communication - Practice group discussions and presentations")
    
    # Branch-specific recommendations
    branch = student.get('branch', 'Computer Science (CSE)')
    config = BRANCH_CONFIG.get(branch, BRANCH_CONFIG['Computer Science (CSE)'])
    
    if readiness >= 80:
        recommendations.append(f"🏆 Target Top Companies: {', '.join(config['companies'][:5])}")
        recommendations.append("💰 Expected Salary: Premium bracket")
    elif readiness >= 65:
        recommendations.append(f"🎯 Target Mid-tier Companies in {branch}")
        recommendations.append("📈 Focus on skill enhancement for better packages")
    else:
        recommendations.append("📚 Focus on fundamentals and skill development")
        recommendations.append("🎯 Start with service-based companies for initial experience")
    
    # Add preparation tips
    if config['coding_required']:
        recommendations.append("💻 Practice coding daily on LeetCode/HackerRank")
        recommendations.append("📖 Prepare Data Structures & Algorithms thoroughly")
    
    recommendations.append("📝 Create a professional resume highlighting your strengths")
    recommendations.append("🎤 Practice mock interviews with peers")
    
    return strengths, improvements, recommendations

# =========================
# UI COMPONENTS
# =========================
def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    /* Subheader styling */
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin: 1rem 0;
        padding-left: 1rem;
        border-left: 4px solid #4F46E5;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
        border: 1px solid #e0e0e0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Status cards */
    .status-placed {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    .status-not-placed {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    /* Chat styling */
    .chat-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px;
        border-radius: 15px 15px 5px 15px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .chat-bot {
        background: #F3F4F6;
        padding: 12px;
        border-radius: 15px 15px 15px 5px;
        margin: 10px 0;
        max-width: 80%;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Info boxes */
    .info-box {
        background: #EFF6FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3B82F6;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    """Create sidebar navigation"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1 style="color: white; font-size: 1.8rem;">🎓 PlaceMate Pro</h1>
            <p style="color: rgba(255,255,255,0.8);">AI-Powered Placement System</p>
            <hr style="background: rgba(255,255,255,0.3);">
        </div>
        """, unsafe_allow_html=True)
        
        menu = st.radio(
            "Navigation Menu",
            ["🏠 Dashboard", "📝 Register Student", "🎯 Predict Placement", 
             "📊 Analytics", "💬 Chat Assistant", "👨‍🏫 Faculty Portal", "ℹ️ About"],
            label_visibility="hidden"
        )
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem; font-size: 0.8rem;">
            <p>© 2024 PlaceMate Pro</p>
            <p>Version 3.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        return menu

# =========================
# DASHBOARD
# =========================
def show_dashboard():
    st.markdown('<h1 class="main-header">📊 Placement Dashboard</h1>', unsafe_allow_html=True)
    
    students_df = get_students()
    predictions_df = get_predictions()
    
    if students_df.empty:
        st.info("📭 No data available. Please register students first.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(students_df)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);">
            <h3 style="color: white;">👥 Total Students</h3>
            <h1 style="font-size: 2.5rem; color: white;">{total}</h1>
            <p style="color: #BFDBFE;">Registered in system</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if not predictions_df.empty and 'status' in predictions_df.columns:
            placed = len(predictions_df[predictions_df['status'].str.contains('PLACED', na=False)])
        else:
            placed = 0
        placement_rate = (placed/total*100) if total > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #064E3B 0%, #10B981 100%);">
            <h3 style="color: white;">✅ Placement Rate</h3>
            <h1 style="font-size: 2.5rem; color: white;">{placement_rate:.1f}%</h1>
            <p style="color: #A7F3D0;">{placed} students placed</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_cgpa = students_df['cgpa'].mean()
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #92400E 0%, #F59E0B 100%);">
            <h3 style="color: white;">📊 Average CGPA</h3>
            <h1 style="font-size: 2.5rem; color: white;">{avg_cgpa:.2f}</h1>
            <p style="color: #FDE68A;">Across all branches</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        top_branch = students_df['branch'].mode().iloc[0] if not students_df['branch'].mode().empty else "N/A"
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #7E1F86 0%, #A855F7 100%);">
            <h3 style="color: white;">🏆 Top Branch</h3>
            <h1 style="font-size: 1.5rem; color: white;">{top_branch}</h1>
            <p style="color: #E9D5FF;">Most registrations</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Branch Distribution")
        branch_counts = students_df['branch'].value_counts()
        fig = px.pie(values=branch_counts.values, names=branch_counts.index, 
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=400, plot_bgcolor='blue', paper_bgcolor='blue', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 CGPA Distribution")
        fig = px.histogram(students_df, x='cgpa', nbins=20,
                          color_discrete_sequence=['#4F46E5'])
        fig.update_layout(
                            height=400, 
                            plot_bgcolor='blue', 
                            paper_bgcolor='blue',
                            font=dict(color='white')
                        )
        st.plotly_chart(fig, use_container_width=True)

    
    # Recent activity
    st.markdown("---")
    st.subheader("🔄 Recent Activity")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📋 Latest Registrations**")
        recent_students = students_df.head(5)
        for _, student in recent_students.iterrows():
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 0.75rem; margin: 0.5rem 0; border-radius: 10px; border-left: 4px solid #60A5FA; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong style="color: white;">👨‍🎓 {student['student_name']}</strong><br>
                <small style="color: #BFDBFE;">📚 {student['branch']} | CGPA: {student['cgpa']:.2f}</small>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("**🎯 Recent Predictions**")
        if not predictions_df.empty:
            recent_pred = predictions_df.head(5)
            for _, pred in recent_pred.iterrows():
                status_icon = "✅" if "PLACED" in str(pred['status']) else "❌"
                status_color = "#10B981" if "PLACED" in str(pred['status']) else "#EF4444"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 0.75rem; margin: 0.5rem 0; border-radius: 10px; border-left: 4px solid {status_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <strong style="color: white;">{status_icon} {pred['student_name']}</strong><br>
                    <small style="color: #BFDBFE;">Status: {pred['status']} | Probability: {pred['probability']:.0%}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 0.75rem; margin: 0.5rem 0; border-radius: 10px; text-align: center;">
                <p style="color: #BFDBFE;">No predictions yet. Generate predictions for students.</p>
            </div>
            """, unsafe_allow_html=True)

# =========================
# STUDENT REGISTRATION
# =========================
def show_registration():
    st.markdown('<h1 class="main-header">📝 Student Registration</h1>', unsafe_allow_html=True)
    
    with st.form("registration_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input("Student ID*", help="Unique identifier")
            name = st.text_input("Full Name*")
            email = st.text_input("Email ID")
            phone = st.text_input("Phone Number")
            branch = st.selectbox("Branch*", list(BRANCH_CONFIG.keys()))
            cgpa = st.number_input("CGPA*", 0.0, 10.0, 7.0, 0.1)
        
        with col2:
            comm_skill = st.slider("Communication Skill", 1, 10, 5)
            aptitude = st.slider("Aptitude Skill", 1, 10, 5)
            problem_solving = st.slider("Problem Solving", 1, 10, 5)
            projects = st.number_input("Projects Completed", 0, 20, 1)
            internships = st.number_input("Internships Done", 0, 10, 0)
        
        # Branch-specific field
        if BRANCH_CONFIG[branch]['coding_required']:
            coding = st.slider("Coding Skill", 1, 10, 5)
        else:
            coding = 0
        
        internship_type = st.selectbox("Internship Type", ["None"] + COMPANY_TYPES)
        certifications = st.number_input("Certifications", 0, 20, 0)
        cert_level = st.selectbox("Certification Level", ["None"] + CERTIFICATION_LEVELS)
        
        tech_skills = st.text_area("Technical Skills (comma-separated)", 
                                   placeholder="Python, Java, SQL, Machine Learning")
        tools = st.text_area("Tools Known (comma-separated)",
                            placeholder="Git, VS Code, Docker, AWS")
        
        submitted = st.form_submit_button("🚀 Register Student", width='stretch')
        
        if submitted:
            if not student_id or not name:
                st.error("⚠️ Please fill required fields: Student ID and Name")
            else:
                student = {
                    'student_id': student_id,
                    'student_name': name,
                    'branch': branch,
                    'cgpa': cgpa,
                    'coding_skill': coding,
                    'communication_skill': comm_skill,
                    'aptitude_skill': aptitude,
                    'problem_solving': problem_solving,
                    'projects_count': projects,
                    'internship_count': internships,
                    'internship_type': internship_type,
                    'certifications_count': certifications,
                    'certification_level': cert_level,
                    'technical_skills': tech_skills,
                    'tools_known': tools,
                    'email': email,
                    'phone': phone
                }
                
                if save_student(student):
                    st.success(f"✅ Student {name} registered successfully!")
                    st.balloons()
                    
                    # Show registration summary
                    with st.expander("📋 Registration Summary"):
                        st.json(student)
    
    # Show existing students
    st.markdown("---")
    st.subheader("📋 Registered Students")
    students_df = get_students()
    if not students_df.empty:
        st.dataframe(students_df[['student_id', 'student_name', 'branch', 'cgpa', 'created_at']], 
                    width='stretch')

# =========================
# PLACEMENT PREDICTION
# =========================
def show_prediction():
    st.markdown('<h1 class="main-header">🎯 Placement Prediction</h1>', unsafe_allow_html=True)
    
    students_df = get_students()
    
    if students_df.empty:
        st.warning("⚠️ No students found. Please register students first.")
        return
    
    # Student selection with search
    search = st.text_input("🔍 Search Student", placeholder="Type student name or ID...")
    filtered_df = students_df[
        students_df['student_name'].str.contains(search, case=False, na=False) |
        students_df['student_id'].str.contains(search, case=False, na=False)
    ] if search else students_df
    
    if filtered_df.empty:
        st.warning("No students found matching your search.")
        return
    
    selected = st.selectbox("Select Student", filtered_df['student_name'].tolist())
    
    if selected:
        student = filtered_df[filtered_df['student_name'] == selected].iloc[0].to_dict()
        
        # Student profile section
        with st.expander("📋 Student Profile", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Student ID", student['student_id'])
                st.metric("Name", student['student_name'])
            with col2:
                st.metric("Branch", student['branch'])
                st.metric("CGPA", f"{student['cgpa']:.2f}")
            with col3:
                st.metric("Projects", student['projects_count'])
                st.metric("Internships", student['internship_count'])
            with col4:
                st.metric("Certifications", student['certifications_count'])
                st.metric("Skills", len(str(student.get('technical_skills', '')).split(',')))
        
        # Generate prediction button
        if st.button("🔮 Generate Placement Prediction", type="primary", width='stretch'):
            with st.spinner("🤖 Analyzing student profile..."):
                # Calculate metrics
                readiness, score_components = calculate_readiness_score(student)
                probability = readiness / 100
                salary_range, salary_multiplier = predict_salary(readiness, student['branch'])
                strengths, improvements, recommendations = generate_detailed_insights(student, readiness, score_components)
                
                # Determine status
                if readiness >= 75:
                    status = "HIGHLY PLACED"
                    status_icon = "🎉"
                    status_color = "#10B981"
                elif readiness >= 60:
                    status = "PLACED"
                    status_icon = "✅"
                    status_color = "#3B82F6"
                else:
                    status = "NOT PLACED"
                    status_icon = "⚠️"
                    status_color = "#EF4444"
                
                # Save prediction
                companies = BRANCH_CONFIG[student['branch']]['companies'][:5]
                insights = " | ".join(recommendations[:3])
                save_prediction(student, status, probability, readiness, companies, insights)
                
                # Display results
                st.markdown("---")
                
                # Status card
                st.markdown(f"""
                <div style="background: {status_color}20; padding: 2rem; border-radius: 15px; text-align: center; margin: 1rem 0;">
                    <h1 style="color: {status_color}; font-size: 3rem;">{status_icon} {status}</h1>
                    <p style="font-size: 1.2rem;">Predicted Status</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Readiness and Probability
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                        <h3 style="color: white; margin: 0 0 1rem 0;">📊 Readiness Score</h3>
                        <h1 style="font-size: 3rem; color: white; margin: 0.5rem 0;">{readiness}/100</h1>
                        <div style="background: rgba(255,255,255,0.3); height: 10px; border-radius: 5px; margin-top: 1rem;">
                            <div style="background: linear-gradient(90deg, #60A5FA, #FFFFFF); width: {readiness}%; height: 100%; border-radius: 5px;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                        <h3 style="color: white; margin: 0 0 1rem 0;">💰 Placement Probability</h3>
                        <h1 style="font-size: 3rem; color: white; margin: 0.5rem 0;">{probability:.1%}</h1>
                        <div style="background: rgba(255,255,255,0.3); height: 10px; border-radius: 5px; margin-top: 1rem;">
                            <div style="background: linear-gradient(90deg, #60A5FA, #FFFFFF); width: {probability*100}%; height: 100%; border-radius: 5px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Score breakdown
                with st.expander("📈 Score Breakdown"):
                    for component, score in score_components.items():
                        st.progress(score / 15, text=f"{component}: {score:.1f}/15")
                
                # Recommended companies
                st.subheader("🏢 Recommended Companies")
                company_cols = st.columns(min(5, len(companies)))
                for i, company in enumerate(companies[:5]):
                    with company_cols[i]:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #60A5FA; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <h4 style="color: white; margin: 0 0 0.5rem 0;">🏢 {company}</h4>
                            <small style="color: #BFDBFE;">Top recruiter for {student['branch']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Salary expectation
                st.info(f"💰 **Expected Salary Range:** {salary_range}")
                
                # Strengths and Improvements
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### ✅ Strengths")
                    for s in strengths[:5]:
                        st.write(f"• {s}")
                
                with col2:
                    st.markdown("### ⚠️ Areas for Improvement")
                    for i in improvements[:5]:
                        st.write(f"• {i}")
                
                # Recommendations
                st.markdown("### 💡 Actionable Recommendations")
                for i, rec in enumerate(recommendations[:6], 1):
                    st.write(f"{i}. {rec}")
                
                # Download report
                if FPDF_AVAILABLE:
                    st.markdown("---")
                    st.subheader("📄 Download Your Report")
                    
                    with st.container():
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); 
                                    padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
                            <p style="color: white; margin: 0;">📋 Generate and download your complete placement report</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    try:
                        from fpdf import FPDF
                        import re
                        
                        # Function to clean Unicode characters
                        def clean_text(text):
                            """Remove emojis and special Unicode characters"""
                            if text is None:
                                return "N/A"
                            # Convert to string
                            text = str(text)
                            # Remove emojis and special characters
                            emoji_pattern = re.compile("["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags
                                u"\u2702-\u27B0"
                                u"\u24C2-\U0001F251"
                                u"\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff]"
                                "]+", flags=re.UNICODE)
                            text = emoji_pattern.sub(r'', text)
                            # Replace bullet points and other special chars
                            text = text.replace('•', '-')
                            text = text.replace('✅', '[PLACED]')
                            text = text.replace('❌', '[NOT PLACED]')
                            text = text.replace('🎯', '*')
                            text = text.replace('⚠️', '!')
                            text = text.replace('📊', '')
                            text = text.replace('💰', '')
                            text = text.replace('🏆', '')
                            text = text.replace('🎓', '')
                            # Remove any other non-ASCII characters
                            text = text.encode('ascii', 'ignore').decode('ascii')
                            return text.strip()
                        
                        class PDFReport(FPDF):
                            def header(self):
                                self.set_font('Arial', 'B', 15)
                                self.cell(0, 10, 'PlaceMate Pro - Placement Prediction Report', 0, 1, 'C')
                                self.set_font('Arial', 'I', 8)
                                self.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
                                self.ln(5)
                            
                            def footer(self):
                                self.set_y(-15)
                                self.set_font('Arial', 'I', 8)
                                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
                        
                        pdf = PDFReport()
                        pdf.add_page()
                        
                        # Student Information
                        pdf.set_font('Arial', 'B', 12)
                        pdf.set_fill_color(70, 70, 70)
                        pdf.cell(0, 10, 'Student Information', 0, 1, 'L', 1)
                        pdf.set_font('Arial', '', 10)
                        pdf.cell(40, 8, 'Student ID:', 0, 0)
                        pdf.cell(0, 8, clean_text(student.get('student_id', 'N/A')), 0, 1)
                        pdf.cell(40, 8, 'Name:', 0, 0)
                        pdf.cell(0, 8, clean_text(student.get('student_name', 'N/A')), 0, 1)
                        pdf.cell(40, 8, 'Branch:', 0, 0)
                        pdf.cell(0, 8, clean_text(student.get('branch', 'N/A')), 0, 1)
                        pdf.cell(40, 8, 'CGPA:', 0, 0)
                        pdf.cell(0, 8, str(student.get('cgpa', 'N/A')), 0, 1)
                        pdf.ln(5)
                        
                        # Skills & Qualifications
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, 'Skills & Qualifications', 0, 1, 'L', 1)
                        pdf.set_font('Arial', '', 10)
                        pdf.cell(45, 8, 'Technical Skills:', 0, 0)
                        pdf.cell(0, 8, clean_text(student.get('technical_skills', 'N/A')), 0, 1)
                        pdf.cell(45, 8, 'Tools Known:', 0, 0)
                        pdf.cell(0, 8, clean_text(student.get('tools_known', 'N/A')), 0, 1)
                        pdf.cell(45, 8, 'Projects:', 0, 0)
                        pdf.cell(0, 8, str(student.get('projects_count', 0)), 0, 1)
                        pdf.cell(45, 8, 'Internships:', 0, 0)
                        pdf.cell(0, 8, str(student.get('internship_count', 0)), 0, 1)
                        pdf.cell(45, 8, 'Certifications:', 0, 0)
                        pdf.cell(0, 8, str(student.get('certifications_count', 0)), 0, 1)
                        pdf.ln(5)
                        
                        # Prediction Results
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, 'Prediction Results', 0, 1, 'L', 1)
                        pdf.set_font('Arial', '', 10)
                        pdf.cell(50, 8, 'Status:', 0, 0)
                        pdf.cell(0, 8, clean_text(status), 0, 1)
                        pdf.cell(50, 8, 'Readiness Score:', 0, 0)
                        pdf.cell(0, 8, f'{readiness}/100', 0, 1)
                        pdf.cell(50, 8, 'Placement Probability:', 0, 0)
                        pdf.cell(0, 8, f'{probability:.1%}', 0, 1)
                        pdf.ln(5)
                        
                        # Recommended Companies
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, 'Recommended Companies', 0, 1, 'L', 1)
                        pdf.set_font('Arial', '', 10)
                        for i, company in enumerate(companies[:5], 1):
                            pdf.cell(10, 8, f'{i}.', 0, 0)
                            pdf.cell(0, 8, clean_text(company), 0, 1)
                        pdf.ln(5)
                        
                        # Career Insights (clean version without bullets)
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, 'Career Insights', 0, 1, 'L', 1)
                        pdf.set_font('Arial', '', 10)
                        insights_list = insights.split(' | ')
                        for insight in insights_list[:6]:
                            clean_insight = clean_text(insight)
                            if clean_insight:
                                pdf.multi_cell(0, 7, f'- {clean_insight}')
                        pdf.ln(5)
                        
                        # Recommendations
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, 'Recommendations', 0, 1, 'L', 1)
                        pdf.set_font('Arial', '', 10)
                        recommendations_list = [
                            "Focus on improving technical skills",
                            "Build more projects to strengthen portfolio",
                            "Practice aptitude and communication skills",
                            "Apply for internships to gain experience",
                            "Prepare for interviews with mock sessions"
                        ]
                        for i, rec in enumerate(recommendations_list[:5], 1):
                            pdf.multi_cell(0, 6, f'{i}. {rec}')
                        
                        # Generate PDF - FIXED ENCODING
                        pdf_output = pdf.output(dest='S')
                        
                        # Handle encoding properly
                        if isinstance(pdf_output, str):
                            # Try different encodings
                            try:
                                pdf_bytes = pdf_output.encode('latin-1')
                            except UnicodeEncodeError:
                                try:
                                    pdf_bytes = pdf_output.encode('utf-8')
                                except:
                                    pdf_bytes = pdf_output.encode('ascii', errors='ignore')
                        else:
                            pdf_bytes = pdf_output
                        
                        # Download button with better styling
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.download_button(
                                label="📥 DOWNLOAD PREDICTION REPORT (PDF)",
                                data=pdf_bytes,
                                file_name=f"Placement_Report_{student['student_id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                width='stretch',
                                type="primary"
                            )
                        
                        st.success("✅ Your report is ready! Click the button above to download.")
                        
                    except Exception as e:
                        st.error(f"PDF Generation Error: {str(e)}")
                        st.info("Please install fpdf: pip install fpdf")
                        
                        # Fallback: Offer HTML download as alternative
                        st.markdown("---")
                        st.subheader("📄 Alternative: Download as Text")
                        
                        # Create text version
                        text_report = f"""
PLACEMATE PRO - PLACEMENT PREDICTION REPORT
============================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STUDENT INFORMATION
------------------
Student ID: {student.get('student_id', 'N/A')}
Name: {student.get('student_name', 'N/A')}
Branch: {student.get('branch', 'N/A')}
CGPA: {student.get('cgpa', 'N/A')}

SKILLS & QUALIFICATIONS
-----------------------
Technical Skills: {student.get('technical_skills', 'N/A')}
Tools Known: {student.get('tools_known', 'N/A')}
Projects: {student.get('projects_count', 0)}
Internships: {student.get('internship_count', 0)}
Certifications: {student.get('certifications_count', 0)}

PREDICTION RESULTS
------------------
Status: {clean_text(status) if 'clean_text' in dir() else status}
Readiness Score: {readiness}/100
Placement Probability: {probability:.1%}

RECOMMENDED COMPANIES
---------------------
{chr(10).join([f'{i+1}. {company}' for i, company in enumerate(companies[:5])])}

CAREER INSIGHTS
---------------
{chr(10).join([f'- {insight}' for insight in insights.split(' | ')[:6]])}

RECOMMENDATIONS
---------------
1. Focus on improving technical skills
2. Build more projects to strengthen portfolio
3. Practice aptitude and communication skills
4. Apply for internships to gain experience
5. Prepare for interviews with mock sessions

============================================
This report is AI-generated based on your profile.
© 2024 PlaceMate Pro - All Rights Reserved
"""
                        
                        st.download_button(
                            label="📥 Download Report as Text File",
                            data=text_report,
                            file_name=f"Placement_Report_{student['student_id']}_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain",
                            width='stretch'
                        )

# =========================
# ANALYTICS PAGE
# =========================
def show_analytics():
    st.markdown('<h1 class="main-header">📊 Advanced Analytics</h1>', unsafe_allow_html=True)
    
    students_df = get_students()
    predictions_df = get_predictions()
    
    if students_df.empty:
        st.info("No data available for analytics")
        return
    
    # Branch performance comparison
    st.subheader("🏆 Branch-wise Performance")
    
    branch_stats = []
    for branch in BRANCH_CONFIG.keys():
        branch_students = students_df[students_df['branch'] == branch]
        if not branch_students.empty:
            branch_predictions = predictions_df[predictions_df['branch'] == branch] if not predictions_df.empty else pd.DataFrame()
            placed = len(branch_predictions[branch_predictions['status'].str.contains('PLACED', na=False)]) if not branch_predictions.empty else 0
            
            branch_stats.append({
                'Branch': branch,
                'Students': len(branch_students),
                'Avg CGPA': branch_students['cgpa'].mean(),
                'Placed': placed,
                'Placement Rate': (placed/len(branch_students)*100) if len(branch_students) > 0 else 0
            })
    
    stats_df = pd.DataFrame(branch_stats)
    st.dataframe(stats_df, width='stretch')
    
    # Skills analysis
    st.subheader("🔧 Most Common Technical Skills")
    all_skills = []
    for skills in students_df['technical_skills'].dropna():
        all_skills.extend([s.strip() for s in str(skills).split(',') if s.strip()])
    
    if all_skills:
        skill_counts = Counter(all_skills).most_common(10)
        skills_df = pd.DataFrame(skill_counts, columns=['Skill', 'Count'])
        fig = px.bar(skills_df, x='Count', y='Skill', orientation='h', title="Top 10 Skills")
        fig.update_layout(height=500)
        st.plotly_chart(fig, width='stretch')
    
    # CGPA distribution by branch
    st.subheader("📊 CGPA Distribution by Branch")
    fig = px.box(students_df, x='branch', y='cgpa', title="CGPA Distribution by Branch",
                color='branch', color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(height=500)
    st.plotly_chart(fig, width='stretch')
    
    # Placement trends
    if not predictions_df.empty and 'created_at' in predictions_df.columns:
        st.subheader("📈 Placement Trends Over Time")
        predictions_df['date'] = pd.to_datetime(predictions_df['created_at']).dt.date
        daily_trends = predictions_df.groupby('date').size().reset_index(name='count')
        fig = px.line(daily_trends, x='date', y='count', title="Daily Prediction Trends")
        st.plotly_chart(fig, width='stretch')

# =========================
# CHAT ASSISTANT
# =========================
class PlacementChatbot:
    def __init__(self):
        self.context = {}
        
    def get_response(self, question, student_data=None):
        q = question.lower()
        
        # Greetings
        if any(word in q for word in ['hi', 'hello', 'hey']):
            return "Hello! I'm your Placement Assistant. How can I help you with your placement preparation today?"
        
        # Placement process
        if 'placement process' in q or 'how to get placed' in q:
            return """📋 **Placement Process Overview:**
1. Registration & Resume Submission
2. Aptitude Test (Quantitative, Logical, Verbal)
3. Technical Interview (Domain-specific questions)
4. HR Interview (Soft skills, attitude)
5. Offer Letter

💡 **Tip:** Start preparing at least 6 months before placement season!"""
        
        # Resume tips
        if 'resume' in q or 'cv' in q:
            return """📄 **Resume Building Tips:**
✅ Keep it 1-2 pages maximum
✅ Use a clean, professional format
✅ Highlight projects and internships
✅ Quantify achievements (e.g., "Improved efficiency by 30%")
✅ Include relevant technical skills
✅ Add GitHub/Portfolio links

❌ Avoid: Spelling errors, irrelevant info, fancy designs"""
        
        # Interview prep
        if 'interview' in q:
            return """🎯 **Interview Preparation Guide:**
**Before Interview:**
- Research the company thoroughly
- Practice common questions
- Prepare your introduction (30-60 seconds)
- Review your projects

**During Interview:**
- Dress professionally
- Maintain eye contact
- Ask clarifying questions
- Show enthusiasm

**After Interview:**
- Send a thank-you email
- Note down questions asked for future prep"""
        
        # Technical skills
        if 'technical skill' in q or 'what to learn' in q:
            return """💻 **In-Demand Technical Skills by Branch:**

**CSE/IT:** Python, Java, SQL, Data Structures, ML/AI, Cloud (AWS/Azure), React, Node.js

**ECE:** Embedded C, VHDL, MATLAB, IoT, PCB Design, Verilog

**Mechanical:** AutoCAD, SolidWorks, ANSYS, CATIA, MATLAB

**Civil:** AutoCAD Civil, STAAD Pro, Revit, Primavera, ETABS

**Electrical:** MATLAB, PLC Programming, SCADA, ETAP, Power Systems"""
        
        # Salary expectations
        if 'salary' in q or 'package' in q:
            return """💰 **Average Salary Packages by Branch:**

**CSE:** 6-25 LPA (Top companies: 20-40 LPA)
**ECE:** 5-18 LPA
**Mechanical:** 4-12 LPA
**Civil:** 4-10 LPA
**Electrical:** 5-14 LPA

*Note: Salaries vary based on company, role, location, and your skills*
💡 Higher readiness score = Better salary packages!"""
        
        # CGPA importance
        if 'cgpa' in q or 'grade' in q:
            return """📚 **CGPA Importance:**
✅ Minimum requirement: Usually 6.0-6.5 CGPA
✅ Top companies: 7.5+ CGPA preferred
✅ PSUs/Govt jobs: Often 60% throughout academics

**What if CGPA is low?**
- Focus on strong technical skills
- Build impressive projects
- Get certifications
- Do internships
- Prepare well for aptitude tests"""
        
        # Default response
        return """I can help you with:
• Placement process and preparation
• Resume building tips
• Interview preparation
• Skills to learn for your branch
• Salary expectations
• CGPA requirements
• Company information

What specific information would you like to know?"""

def show_chatbot():
    st.markdown('<h1 class="main-header">💬 AI Placement Assistant</h1>', unsafe_allow_html=True)
    
    # Chatbot info
    st.info("🤖 **Your Personal Placement Guide** - Ask me anything about placements, interviews, resume, skills, or careers!")
    
    # Initialize chat history
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hello! I'm your Placement Assistant. How can I help you with your placement journey today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about placements..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        chatbot = PlacementChatbot()
        response = chatbot.get_response(prompt)
        
        # Add bot response
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hello! I'm your Placement Assistant. How can I help you with your placement journey today?"}
        ]
        st.rerun()
    
    # Quick questions
    st.markdown("---")
    st.markdown("### 📌 Quick Questions")
    quick_qs = ["What is the placement process?", "How to prepare for interviews?", "How to make a good resume?", "What skills are in demand?", "Expected salary packages?"]
    
    cols = st.columns(5)
    for i, q in enumerate(quick_qs):
        if cols[i].button(q, key=f"quick_{i}"):
            st.session_state.chat_messages.append({"role": "user", "content": q})
            chatbot = PlacementChatbot()
            response = chatbot.get_response(q)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()

# =========================
# FACULTY PORTAL
# =========================
def show_faculty_portal():
    st.markdown('<h1 class="main-header">👨‍🏫 Faculty Portal</h1>', unsafe_allow_html=True)
    
    if 'faculty_logged_in' not in st.session_state:
        st.session_state.faculty_logged_in = False
    
    if not st.session_state.faculty_logged_in:
        with st.form("faculty_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.faculty_logged_in = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    else:
        st.success("Welcome to Faculty Dashboard")
        
        students_df = get_students()
        predictions_df = get_predictions()
        
        tabs = st.tabs(["📊 Overview", "👥 All Students", "📈 Predictions", "📤 Export Data"])
        
        with tabs[0]:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Students", len(students_df))
            with col2:
                placed = len(predictions_df[predictions_df['status'].str.contains('PLACED', na=False)]) if not predictions_df.empty else 0
                st.metric("Total Placed", placed)
            with col3:
                rate = (placed/len(students_df)*100) if len(students_df) > 0 else 0
                st.metric("Placement Rate", f"{rate:.1f}%")
        
        with tabs[1]:
            if not students_df.empty:
                st.dataframe(students_df, width='stretch')
            else:
                st.info("No students found")
        
        with tabs[2]:
            if not predictions_df.empty:
                st.dataframe(predictions_df, width='stretch')
            else:
                st.info("No predictions found")
        
        with tabs[3]:
            if not students_df.empty:
                csv = students_df.to_csv(index=False)
                st.download_button("📥 Download Students Data (CSV)", csv, "students_data.csv", "text/csv")
            
            if not predictions_df.empty:
                csv = predictions_df.to_csv(index=False)
                st.download_button("📥 Download Predictions Data (CSV)", csv, "predictions_data.csv", "text/csv")
        
        if st.button("🚪 Logout", width='stretch'):
            st.session_state.faculty_logged_in = False
            st.rerun()

# =========================
# DATABASE OPERATIONS
# =========================
def get_students():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM students ORDER BY created_at DESC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def get_predictions():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM predictions ORDER BY created_at DESC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def save_student(student):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO students 
        (student_id, student_name, branch, cgpa, coding_skill, communication_skill, 
         aptitude_skill, problem_solving, projects_count, internship_count, 
         internship_type, certifications_count, certification_level, 
         technical_skills, tools_known, email, phone, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM students WHERE student_id=?), CURRENT_TIMESTAMP))
        """, (
            student['student_id'], student['student_name'], student['branch'], student['cgpa'],
            student.get('coding_skill', 0), student.get('communication_skill', 0),
            student.get('aptitude_skill', 0), student.get('problem_solving', 0),
            student.get('projects_count', 0), student.get('internship_count', 0),
            student.get('internship_type', 'None'), student.get('certifications_count', 0),
            student.get('certification_level', 'None'), student.get('technical_skills', ''),
            student.get('tools_known', ''), student.get('email', ''), student.get('phone', ''),
            student['student_id']
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def save_prediction(student, status, probability, readiness, companies, insights):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO predictions 
        (student_id, student_name, branch, status, probability, 
         readiness_score, company_suggestions, career_insights, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            student['student_id'], student['student_name'], student['branch'],
            status, probability, readiness, ", ".join(companies), insights
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Prediction save error: {e}")
        return False

def generate_prediction_pdf(student, readiness, probability, status, companies, insights, branch_info):
    if not FPDF_AVAILABLE:
        return None
    
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, "PlaceMate Pro - Placement Prediction Report", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "R")
        pdf.ln(10)
        
        # Student Info
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Student Information", 0, 1)
        pdf.set_font("Arial", "", 11)
        pdf.cell(40, 8, f"Name: {student.get('student_name', 'N/A')}", 0, 1)
        pdf.cell(40, 8, f"ID: {student.get('student_id', 'N/A')}", 0, 1)
        pdf.cell(40, 8, f"Branch: {student.get('branch', 'N/A')}", 0, 1)
        pdf.cell(40, 8, f"CGPA: {student.get('cgpa', 'N/A')}", 0, 1)
        pdf.ln(5)
        
        # Prediction Results
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Prediction Results", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"Status: {status}", 0, 1)
        pdf.cell(0, 8, f"Readiness Score: {readiness}/100", 0, 1)
        pdf.cell(0, 8, f"Placement Probability: {probability:.0%}", 0, 1)
        pdf.ln(5)
        
        # Companies
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Recommended Companies:", 0, 1)
        pdf.set_font("Arial", "", 10)
        for i, company in enumerate(companies[:5], 1):
            pdf.cell(10, 6, "", 0, 0)
            pdf.cell(0, 6, f"{i}. {company}", 0, 1)
        
        pdf.ln(5)
        
        # Insights
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Career Insights:", 0, 1)
        pdf.set_font("Arial", "", 10)
        insights_list = insights.split(' | ')
        for insight in insights_list[:5]:
            pdf.multi_cell(0, 6, f"• {insight}")
        
        return pdf.output(dest='S').encode('latin-1', errors='ignore')
        
    except Exception as e:
        return None

# =========================
# ABOUT PAGE
# =========================
def show_about():
    st.markdown('<h1 class="main-header">ℹ️ About PlaceMate Pro</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; text-align: center;">
            <h1 style="color: white; font-size: 3rem;">🎓</h1>
            <h2 style="color: white;">PlaceMate Pro</h2>
            <p style="color: white;">Version 3.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        ### 🚀 AI-Powered Placement Prediction System
        
        **PlaceMate Pro** is an intelligent placement preparation platform that helps students:
        - 📊 Assess their placement readiness
        - 🎯 Get personalized recommendations
        - 💼 Find suitable companies
        - 📈 Track their progress
        - 🤖 Get AI-powered guidance
        
        ### Key Features
        
        ✅ **Smart Prediction Algorithm** - ML-based readiness scoring
        ✅ **Branch-wise Analysis** - Tailored recommendations
        ✅ **Real-time Dashboard** - Interactive analytics
        ✅ **AI Chat Assistant** - 24/7 placement guidance
        ✅ **PDF Reports** - Downloadable predictions
        ✅ **Faculty Portal** - Admin analytics
        
        ### Technologies Used
        
        - **Frontend:** Streamlit
        - **Backend:** Python, SQLite
        - **Analytics:** Pandas, Plotly
        - **AI/ML:** Custom scoring algorithm
        - **Reports:** FPDF
        
        ### Contact
        
        For support or queries, contact your placement cell.
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <p>© 2026 Sudarshan | All Rights Reserved </p>
        <p>Made with ❤️ for placement preparation</p>
    </div>
    """, unsafe_allow_html=True)

# =========================
# MAIN APPLICATION
# =========================
def main():
    # Initialize database
    init_database()
    
    # Apply styling
    apply_custom_css()
    
    # Create sidebar
    menu = create_sidebar()
    
    # Page routing
    if menu == "🏠 Dashboard":
        show_dashboard()
    elif menu == "📝 Register Student":
        show_registration()
    elif menu == "🎯 Predict Placement":
        show_prediction()
    elif menu == "📊 Analytics":
        show_analytics()
    elif menu == "💬 Chat Assistant":
        show_chatbot()
    elif menu == "👨‍🏫 Faculty Portal":
        show_faculty_portal()
    elif menu == "ℹ️ About":
        show_about()

if __name__ == "__main__":
    main()