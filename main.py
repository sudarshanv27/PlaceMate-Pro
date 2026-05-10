# ============================================
# PLACE MATE – STUDENT PLACEMENT SYSTEM (CLI)
# ============================================

import os
import pandas as pd
from datetime import datetime

# --------------------------------------------
# FILE PATHS
# --------------------------------------------
DATA_PATH = "data/registered_students.csv"
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

# --------------------------------------------
# CSV CHECK
# --------------------------------------------
COLUMNS = [
    "student_id", "student_name", "branch", "cgpa",
    "coding_skill", "communication_skill", "aptitude_skill",
    "problem_solving", "projects_count", "internship_count",
    "certification_count", "internship_company_level",
    "certification_company_level", "technical_skills", "tools_known",
    "selected_career", "readiness_score", "placement_status", "created_at"
]

if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_PATH, index=False)

df = pd.read_csv(DATA_PATH)

# Ensure all columns exist in existing CSV
for col in COLUMNS:
    if col not in df.columns:
        df[col] = None
df.to_csv(DATA_PATH, index=False)

# --------------------------------------------
# BRANCH CONFIG
# --------------------------------------------
BRANCH_SKILLS = {
    "CSE": ["Python", "Java", "C++", "SQL", "ML", "Data Analytics", "JavaScript", "React", "Django"],
    "ECE": ["Embedded C", "VHDL", "MATLAB", "Python", "Arduino", "PCB Design", "Verilog"],
    "MECHANICAL": ["AutoCAD", "SolidWorks", "ANSYS", "MATLAB", "CATIA", "Fusion 360"],
    "CIVIL": ["AutoCAD Civil 3D", "STAAD.Pro", "Revit", "ETABS", "MS Project", "Primavera"],
    "ELECTRICAL": ["MATLAB", "Proteus", "ETAP", "Power Systems", "PLC", "SCADA"],
    "OTHER": ["MS Office", "Communication", "Project Management", "Leadership"]
}

BRANCH_TOOLS = {
    "CSE": ["Git", "AWS", "Docker", "Linux", "Jupyter Notebook", "VS Code", "PyCharm"],
    "ECE": ["Oscilloscope", "Multimeter", "PCB Etching Tools", "Proteus", "Arduino IDE", "Keil"],
    "MECHANICAL": ["SolidWorks", "ANSYS", "MATLAB", "CATIA", "MS Excel", "3D Printer"],
    "CIVIL": ["AutoCAD", "STAAD.Pro", "MS Project", "Revit", "Surveying Tools", "Total Station"],
    "ELECTRICAL": ["MATLAB", "Simulink", "Proteus", "ETAP", "Multimeter", "Oscilloscope"],
    "OTHER": ["MS Office", "Google Workspace", "Trello", "Slack", "Zoom"]
}

BRANCH_COMPANIES = {
    "CSE": ["Google", "Microsoft", "Amazon", "TCS", "Infosys", "Accenture", "Wipro", "IBM"],
    "ECE": ["Qualcomm", "Intel", "Texas Instruments", "TCS", "Infosys", "Samsung", "NVIDIA"],
    "MECHANICAL": ["L&T", "Siemens", "TATA Motors", "Mahindra", "Bosch", "Ashok Leyland"],
    "CIVIL": ["L&T", "Reliance Infrastructure", "Shapoorji Pallonji", "Afcons", "Gammon", "GMR"],
    "ELECTRICAL": ["Siemens", "ABB", "BHEL", "GE Power", "TCS", "Schneider Electric"],
    "OTHER": ["Various MNCs", "Startups", "Government Sector", "Public Sector", "Consulting Firms"]
}

CAREER_BY_STRENGTH = {
    "Coding": ["Software Developer", "Data Scientist", "ML Engineer", "Backend Developer"],
    "Aptitude": ["Data Analyst", "Research Analyst", "Business Analyst", "Quant Analyst"],
    "Communication": ["HR", "Business Analyst", "Consultant", "Sales Manager", "Customer Success"],
    "Problem Solving": ["Product Manager", "Consultant", "Solutions Architect", "Technical Lead"],
    "Technical": ["Engineer", "Technician", "Technical Support", "Field Engineer"]
}

