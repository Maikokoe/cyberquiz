QUIZ_QUESTIONS = [
    {"id": 1, "category": "Network Security", "difficulty": "easy", "question": "What does TCP/IP stand for?", "options": ["Transmission Control Protocol/Internet Protocol", "Transfer Connection Point/Internet Provider", "Transmit Control Package/IP", "Transport Cable Protocol/Internal Process"], "correct": 0, "explanation": "TCP/IP is the fundamental protocol suite used for internet communication."},
    {"id": 2, "category": "Network Security", "difficulty": "easy", "question": "What is the primary role of a Network Security professional?", "options": ["Protect network infrastructure from cyber threats", "Fix hardware issues", "Manage email systems", "Create software applications"], "correct": 0, "explanation": "Network security professionals focus on protecting networks from unauthorized access and attacks."},
    {"id": 3, "category": "Network Security", "difficulty": "medium", "question": "What is a VLAN?", "options": ["Virtual Local Area Network", "Very Large Access Network", "Virtual LAN Architecture", "Volatile Link Access Node"], "correct": 0, "explanation": "A VLAN is a virtual network that logically groups devices for better security and management."},
    {"id": 4, "category": "WiFi Security", "difficulty": "easy", "question": "What does SSID stand for?", "options": ["Service Set Identifier", "Secured Signal ID", "System Security Interface", "Signal Strength Indicator"], "correct": 0, "explanation": "SSID is the name of a wireless network that devices see when scanning."},
    {"id": 5, "category": "WiFi Security", "difficulty": "medium", "question": "Which WiFi security protocol is most vulnerable?", "options": ["WEP", "WPA2", "WPA3", "WPS"], "correct": 0, "explanation": "WEP has known vulnerabilities and should be avoided."},
    {"id": 6, "category": "Firewall", "difficulty": "easy", "question": "What is the primary function of a firewall?", "options": ["Control traffic entering and leaving a network", "Encrypt all data", "Prevent software viruses", "Monitor CPU usage"], "correct": 0, "explanation": "Firewalls use ACLs to allow or deny traffic based on rules."},
    {"id": 7, "category": "Penetration Testing", "difficulty": "easy", "question": "What is the first phase of penetration testing?", "options": ["Reconnaissance", "Exploitation", "Maintenance", "Reporting"], "correct": 0, "explanation": "Reconnaissance involves gathering information about the target system."},
    {"id": 8, "category": "Penetration Testing", "difficulty": "medium", "question": "What is port scanning used for?", "options": ["Identifying open ports and services on a target", "Encrypting network data", "Blocking unauthorized access", "Managing firewall rules"], "correct": 0, "explanation": "Port scanning helps discover what services are running on a target system."},
    {"id": 9, "category": "Ethical Hacking", "difficulty": "easy", "question": "What is ethical hacking?", "options": ["Authorized security testing to find vulnerabilities", "Illegal hacking for profit", "Testing without permission", "Computer sabotage"], "correct": 0, "explanation": "Ethical hacking must have proper authorization and follow legal guidelines."},
    {"id": 10, "category": "Python Scripting", "difficulty": "easy", "question": "What is the purpose of libraries in Python?", "options": ["Reusable code modules for common tasks", "Store data permanently", "Encrypt sensitive information", "Execute shell commands"], "correct": 0, "explanation": "Libraries provide pre-built functions for networking and security tasks."},
]

def get_questions_by_category(category=None, difficulty=None):
    questions = QUIZ_QUESTIONS
    if category:
        questions = [q for q in questions if q["category"] == category]
    if difficulty:
        questions = [q for q in questions if q["difficulty"] == difficulty]
    return questions

def get_all_categories():
    return list(set(q["category"] for q in QUIZ_QUESTIONS))

def get_question_by_id(question_id):
    for q in QUIZ_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None
