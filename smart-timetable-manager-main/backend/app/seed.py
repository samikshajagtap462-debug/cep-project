import logging
from .models import (
    Faculty,
    Subject,
    TimetableEntry,
    Room,
    ClassModel,
    FacultyAssignment
)
from .security import hash_password

logger = logging.getLogger(__name__)

# ==========================================================
# 1. CLASSES DEFINITION (AI&DS DEPARTMENT ONLY)
# ==========================================================
CLASSES = [
    ("SY", "AD1", "SY-AD1"),
    ("SY", "AD2", "SY-AD2"),
    ("SY", "AD3", "SY-AD3"),
    ("TY", "AD1", "TY-AD1"),
    ("TY", "AD2", "TY-AD2"),
    ("BE", "AD1", "BE-AD1"),
    ("BE", "AD2", "BE-AD2"),
]

# ==========================================================
# 2. ROOMS DEFINITION (10 INTENDED FACILITIES)
# ==========================================================
ROOMS = [
    ("Room 102", "Classroom", 60),
    ("Room 103", "Classroom", 60),
    ("Room 104", "Classroom", 60),
    ("Lab 609A", "Laboratory", 40),
    ("Lab 609B", "Laboratory", 40),
    ("AI1", "AI Lab 1", 40),
    ("AI2", "AI Lab 2", 40),
    ("CN1", "CN Lab 1", 40),
    ("IIOT", "IIOT Lab", 40),
    ("ARVR", "AR/VR Lab", 40),
]

# ==========================================================
# 3. FACULTY ACCOUNTS (PRESERVES EXISTING & ADDS OFFICIAL AI&DS)
# ==========================================================
ALL_FACULTY = [
    # Preserved baseline accounts
    ("Admin", "admin@edunova.edu", "ADM-101", "admin", "Administration", 16, "admin123"),
    ("Dr. Sharma", "sharma@edunova.edu", "FAC-101", "faculty", "Machine Learning,Advanced AI", 16, "faculty123"),
    ("Prof. Patil", "patil@edunova.edu", "FAC-102", "faculty", "DBMS,Python,SQL", 16, "faculty123"),
    ("Prof. Joshi", "joshi@edunova.edu", "FAC-103", "faculty", "DBMS,Python,SQL", 16, "faculty123"),
    ("Dr. Kulkarni", "kulkarni@edunova.edu", "FAC-104", "faculty", "Machine Learning,AI,Data Structures", 16, "faculty123"),
    ("Prof. Pawar", "pawar@edunova.edu", "FAC-105", "faculty", "Computer Networks,DBMS", 16, "faculty123"),
    
    # Official AI&DS Department Faculty (MMCOE, Pune) from Timetables
    ("Mrs. Ashvini N. Ahirrao", "ana@edunova.edu", "FAC-ANA", "faculty", "PS&OOP,PS&OOPL,EDIL", 18, "faculty123"),
    ("Mrs. Abhilasha S. Shinde", "ass@edunova.edu", "FAC-ASS", "faculty", "Discrete Mathematics,CE&IL", 18, "faculty123"),
    ("Mrs. Sinu J. Nambiar", "sjn@edunova.edu", "FAC-SJN", "faculty", "Operating Systems,OSL", 18, "faculty123"),
    ("Dr. Vina Lomte", "vl@edunova.edu", "FAC-VL", "faculty", "Sustainable Engineering Practices,MDM,SRP", 18, "faculty123"),
    ("Dr. M. K. Mokashi", "mkm@edunova.edu", "FAC-MKM", "faculty", "PS&OOP,SRP", 18, "faculty123"),
    ("Mrs. Swati D. Jakkan", "sdj@edunova.edu", "FAC-SDJ", "faculty", "Discrete Mathematics,CE&IL", 18, "faculty123"),
    ("Mrs. Kalpna P. Saharan", "kps@edunova.edu", "FAC-KPS", "faculty", "Operating Systems,OSL,CE&IL", 18, "faculty123"),
    ("Mrs. Shruti A. Kulkarni", "sak@edunova.edu", "FAC-SAK", "faculty", "PS&OOP,PS&OOPL,EDIL", 18, "faculty123"),
    ("Mrs. Dhanashree A. Gore", "dag@edunova.edu", "FAC-DAG", "faculty", "Operating Systems,OSL,Edge Computing", 18, "faculty123"),
    ("Mrs. Gayatri Rukare", "gr@edunova.edu", "FAC-GR", "faculty", "AT&A,CE&IL,OEL,EDIL", 18, "faculty123"),
    ("Mrs. Supriya D. Kapase", "sdk@edunova.edu", "FAC-SDK", "faculty", "CE&IL", 16, "faculty123"),
    ("Dr. Mrunal Kothari", "mk@edunova.edu", "FAC-MK", "faculty", "PC&PD", 16, "faculty123"),
    ("Dr. Dhanraj R. Dhotre", "drdhotre@edunova.edu", "FAC-DRD", "admin", "SRP,Administration", 18, "admin123"),
    ("Mrs. Mayuri S. Agrawal", "msa@edunova.edu", "FAC-MSA", "faculty", "AI&ML,AI&MLL,SDM", 18, "faculty123"),
    ("Mrs. Pooja Chavan", "pc@edunova.edu", "FAC-PC", "faculty", "CN&CC,CN&CCL,SRP", 18, "faculty123"),
    ("Mr. Rishikesh C. Yeolekar", "rcy@edunova.edu", "FAC-RCY", "faculty", "AR&VR,EDIL", 16, "faculty123"),
    ("Ms. Avani Anawardekar", "ara@edunova.edu", "FAC-ARA", "faculty", "IISS,IISSL,EDIL,MDM", 18, "faculty123"),
    ("Mrs. Deepali Bhaturkar", "db@edunova.edu", "FAC-DB", "faculty", "AI&MLL,EDIL", 16, "faculty123"),
]