PLACEMENT_THRESHOLD = 65  # Minimum readiness score to be placed

# --------------------------------------------
# UTILITY FUNCTIONS
# --------------------------------------------
def validate_numeric_input(prompt, min_val=0, max_val=10, is_float=True):
    """Validate numeric input with range checking"""
    while True:
        try:
            if is_float:
                value = float(input(prompt))
            else:
                value = int(input(prompt))
            
            if min_val <= value <= max_val:
                return value
            else:
                print(f"❌ Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

def detect_strength(student, branch):
    """Detect student's strongest skill area"""
    if branch in ["CSE", "ECE"]:
        skills = {
            "Coding": student.get("coding_skill", 0),
            "Aptitude": student.get("aptitude_skill", 0),
            "Communication": student.get("communication_skill", 0),
            "Problem Solving": student.get("problem_solving", 0)
        }
    else:
        # Calculate technical score based on number of skills
        tech_skills_count = len(str(student.get("technical_skills", "")).split(",")) if student.get("technical_skills") else 0
        skills = {
            "Aptitude": student.get("aptitude_skill", 0),
            "Communication": student.get("communication_skill", 0),
            "Problem Solving": student.get("problem_solving", 0),
            "Technical": min(tech_skills_count * 2, 10)  # Convert skills count to 0-10 scale
        }
    
    # Handle case where all skills are 0
    if max(skills.values()) == 0:
        return "Technical"
    
    return max(skills, key=skills.get)

def calculate_results(student, branch):
    """Calculate placement readiness, probability, and eligible companies"""
    # Get skills and tools lists
    tech_skills = [s.strip() for s in str(student.get("technical_skills", "")).split(",") if s.strip()]
    tools = [t.strip() for t in str(student.get("tools_known", "")).split(",") if t.strip()]
    
    tech_skill_score = min(len(tech_skills) * 2, 20)  # Max 20 points for skills
    tools_score = min(len(tools) * 1.5, 15)  # Max 15 points for tools
    
    # Calculate base score with proper weightage (max 100)
    score = 0
    
    # CGPA contribution (max 20 points)
    score += (student["cgpa"] / 10) * 20
    
    # Communication skill (max 10 points)
    score += (student.get("communication_skill", 0) / 10) * 10
    
    # Aptitude skill (max 10 points)
    score += (student.get("aptitude_skill", 0) / 10) * 10
    
    # Problem solving (max 10 points)
    score += (student.get("problem_solving", 0) / 10) * 10
    
    # Projects (max 10 points - 2 points per project)
    score += min(student.get("projects_count", 0) * 2, 10)
    
    # Internships (max 10 points - 2 points per internship)
    score += min(student.get("internship_count", 0) * 2, 10)
    
    # Internship company level (max 5 points)
    score += (student.get("internship_company_level", 0) / 3) * 5
    
    # Certifications (max 5 points)
    score += min(student.get("certification_count", 0) * 1, 5)
    
    # Certification level (max 3 points)
    score += (student.get("certification_company_level", 0) / 3) * 3
    
    # Technical skills
    score += tech_skill_score
    
    # Tools known
    score += tools_score
    
    # Coding skill for tech branches (max 15 points)
    if branch in ["CSE", "ECE"]:
        score += (student.get("coding_skill", 0) / 10) * 15
    
    # Ensure score doesn't exceed 100
    readiness = min(round(score, 2), 100)
    probability = round(readiness / 100, 2)
    
    # Determine status
    if readiness >= PLACEMENT_THRESHOLD:
        status = "PLACED ✅"
    else:
        status = "NOT PLACED ❌"
    
    # Get eligible companies (CGPA >= 6.0)
    companies = BRANCH_COMPANIES.get(branch, [])
    eligible = [c for c in companies if student["cgpa"] >= 6.0]
    
    # If no eligible companies due to low CGPA, show all with note
    if not eligible and companies:
        eligible = companies[:3]
    
    strength = detect_strength(student, branch)
    
    return readiness, probability, status, strength, eligible

def career_insights(student, branch):
    """Generate personalized career insights"""
    strengths = []
    improvements = []
    recommendations = []

    # CGPA Analysis
    if student["cgpa"] >= 8.5:
        strengths.append("🏆 Excellent Academic Record - Top percentile")
    elif student["cgpa"] >= 7.5:
        strengths.append("📚 Good Academic Performance")
    elif student["cgpa"] >= 6.0:
        improvements.append("📈 Aim for CGPA above 7.5 for better opportunities")
    else:
        improvements.append("⚠️ CGPA below 6.0 - Focus on academic improvement")

    # Coding Skills (for tech branches)
    if branch in ["CSE", "ECE"]:
        if student.get("coding_skill", 0) >= 8:
            strengths.append("💻 Strong Coding Skills - Ready for technical interviews")
        elif student.get("coding_skill", 0) >= 6:
            strengths.append("👨‍💻 Good Coding Foundation - Practice more problems")
        else:
            improvements.append("🔧 Improve coding skills - Practice on LeetCode/HackerRank")

    # Communication Skills
    if student.get("communication_skill", 0) >= 8:
        strengths.append("🗣️ Excellent Communication Skills")
    elif student.get("communication_skill", 0) >= 6:
        strengths.append("💬 Good Communication Skills")
    else:
        improvements.append("🎯 Enhance communication - Participate in debates/speaking events")

    # Projects
    projects = student.get("projects_count", 0)
    if projects >= 3:
        strengths.append(f"🎯 Strong Project Portfolio ({projects} projects)")
    elif projects >= 2:
        strengths.append(f"📁 Decent Project Experience ({projects} projects)")
    else:
        improvements.append("🛠️ Build more real-time projects to showcase skills")

    # Internships
    internships = student.get("internship_count", 0)
    if internships >= 2:
        strengths.append(f"💼 Good Industry Exposure ({internships} internships)")
    elif internships >= 1:
        strengths.append(f"📅 Has internship experience ({internships} internship)")
    else:
        improvements.append("🏢 Gain internship experience for industry exposure")

    # Certifications
    certs = student.get("certification_count", 0)
    if certs >= 3:
        strengths.append(f"📜 Multiple Certifications ({certs})")
    elif certs >= 1:
        strengths.append(f"✅ Certified Professional ({certs} certification(s))")
    else:
        improvements.append("📖 Get industry-recognized certifications")

    # Technical Skills Analysis
    tech_skills = len(str(student.get("technical_skills", "")).split(",")) if student.get("technical_skills") else 0
    if tech_skills >= 5:
        strengths.append(f"🔧 Diverse Technical Skills ({tech_skills} skills)")
    elif tech_skills >= 3:
        strengths.append(f"⚙️ Good Technical Foundation")
    else:
        improvements.append("🎓 Learn more technical skills relevant to your branch")

    # Branch-specific recommendations
    if branch == "CSE":
        recommendations.append("🎯 Focus on Data Structures & Algorithms for tech interviews")
        recommendations.append("🌐 Build a strong GitHub portfolio")
    elif branch == "ECE":
        recommendations.append("🔌 Master embedded systems and IoT concepts")
        recommendations.append("📡 Work on hardware-software integration projects")
    elif branch == "MECHANICAL":
        recommendations.append("🏭 Learn industry-standard CAD software")
        recommendations.append("🔧 Develop hands-on workshop skills")
    elif branch == "CIVIL":
        recommendations.append("🏗️ Focus on structural analysis and design software")
        recommendations.append("📐 Get AutoCAD certification")
    elif branch == "ELECTRICAL":
        recommendations.append("⚡ Master power systems and control theory")
        recommendations.append("🔌 Work on PLC and SCADA projects")

    return strengths, improvements, recommendations

def save_student(student):
    """Save student data to CSV"""
    global df
    
    # Check if student already exists
    if student["student_id"] in df["student_id"].values:
        # Update existing record
        df.loc[df["student_id"] == student["student_id"]] = pd.Series(student)
        print("🔄 Student record updated successfully!")
    else:
        # Add new record
        df = pd.concat([df, pd.DataFrame([student])], ignore_index=True)
        print("💾 New student registered successfully!")
    
    # Save to CSV
    df.to_csv(DATA_PATH, index=False)

def show_dashboard(student, branch):
    """Display comprehensive student dashboard"""
    readiness, probability, status, strength, eligible = calculate_results(student, branch)
    strengths, improvements, recommendations = career_insights(student, branch)
    
    print("\n" + "="*60)
    print("📊 STUDENT PLACEMENT DASHBOARD")
    print("="*60)
    
    # Basic Info
    print(f"\n📌 BASIC INFORMATION")
    print(f"   Student ID    : {student.get('student_id', 'N/A')}")
    print(f"   Name          : {student.get('student_name', 'N/A')}")
    print(f"   Branch        : {student.get('branch', 'N/A')}")
    print(f"   CGPA          : {student.get('cgpa', 'N/A')}")
    print(f"   Core Strength : {strength}")
    print(f"   Career Path   : {student.get('selected_career', 'N/A')}")
    
    # Performance Metrics
    print(f"\n📈 PERFORMANCE METRICS")
    print(f"   Readiness Score      : {readiness}/100")
    print(f"   Placement Probability: {probability:.1%}")
    
    # Progress Bar
    bar_length = 30
    filled = int(bar_length * readiness / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"   Progress             : [{bar}] {readiness}%")
    
    # Status with color indicator (visual only)
    status_indicator = "🟢" if "PLACED" in status else "🔴"
    print(f"   Status               : {status_indicator} {status}")
    
    # Companies
    print(f"\n🏢 ELIGIBLE COMPANIES")
    if eligible:
        for i, company in enumerate(eligible[:5], 1):
            print(f"   {i}. {company}")
        if len(eligible) > 5:
            print(f"   ... and {len(eligible) - 5} more")
    else:
        print("   No companies listed. Focus on improving your profile.")
    
    # Strengths
    print(f"\n✅ STRENGTHS")
    if strengths:
        for s in strengths:
            print(f"   • {s}")
    else:
        print("   • No strengths identified yet")
    
    # Areas to Improve
    print(f"\n⚠️ AREAS FOR IMPROVEMENT")
    if improvements:
        for i in improvements:
            print(f"   • {i}")
    else:
        print("   • Keep maintaining your current performance!")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    if recommendations:
        for r in recommendations[:3]:
            print(f"   • {r}")
    
    # Skill Breakdown (if available)
    tech_skills = str(student.get("technical_skills", "")).split(",") if student.get("technical_skills") else []
    tools = str(student.get("tools_known", "")).split(",") if student.get("tools_known") else []
    
    if tech_skills and tech_skills[0]:
        print(f"\n🔧 TECHNICAL SKILLS")
        for skill in tech_skills[:4]:
            print(f"   • {skill.strip()}")
        if len(tech_skills) > 4:
            print(f"   • ... and {len(tech_skills) - 4} more")
    
    if tools and tools[0]:
        print(f"\n🛠️ TOOLS KNOWN")
        for tool in tools[:4]:
            print(f"   • {tool.strip()}")
        if len(tools) > 4:
            print(f"   • ... and {len(tools) - 4} more")
    
    print("\n" + "="*60)
    
    # Return values for potential saving
    return readiness, status

def student_registration():
    """Handle new student registration"""
    print("\n" + "="*60)
    print("📝 NEW STUDENT REGISTRATION")
    print("="*60)
    
    student_id = input("Student ID: ").strip().upper()
    
    # Check if student already exists
    existing = df[df["student_id"] == student_id]
    if not existing.empty:
        print(f"\n👋 Welcome back, {existing.iloc[0].get('student_name', 'Student')}!")
        return existing.iloc[0].to_dict()
    
    # New student registration
    student = {"student_id": student_id}
    
    student["student_name"] = input("Full Name: ").strip().title()
    
    # Branch selection
    print("\nAvailable Branches: CSE, ECE, MECHANICAL, CIVIL, ELECTRICAL, OTHER")
    while True:
        branch = input("Branch: ").strip().upper()
        if branch in BRANCH_SKILLS:
            student["branch"] = branch
            break
        else:
            print("❌ Invalid branch. Please choose from the list.")
    
    student["cgpa"] = validate_numeric_input("CGPA (0-10): ", 0, 10, True)
    
    # Branch-specific inputs
    if student["branch"] in ["CSE", "ECE"]:
        student["coding_skill"] = validate_numeric_input("Coding Skill (0-10): ", 0, 10, True)
    else:
        student["coding_skill"] = 0
    
    student["communication_skill"] = validate_numeric_input("Communication Skill (0-10): ", 0, 10, True)
    student["aptitude_skill"] = validate_numeric_input("Aptitude Skill (0-10): ", 0, 10, True)
    student["problem_solving"] = validate_numeric_input("Problem Solving (0-10): ", 0, 10, True)
    student["projects_count"] = validate_numeric_input("Projects Completed (0-20): ", 0, 20, False)
    student["internship_count"] = validate_numeric_input("Internships Done (0-10): ", 0, 10, False)
    student["internship_company_level"] = validate_numeric_input("Internship Company Level (0-3, 3=Highest): ", 0, 3, False)
    student["certification_count"] = validate_numeric_input("Certifications Completed (0-10): ", 0, 10, False)
    student["certification_company_level"] = validate_numeric_input("Certification Level (0-3, 3=Highest): ", 0, 3, False)
    
    # Technical skills selection
    print(f"\n💻 Available Technical Skills for {student['branch']}:")
    skills_list = BRANCH_SKILLS.get(student["branch"], BRANCH_SKILLS["OTHER"])
    for i, skill in enumerate(skills_list[:8], 1):
        print(f"   {i}. {skill}")
    
    skills_input = input("\nEnter technical skills (comma-separated, you can add custom ones): ")
    student["technical_skills"] = skills_input
    
    # Tools selection
    print(f"\n🛠️ Available Tools for {student['branch']}:")
    tools_list = BRANCH_TOOLS.get(student["branch"], BRANCH_TOOLS["OTHER"])
    for i, tool in enumerate(tools_list[:8], 1):
        print(f"   {i}. {tool}")
    
    tools_input = input("\nEnter tools known (comma-separated, you can add custom ones): ")
    student["tools_known"] = tools_input
    
    # Career path based on strength
    strength = detect_strength(student, student["branch"])
    career_options = CAREER_BY_STRENGTH.get(strength, ["Professional"])
    student["selected_career"] = career_options[0]
    
    # Calculate initial scores
    readiness, probability, status, _, _ = calculate_results(student, student["branch"])
    student["readiness_score"] = readiness
    student["placement_status"] = status
    student["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return student

def faculty_dashboard():
    """Display faculty dashboard with analytics"""
    global df
    
    print("\n" + "="*60)
    print("👨‍🏫 FACULTY DASHBOARD")
    print("="*60)
    
    if df.empty or len(df) == 0:
        print("\n📭 No students registered yet.")
        return
    
    # Basic statistics
    total_students = len(df)
    placed_students = len(df[df["placement_status"].str.contains("PLACED", na=False)]) if "placement_status" in df.columns else 0
    avg_cgpa = df["cgpa"].mean() if "cgpa" in df.columns else 0
    
    print(f"\n📊 OVERVIEW STATISTICS")
    print(f"   Total Students    : {total_students}")
    print(f"   Placed Students   : {placed_students}")
    print(f"   Placement Rate    : {(placed_students/total_students*100):.1f}%")
    print(f"   Average CGPA      : {avg_cgpa:.2f}")
    
    # Branch-wise distribution
    print(f"\n📚 BRANCH-WISE DISTRIBUTION")
    if "branch" in df.columns:
        branch_counts = df["branch"].value_counts()
        for branch, count in branch_counts.items():
            branch_placed = len(df[(df["branch"] == branch) & (df["placement_status"].str.contains("PLACED", na=False))]) if "placement_status" in df.columns else 0
            print(f"   {branch:12} : {count:3} students (Placed: {branch_placed})")
    
    # Top performers
    print(f"\n🏆 TOP PERFORMERS")
    if "readiness_score" in df.columns:
        top_students = df.nlargest(5, "readiness_score")[["student_id", "student_name", "branch", "cgpa", "readiness_score"]]
        for idx, student in top_students.iterrows():
            print(f"   {student['student_name']:20} | {student['branch']:10} | CGPA: {student['cgpa']:.2f} | Score: {student['readiness_score']:.1f}")
    
    # Students needing attention
    print(f"\n⚠️ STUDENTS NEEDING ATTENTION")
    if "readiness_score" in df.columns:
        low_performers = df[df["readiness_score"] < 50].nsmallest(5, "readiness_score")[["student_id", "student_name", "branch", "cgpa", "readiness_score"]]
        if not low_performers.empty:
            for idx, student in low_performers.iterrows():
                print(f"   {student['student_name']:20} | {student['branch']:10} | CGPA: {student['cgpa']:.2f} | Score: {student['readiness_score']:.1f}")
        else:
            print("   No students with low readiness scores!")
    
    # Recent registrations
    print(f"\n📅 RECENT REGISTRATIONS")
    if "created_at" in df.columns:
        recent = df.sort_values("created_at", ascending=False).head(5)
        for idx, student in recent.iterrows():
            created = student.get("created_at", "Unknown")[:10]
            print(f"   {student['student_name']:20} | {student['branch']:10} | Registered: {created}")
    
    # Export option
    print("\n" + "="*60)
    export_choice = input("Export data to CSV? (y/n): ").strip().lower()
    if export_choice == 'y':
        export_file = f"data/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(export_file, index=False)
        print(f"✅ Data exported to {export_file}")
    
    input("\nPress Enter to continue...")

# --------------------------------------------
# MAIN LOOP
# --------------------------------------------
def main():
    """Main application loop"""
    print("\n" + "="*60)
    print("🎓 WELCOME TO PLACEMATE - STUDENT PLACEMENT SYSTEM")
    print("="*60)
    
    while True:
        print("\n" + "="*30)
        print("    MAIN MENU")
        print("="*30)
        print("1️⃣  Student Portal")
        print("2️⃣  Faculty Portal")
        print("3️⃣  View All Students")
        print("4️⃣  Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # Student Portal
            student = student_registration()
            
            # Calculate and save results
            readiness, status = show_dashboard(student, student["branch"])
            
            # Update student record with latest scores
            student["readiness_score"] = readiness
            student["placement_status"] = status
            save_student(student)
            
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            # Faculty Portal
            faculty_dashboard()
        
        elif choice == "3":
            # View all students
            print("\n" + "="*60)
            print("📋 ALL REGISTERED STUDENTS")
            print("="*60)
            
            if df.empty or len(df) == 0:
                print("\n📭 No students registered yet.")
            else:
                # Display student list
                display_cols = ["student_id", "student_name", "branch", "cgpa", "readiness_score", "placement_status"]
                available_cols = [col for col in display_cols if col in df.columns]
                
                if available_cols:
                    print(df[available_cols].to_string(index=False))
                else:
                    print(df.to_string(index=False))
            
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            print("\n👋 Thank you for using PlaceMate!")
            print("📊 Good luck with your placement preparations!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

# Run the application
if __name__ == "__main__":
    main()