ACRONYM_TO_EMAIL = {
    "ANA": "ana@edunova.edu",
    "ASS": "ass@edunova.edu",
    "SJN": "sjn@edunova.edu",
    "VL": "vl@edunova.edu",
    "MKM": "mkm@edunova.edu",
    "SDJ": "sdj@edunova.edu",
    "KPS": "kps@edunova.edu",
    "SAK": "sak@edunova.edu",
    "DAG": "dag@edunova.edu",
    "DG": "dag@edunova.edu",
    "GR": "gr@edunova.edu",
    "SDK": "sdk@edunova.edu",
    "MK": "mk@edunova.edu",
    "MBK": "mk@edunova.edu",
    "DRD": "drdhotre@edunova.edu",
    "MSA": "msa@edunova.edu",
    "PC": "pc@edunova.edu",
    "RCY": "rcy@edunova.edu",
    "ARA": "ara@edunova.edu",
    "DB": "db@edunova.edu",
}

# ==========================================================
# 4. OFFICIAL TIMETABLE ENTRIES (EXTRACTED FROM SCREENSHOTS)
# ==========================================================
OFFICIAL_TIMETABLE_ENTRIES = [
    # SY AD1 (Semester III)
    ("SY-AD1", "Monday", "10:15", "11:15", "Problem Solving & Object-Oriented Programming", "Room 102", "ANA", None, False, "Theory"),
    ("SY-AD1", "Monday", "11:15", "12:15", "Operating System & Administration", "Room 102", "SJN", None, False, "Theory"),
    ("SY-AD1", "Monday", "13:00", "14:00", "Problem Solving & Object-Oriented Programming", "Room 102", "ANA", None, False, "Theory"),
    ("SY-AD1", "Monday", "14:00", "15:00", "Discrete Mathematics", "Room 102", "ASS", None, False, "Theory"),
    ("SY-AD1", "Monday", "15:15", "17:15", "Operating Systems Laboratory", "AI1", "SJN", "Batch A", True, "Practical"),
    ("SY-AD1", "Monday", "15:15", "17:15", "Community Engagement and Innovation Lab-I", "AI2", "ASS", "Batch B", True, "Practical"),
    ("SY-AD1", "Monday", "15:15", "17:15", "Scientific Research & Publication", "IIOT", "DRD", "Batch C", True, "Practical"),
    ("SY-AD1", "Tuesday", "08:00", "10:00", "Community Engagement and Innovation Lab-I", "AI2", "ASS", "Batch A", True, "Practical"),
    ("SY-AD1", "Tuesday", "08:00", "10:00", "Problem Solving & Object-Oriented Programming Lab", "CN1", "ANA", "Batch B", True, "Practical"),
    ("SY-AD1", "Tuesday", "08:00", "10:00", "Professional Communication & Personality Development", "Lab 609A", "MK", "Batch C", True, "Practical"),
    ("SY-AD1", "Tuesday", "10:15", "12:15", "Sustainable Engineering Practices", "Room 103", "VL", None, False, "Theory"),
    ("SY-AD1", "Tuesday", "13:00", "15:00", "Sustainable Engineering Practices Lab", "AI1", "VL", "Batch A", True, "Practical"),
    ("SY-AD1", "Wednesday", "08:00", "10:00", "Professional Communication & Personality Development", "Lab 609A", "MK", "Batch A", True, "Practical"),
    ("SY-AD1", "Wednesday", "08:00", "10:00", "Community Engagement and Innovation Lab-I", "AI2", "ASS", "Batch B", True, "Practical"),
    ("SY-AD1", "Wednesday", "08:00", "10:00", "Operating Systems Laboratory", "AI1", "SJN", "Batch C", True, "Practical"),
    ("SY-AD1", "Wednesday", "10:15", "11:15", "Discrete Mathematics", "Room 103", "ASS", None, False, "Theory"),
    ("SY-AD1", "Wednesday", "11:15", "12:15", "Operating System & Administration", "Room 103", "SJN", None, False, "Theory"),
    ("SY-AD1", "Wednesday", "13:00", "15:00", "Scientific Research & Publication", "IIOT", "DRD", "Batch A", True, "Practical"),
    ("SY-AD1", "Wednesday", "13:00", "15:00", "Professional Communication & Personality Development", "Room MB614", "MK", "Batch B", True, "Practical"),
    ("SY-AD1", "Wednesday", "13:00", "15:00", "Community Engagement and Innovation Lab-I", "ARVR", "GR", "Batch C", True, "Practical"),
    ("SY-AD1", "Thursday", "08:00", "09:00", "Operating System & Administration", "Room 102", "SJN", None, False, "Theory"),
    ("SY-AD1", "Thursday", "09:00", "10:00", "Discrete Mathematics", "Room 102", "ASS", None, False, "Theory"),
    ("SY-AD1", "Thursday", "10:15", "12:15", "Community Engagement and Innovation Lab-I", "ARVR", "ASS", "Batch A", True, "Practical"),
    ("SY-AD1", "Thursday", "10:15", "12:15", "Scientific Research & Publication", "IIOT", "DRD", "Batch B", True, "Practical"),
    ("SY-AD1", "Thursday", "10:15", "12:15", "Problem Solving & Object-Oriented Programming Lab", "CN1", "ANA", "Batch C", True, "Practical"),
    ("SY-AD1", "Thursday", "13:00", "14:00", "Problem Solving & Object-Oriented Programming", "Room 102", "ANA", None, False, "Theory"),
    ("SY-AD1", "Friday", "08:00", "10:00", "Problem Solving & Object-Oriented Programming Lab", "CN1", "ANA", "Batch A", True, "Practical"),
    ("SY-AD1", "Friday", "08:00", "10:00", "Operating Systems Laboratory", "AI1", "SJN", "Batch B", True, "Practical"),
    ("SY-AD1", "Friday", "08:00", "10:00", "Community Engagement and Innovation Lab-I", "AI2", "GR", "Batch C", True, "Practical"),
    ("SY-AD1", "Friday", "10:15", "12:15", "Sustainable Engineering Practices Lab", "AI1", "VL", "Batch B", True, "Practical"),
    ("SY-AD1", "Friday", "13:00", "15:00", "Sustainable Engineering Practices Lab", "AI1", "VL", "Batch C", True, "Practical"),
    ("SY-AD1", "Friday", "16:15", "17:15", "Universal Human Values", "Room 102", "ANA", None, False, "Tutorial"),

    # SY AD2 (Semester III)
    ("SY-AD2", "Monday", "08:00", "10:00", "Professional Communication & Personality Development", "Lab 609A", "MK", "Batch A", True, "Practical"),
    ("SY-AD2", "Monday", "08:00", "10:00", "Operating Systems Laboratory", "ARVR", "KPS", "Batch B", True, "Practical"),
    ("SY-AD2", "Monday", "08:00", "10:00", "Problem Solving & Object-Oriented Programming Lab", "Lab 609B", "MKM", "Batch C", True, "Practical"),
    ("SY-AD2", "Monday", "10:15", "11:15", "Problem Solving & Object-Oriented Programming", "Room 104", "MKM", None, False, "Theory"),
    ("SY-AD2", "Monday", "11:15", "12:15", "Discrete Mathematics", "Room 104", "SDJ", None, False, "Theory"),
    ("SY-AD2", "Monday", "13:00", "15:00", "Operating Systems Laboratory", "AI1", "KPS", "Batch A", True, "Practical"),
    ("SY-AD2", "Monday", "13:00", "15:00", "Community Engagement and Innovation Lab-I", "Lab 609A", "SDJ", "Batch B", True, "Practical"),
    ("SY-AD2", "Monday", "13:00", "15:00", "Scientific Research & Publication", "Lab 609B", "VL", "Batch C", True, "Practical"),
    ("SY-AD2", "Tuesday", "08:00", "09:00", "Discrete Mathematics", "Room 102", "SDJ", None, False, "Theory"),
    ("SY-AD2", "Tuesday", "09:00", "10:00", "Operating System & Administration", "Room 102", "KPS", None, False, "Theory"),
    ("SY-AD2", "Tuesday", "10:15", "12:15", "Sustainable Engineering Practices", "Room 103", "VL", None, False, "Theory"),
    ("SY-AD2", "Tuesday", "13:00", "15:00", "Sustainable Engineering Practices Lab", "AI1", "VL", "Batch A", True, "Practical"),
    ("SY-AD2", "Wednesday", "10:15", "12:15", "Scientific Research & Publication", "Lab 609A", "VL", "Batch A", True, "Practical"),
    ("SY-AD2", "Wednesday", "10:15", "12:15", "Problem Solving & Object-Oriented Programming Lab", "Lab 609B", "MKM", "Batch B", True, "Practical"),
    ("SY-AD2", "Wednesday", "10:15", "12:15", "Operating Systems Laboratory", "AI2", "KPS", "Batch C", True, "Practical"),
    ("SY-AD2", "Wednesday", "13:00", "14:00", "Discrete Mathematics", "Room 102", "SDJ", None, False, "Theory"),
    ("SY-AD2", "Wednesday", "14:00", "15:00", "Problem Solving & Object-Oriented Programming", "Room 102", "MKM", None, False, "Theory"),
    ("SY-AD2", "Wednesday", "15:15", "17:15", "Community Engagement and Innovation Lab-I", "AI1", "KPS", "Batch A", True, "Practical"),
    ("SY-AD2", "Wednesday", "15:15", "17:15", "Scientific Research & Publication", "Lab 609A", "VL", "Batch B", True, "Practical"),
    ("SY-AD2", "Wednesday", "15:15", "17:15", "Community Engagement and Innovation Lab-I", "IIOT", "SDJ", "Batch C", True, "Practical"),
    ("SY-AD2", "Thursday", "08:00", "10:00", "Problem Solving & Object-Oriented Programming Lab", "Lab 609B", "MKM", "Batch A", True, "Practical"),
    ("SY-AD2", "Thursday", "08:00", "10:00", "Community Engagement and Innovation Lab-I", "IIOT", "SDJ", "Batch B", True, "Practical"),
    ("SY-AD2", "Thursday", "08:00", "10:00", "Professional Communication & Personality Development", "Room 104", "MK", "Batch C", True, "Practical"),
    ("SY-AD2", "Thursday", "10:15", "11:15", "Problem Solving & Object-Oriented Programming", "Room 102", "MKM", None, False, "Theory"),
    ("SY-AD2", "Thursday", "11:15", "12:15", "Operating System & Administration", "Room 102", "KPS", None, False, "Theory"),
    ("SY-AD2", "Thursday", "13:00", "15:00", "Community Engagement and Innovation Lab-I", "AI1", "KPS", "Batch A", True, "Practical"),
    ("SY-AD2", "Thursday", "13:00", "15:00", "Professional Communication & Personality Development", "Room MB614", "MK", "Batch B", True, "Practical"),
    ("SY-AD2", "Thursday", "13:00", "15:00", "Community Engagement and Innovation Lab-I", "IIOT", "SDJ", "Batch C", True, "Practical"),
    ("SY-AD2", "Friday", "09:00", "10:00", "Operating System & Administration", "Room 102", "KPS", None, False, "Theory"),
    ("SY-AD2", "Friday", "10:15", "12:15", "Sustainable Engineering Practices Lab", "AI1", "VL", "Batch B", True, "Practical"),
    ("SY-AD2", "Friday", "13:00", "15:00", "Sustainable Engineering Practices Lab", "AI1", "VL", "Batch C", True, "Practical"),
    ("SY-AD2", "Friday", "16:15", "17:15", "Universal Human Values", "Room 104", "SDJ", None, False, "Tutorial"),

    # SY AD3 (Semester III)
    ("SY-AD3", "Monday", "09:00", "10:00", "Operating System & Administration", "Room 103", "DAG", None, False, "Theory"),
    ("SY-AD3", "Monday", "10:15", "11:15", "Problem Solving & Object-Oriented Programming", "Room 103", "SAK", None, False, "Theory"),
    ("SY-AD3", "Monday", "11:15", "12:15", "Discrete Mathematics", "Room 103", "ASS", None, False, "Theory"),
    ("SY-AD3", "Monday", "13:00", "15:00", "Professional Communication & Personality Development", "IIOT", "MK", "Batch A", True, "Practical"),
    ("SY-AD3", "Monday", "13:00", "15:00", "Scientific Research & Publication", "ARVR", "MKM", "Batch B", True, "Practical"),
    ("SY-AD3", "Monday", "13:00", "15:00", "Community Engagement and Innovation Lab-I", "CN1", "SDK", "Batch C", True, "Practical"),
    ("SY-AD3", "Tuesday", "08:00", "10:00", "Community Engagement and Innovation Lab-I", "ARVR", "GR", "Batch A", True, "Practical"),
    ("SY-AD3", "Tuesday", "08:00", "10:00", "Problem Solving & Object-Oriented Programming Lab", "AI1", "SAK", "Batch B", True, "Practical"),
    ("SY-AD3", "Tuesday", "08:00", "10:00", "Operating Systems Laboratory", "IIOT", "DAG", "Batch C", True, "Practical"),
    ("SY-AD3", "Tuesday", "10:15", "12:15", "Sustainable Engineering Practices", "Room 103", "VL", None, False, "Theory"),
    ("SY-AD3", "Tuesday", "13:00", "15:00", "Sustainable Engineering Practices Lab", "AI1", "VL", "Batch A", True, "Practical"),
    ("SY-AD3", "Wednesday", "08:00", "10:00", "Scientific Research & Publication", "CN1", "MKM", "Batch A", True, "Practical"),
    ("SY-AD3", "Wednesday", "08:00", "10:00", "Operating Systems Laboratory", "IIOT", "DAG", "Batch B", True, "Practical"),
    ("SY-AD3", "Wednesday", "08:00", "10:00", "Problem Solving & Object-Oriented Programming Lab", "ARVR", "SAK", "Batch C", True, "Practical"),
    ("SY-AD3", "Wednesday", "10:15", "12:15", "Community Engagement and Innovation Lab-I", "AI1", "GR", "Batch A", True, "Practical"),
    ("SY-AD3", "Wednesday", "10:15", "12:15", "Community Engagement and Innovation Lab-I", "CN1", "SDK", "Batch B", True, "Practical"),
    ("SY-AD3", "Wednesday", "10:15", "12:15", "Professional Communication & Personality Development", "ARVR", "MK", "Batch C", True, "Practical"),
    ("SY-AD3", "Wednesday", "13:00", "14:00", "Operating System & Administration", "Room 103", "DAG", None, False, "Theory"),
    ("SY-AD3", "Wednesday", "14:00", "15:00", "Discrete Mathematics", "Room 103", "ASS", None, False, "Theory"),
    ("SY-AD3", "Thursday", "08:00", "10:00", "Operating Systems Laboratory", "AI1", "DAG", "Batch A", True, "Practical"),
    ("SY-AD3", "Thursday", "08:00", "10:00", "Community Engagement and Innovation Lab-I", "ARVR", "SDK", "Batch B", True, "Practical"),
    ("SY-AD3", "Thursday", "08:00", "10:00", "Scientific Research & Publication", "CN1", "ANA", "Batch C", True, "Practical"),
    ("SY-AD3", "Thursday", "10:15", "11:15", "Operating System & Administration", "Room 103", "DAG", None, False, "Theory"),
    ("SY-AD3", "Thursday", "11:15", "12:15", "Problem Solving & Object-Oriented Programming", "Room 103", "SAK", None, False, "Theory"),
    ("SY-AD3", "Thursday", "13:00", "14:00", "Discrete Mathematics", "Room 103", "ASS", None, False, "Theory"),
    ("SY-AD3", "Thursday", "14:00", "15:00", "Problem Solving & Object-Oriented Programming", "Room 103", "SAK", None, False, "Theory"),
    ("SY-AD3", "Friday", "08:00", "10:00", "Problem Solving & Object-Oriented Programming Lab", "ARVR", "SAK", "Batch A", True, "Practical"),
    ("SY-AD3", "Friday", "08:00", "10:00", "Professional Communication & Personality Development", "Lab 609A", "MK", "Batch B", True, "Practical"),
    ("SY-AD3", "Friday", "08:00", "10:00", "Community Engagement and Innovation Lab-I", "IIOT", "SDK", "Batch C", True, "Practical"),
    ("SY-AD3", "Friday", "10:15", "12:15", "Sustainable Engineering Practices Lab", "AI1", "VL", "Batch B", True, "Practical"),
    ("SY-AD3", "Friday", "13:00", "15:00", "Sustainable Engineering Practices Lab", "AI1", "VL", "Batch C", True, "Practical"),
    ("SY-AD3", "Friday", "16:15", "17:15", "Universal Human Values", "Room 103", "SAK", None, False, "Tutorial"),

    # TY AD1 (Semester V)
    ("TY-AD1", "Monday", "08:00", "10:00", "Engineering Design and Innovation-I", "IOT", "ANA", "Batch A", True, "Practical"),
    ("TY-AD1", "Monday", "08:00", "10:00", "Engineering Design and Innovation-I", "AI1", "ARA", "Batch B", True, "Practical"),
    ("TY-AD1", "Monday", "08:00", "10:00", "Engineering Design and Innovation-I", "CN1", "DB", "Batch C", True, "Practical"),
    ("TY-AD1", "Monday", "10:15", "12:15", "Artificial Intelligence & Machine Learning Laboratory", "CN1", "MSA", "Batch A", True, "Practical"),
    ("TY-AD1", "Monday", "10:15", "12:15", "Computer Network & Cloud Computing Laboratory", "Lab 609B", "PC", "Batch B", True, "Practical"),
    ("TY-AD1", "Monday", "10:15", "12:15", "Edge Computing", "Lab 609A", "DAG", "Batch C", True, "Practical"),
    ("TY-AD1", "Monday", "13:00", "14:00", "Edge Computing / AR & VR", "Room 104", "DAG", None, False, "Theory"),
    ("TY-AD1", "Monday", "14:00", "15:00", "Sustainable Engineering Practices", "Room 104", "ARA", None, False, "Theory"),
    ("TY-AD1", "Monday", "15:15", "16:15", "Computer Network & Cloud Computing", "Room 104", "PC", None, False, "Theory"),
    ("TY-AD1", "Tuesday", "08:00", "09:00", "Computer Network & Cloud Computing", "Room 102", "PC", None, False, "Theory"),
    ("TY-AD1", "Tuesday", "09:00", "10:00", "Artificial Intelligence & Machine Learning", "Room 102", "MSA", None, False, "Theory"),
    ("TY-AD1", "Tuesday", "10:15", "11:15", "Artificial Intelligence & Machine Learning", "Room 104", "MSA", None, False, "Theory"),
    ("TY-AD1", "Tuesday", "11:15", "12:15", "Automata Theory and Applications", "Room 104", "GR", None, False, "Theory"),
    ("TY-AD1", "Tuesday", "13:00", "15:00", "Sustainable Engineering Practices Lab", "IIOT", "ARA", "Batch A", True, "Practical"),
    ("TY-AD1", "Wednesday", "09:00", "10:00", "Computer Network & Cloud Computing", "Room 104", "PC", None, False, "Theory"),
    ("TY-AD1", "Wednesday", "10:15", "12:15", "Sustainable Engineering Practices", "Room 102", "ARA", None, False, "Theory"),
    ("TY-AD1", "Wednesday", "13:00", "15:00", "Computer Network & Cloud Computing Laboratory", "CN1", "PC", "Batch A", True, "Practical"),
    ("TY-AD1", "Wednesday", "13:00", "15:00", "Artificial Intelligence & Machine Learning Laboratory", "AI1", "MSA", "Batch B", True, "Practical"),
    ("TY-AD1", "Wednesday", "13:00", "15:00", "Artificial Intelligence & Machine Learning Laboratory", "AI2", "DB", "Batch C", True, "Practical"),
    ("TY-AD1", "Wednesday", "15:15", "16:15", "Automata Theory and Applications", "Room 104", "GR", None, False, "Theory"),
    ("TY-AD1", "Wednesday", "16:15", "17:15", "Automata Theory and Applications", "Room 104", "GR", None, False, "Theory"),
    ("TY-AD1", "Thursday", "10:15", "12:15", "Online OEL Lecture", "Online", "GR", None, False, "Theory"),
    ("TY-AD1", "Thursday", "13:00", "15:00", "AR & VR", "ARVR", "RCY", "Batch A", True, "Practical"),
    ("TY-AD1", "Thursday", "13:00", "15:00", "Edge Computing", "Lab 609A", "DAG", "Batch B", True, "Practical"),
    ("TY-AD1", "Thursday", "13:00", "15:00", "Computer Network & Cloud Computing Laboratory", "AI2", "PC", "Batch C", True, "Practical"),
    ("TY-AD1", "Thursday", "15:15", "17:15", "Engineering Design and Innovation-I", "CN1", "ARA", "Batch A", True, "Practical"),
    ("TY-AD1", "Thursday", "15:15", "17:15", "Engineering Design and Innovation-I", "AI1", "SAK", "Batch B", True, "Practical"),
    ("TY-AD1", "Thursday", "15:15", "17:15", "Engineering Design and Innovation-I", "AI2", "RCY", "Batch C", True, "Practical"),
    ("TY-AD1", "Friday", "08:00", "09:00", "Artificial Intelligence & Machine Learning", "Room 104", "MSA", None, False, "Theory"),
    ("TY-AD1", "Friday", "09:00", "10:00", "Edge Computing / AR & VR", "Room 104", "DAG", None, False, "Theory"),
    ("TY-AD1", "Friday", "10:15", "12:15", "Sustainable Engineering Practices Lab", "IIOT", "ARA", "Batch B", True, "Practical"),
    ("TY-AD1", "Friday", "13:00", "15:00", "Sustainable Engineering Practices Lab", "IIOT", "ARA", "Batch C", True, "Practical"),
]


def seed_database(db):
    """
    Idempotent database seeder.
    Preserves all existing user credentials and records.
    Adds all 7 AI&DS classes, rooms, official faculty, subjects, and verified timetables.
    """
    # 1. Classes
    for year, div, name in CLASSES:
        cls = db.query(ClassModel).filter(ClassModel.name == name).first()
        if not cls:
            db.add(ClassModel(academic_year=year, division=div, name=name, department="AI&DS"))
    db.commit()

    class_map = {c.name: c for c in db.query(ClassModel).all()}

    # 2. Rooms - Ensure exactly the 10 intended facilities are active
    intended_names = {name for name, _, _ in ROOMS}
    for name, rtype, cap in ROOMS:
        r = db.query(Room).filter(Room.name == name).first()
        if not r:
            db.add(Room(name=name, room_type=rtype, capacity=cap, active=True))
        else:
            r.active = True
            r.room_type = rtype
            r.capacity = cap
    db.commit()

    # Deactivate any non-intended / sample / duplicate facilities
    for r in db.query(Room).all():
        if r.name not in intended_names:
            r.active = False
    db.commit()

    # 3. Faculty
    for name, email, fac_id, role, expertise, max_h, pwd in ALL_FACULTY:
        f = db.query(Faculty).filter((Faculty.email == email) | (Faculty.faculty_id == fac_id)).first()
        if not f:
            f = Faculty(
                name=name,
                email=email,
                faculty_id=fac_id,
                role=role,
                department="AI&DS",
                expertise=expertise,
                max_hours=max_h,
                password_hash=hash_password(pwd),
                active=True
            )
            db.add(f)
    db.commit()

    fac_by_email = {f.email: f for f in db.query(Faculty).all()}
    fac_by_id = {f.faculty_id: f for f in db.query(Faculty).all()}
    fac_by_name = {f.name: f for f in db.query(Faculty).all()}

    def resolve_faculty(code: str) -> Faculty:
        if code in fac_by_id:
            return fac_by_id[code]
        email = ACRONYM_TO_EMAIL.get(code)
        if email and email in fac_by_email:
            return fac_by_email[email]
        if code in fac_by_name:
            return fac_by_name[code]
        return fac_by_email.get("sharma@edunova.edu")

    # 4. Official Timetable Entries & Subjects & Faculty Assignments
    for (cls_name, day, start, end, subj, room, fac_code, batch, is_lab, stype) in OFFICIAL_TIMETABLE_ENTRIES:
        fac = resolve_faculty(fac_code)
        cls = class_map.get(cls_name)
        cls_id = cls.id if cls else None

        # Check existing timetable entry
        existing_tt = db.query(TimetableEntry).filter(
            TimetableEntry.class_name == cls_name,
            TimetableEntry.day == day,
            TimetableEntry.start_time == start,
            TimetableEntry.end_time == end,
            TimetableEntry.subject == subj,
            TimetableEntry.batch == batch
        ).first()

        if not existing_tt:
            db.add(TimetableEntry(
                day=day,
                start_time=start,
                end_time=end,
                subject=subj,
                class_name=cls_name,
                room=room,
                faculty_id=fac.id,
                batch=batch,
                is_lab=is_lab,
                session_type=stype,
                class_id=cls_id,
                academic_year=cls.academic_year if cls else None,
                semester="Sem III" if "SY" in cls_name else "Sem V"
            ))

        # Check Subject record
        sub = db.query(Subject).filter(Subject.name == subj).first()
        if not sub:
            sub = Subject(
                name=subj,
                class_name=cls_name,
                academic_year=cls.academic_year if cls else None,
                is_practical=is_lab,
                faculty_id=fac.id,
                total_units=6,
                completed_units=2
            )
            db.add(sub)
            db.flush()

        # Check FacultyAssignment record
        if cls_id:
            assign = db.query(FacultyAssignment).filter(
                FacultyAssignment.faculty_id == fac.id,
                FacultyAssignment.class_id == cls_id,
                FacultyAssignment.batch == batch,
                FacultyAssignment.session_type == stype
            ).first()
            if not assign:
                db.add(FacultyAssignment(
                    faculty_id=fac.id,
                    subject_id=sub.id if sub else None,
                    class_id=cls_id,
                    batch=batch,
                    session_type=stype
                ))

    # Also assign Dr. Sharma (FAC-101) to AI&ML so Dr. Sharma's dashboard is populated
    dr_sharma = fac_by_email.get("sharma@edunova.edu")
    ty_ad1 = class_map.get("TY-AD1")
    if dr_sharma and ty_ad1:
        sharma_assign = db.query(FacultyAssignment).filter(
            FacultyAssignment.faculty_id == dr_sharma.id,
            FacultyAssignment.class_id == ty_ad1.id
        ).first()
        if not sharma_assign:
            ml_sub = db.query(Subject).filter(Subject.name.like("%Machine Learning%")).first()
            db.add(FacultyAssignment(
                faculty_id=dr_sharma.id,
                subject_id=ml_sub.id if ml_sub else None,
                class_id=ty_ad1.id,
                batch=None,
                session_type="Theory"
            ))

    db.commit()
