from app import app, db
from models import Candidate, VCTRecord, Interview, Assessment, Document, Notification, TimelineEvent, User
from datetime import datetime, date, timedelta
import random

stages_order = ['Applications', 'VCT Verification', 'Assessment', 'Shortlisted', 'Interview', 'Selected', 'Documentation', 'Joined']

candidates_data = [
    {'name': 'Rahul Sharma', 'email': 'rahul.sharma@email.com', 'phone': '+91-98765-43210', 'position': 'Frontend Developer', 'exp': 3.0, 'skills': 'React, JavaScript, CSS, HTML, Bootstrap', 'education': 'B.Tech CSE', 'college': 'IIT Delhi', 'degree': 'B.Tech', 'year': 2023, 'cgpa': 8.2, 'backlogs': 0, 'source': 'LinkedIn', 'status': 'Interview', 'stage': 'Interview', 'verification': 'Verified', 'eligibility': 'Eligible', 'confidence': 96, 'location': 'Delhi', 'avatar': 'blue'},
    {'name': 'Priya Singh', 'email': 'priya.singh@email.com', 'phone': '+91-98765-43211', 'position': 'Data Analyst', 'exp': 2.5, 'skills': 'Python, SQL, Excel, Tableau, Statistics', 'education': 'M.Sc Statistics', 'college': 'DU Delhi', 'degree': 'M.Sc', 'year': 2024, 'cgpa': 7.8, 'backlogs': 0, 'source': 'Naukri', 'status': 'Assessment', 'stage': 'Assessment', 'verification': 'Verified', 'eligibility': 'Eligible', 'confidence': 91, 'location': 'Delhi', 'avatar': 'purple'},
    {'name': 'Aman Verma', 'email': 'aman.verma@email.com', 'phone': '+91-98765-43212', 'position': 'Python Developer', 'exp': 4.0, 'skills': 'Python, Django, Flask, PostgreSQL, Docker', 'education': 'B.Tech IT', 'college': 'NIT Trichy', 'degree': 'B.Tech', 'year': 2020, 'cgpa': 6.9, 'backlogs': 1, 'source': 'Referral', 'status': 'VCT Review', 'stage': 'VCT Verification', 'verification': 'Flagged', 'eligibility': 'Not Eligible', 'confidence': 87, 'location': 'Pune', 'avatar': 'orange'},
    {'name': 'Neha Gupta', 'email': 'neha.gupta@email.com', 'phone': '+91-98765-43213', 'position': 'UI/UX Designer', 'exp': 5.0, 'skills': 'Figma, Adobe XD, Sketch, Prototyping, User Research', 'education': 'B.Des Visual Comm', 'college': 'NID Ahmedabad', 'degree': 'B.Des', 'year': 2019, 'cgpa': 8.4, 'backlogs': 0, 'source': 'LinkedIn', 'status': 'Selected', 'stage': 'Selected', 'verification': 'Verified', 'eligibility': 'Eligible', 'confidence': 94, 'location': 'Mumbai', 'avatar': 'green'},
    {'name': 'Arjun Patel', 'email': 'arjun.patel@email.com', 'phone': '+91-98765-43214', 'position': 'Backend Developer', 'exp': 3.5, 'skills': 'Java, Spring Boot, MySQL, AWS, Microservices', 'education': 'B.Tech CSE', 'college': 'IIIT Hyderabad', 'degree': 'B.Tech', 'year': 2022, 'cgpa': 7.5, 'backlogs': 0, 'source': 'Company Site', 'status': 'Shortlisted', 'stage': 'Shortlisted', 'verification': 'Verified', 'eligibility': 'Eligible', 'confidence': 93, 'location': 'Hyderabad', 'avatar': 'blue'},
    {'name': 'Sneha Kapoor', 'email': 'sneha.kapoor@email.com', 'phone': '+91-98765-43215', 'position': 'Software Engineer', 'exp': 2.0, 'skills': 'JavaScript, Node.js, React, MongoDB, Git', 'education': 'B.Tech CSE', 'college': 'VIT Vellore', 'degree': 'B.Tech', 'year': 2023, 'cgpa': 8.0, 'backlogs': 0, 'source': 'Naukri', 'status': 'Assessment', 'stage': 'Assessment', 'verification': 'Verified', 'eligibility': 'Eligible', 'confidence': 90, 'location': 'Bangalore', 'avatar': 'purple'},
    {'name': 'Rohan Mehta', 'email': 'rohan.mehta@email.com', 'phone': '+91-98765-43216', 'position': 'Frontend Developer', 'exp': 1.5, 'skills': 'HTML, CSS, JavaScript, React, Tailwind', 'education': 'BCA', 'college': 'MU Mumbai', 'degree': 'BCA', 'year': 2024, 'cgpa': 7.2, 'backlogs': 0, 'source': 'Referral', 'status': 'Pending Review', 'stage': 'VCT Verification', 'verification': 'Pending Review', 'eligibility': 'Pending', 'confidence': 76, 'location': 'Mumbai', 'avatar': 'orange'},
    {'name': 'Ananya Gupta', 'email': 'ananya.gupta@email.com', 'phone': '+91-98765-43217', 'position': 'Data Analyst', 'exp': 3.0, 'skills': 'Python, R, SQL, Power BI, Machine Learning', 'education': 'M.Tech Data Science', 'college': 'IIT Bombay', 'degree': 'M.Tech', 'year': 2022, 'cgpa': 8.8, 'backlogs': 0, 'source': 'LinkedIn', 'status': 'Joined', 'stage': 'Joined', 'verification': 'Verified', 'eligibility': 'Eligible', 'confidence': 97, 'location': 'Bangalore', 'avatar': 'green'},
    {'name': 'Karan Joshi', 'email': 'karan.joshi@email.com', 'phone': '+91-98765-43218', 'position': 'DevOps Engineer', 'exp': 4.5, 'skills': 'Docker, Kubernetes, Jenkins, AWS, Terraform, Linux', 'education': 'B.Tech IT', 'college': 'PICT Pune', 'degree': 'B.Tech', 'year': 2020, 'cgpa': 7.0, 'backlogs': 2, 'source': 'Naukri', 'status': 'Flagged', 'stage': 'VCT Verification', 'verification': 'Flagged', 'eligibility': 'Not Eligible', 'confidence': 60, 'location': 'Pune', 'avatar': 'purple'},
    {'name': 'Divya Reddy', 'email': 'divya.reddy@email.com', 'phone': '+91-98765-43219', 'position': 'UI/UX Designer', 'exp': 2.0, 'skills': 'Figma, UI Design, Wireframing, Design Systems', 'education': 'B.Des', 'college': 'Srishti Bangalore', 'degree': 'B.Des', 'year': 2023, 'cgpa': 8.6, 'backlogs': 0, 'source': 'Referral', 'status': 'Assessment', 'stage': 'Assessment', 'verification': 'Verified', 'eligibility': 'Eligible', 'confidence': 92, 'location': 'Bangalore', 'avatar': 'purple'},
    {'name': 'Manish Tiwari', 'email': 'manish.tiwari@email.com', 'phone': '+91-98765-43220', 'position': 'Python Developer', 'exp': 3.0, 'skills': 'Python, Flask, SQLAlchemy, Pandas, NumPy', 'education': 'M.Sc Computer Science', 'college': 'BHU Varanasi', 'degree': 'M.Sc', 'year': 2021, 'cgpa': 7.6, 'backlogs': 0, 'source': 'Naukri', 'status': 'Shortlisted', 'stage': 'Shortlisted', 'verification': 'Verified', 'eligibility': 'Eligible', 'confidence': 88, 'location': 'Varanasi', 'avatar': 'blue'},
    {'name': 'Ishita Bhatia', 'email': 'ishita.bhatia@email.com', 'phone': '+91-98765-43221', 'position': 'Backend Developer', 'exp': 4.0, 'skills': 'Python, FastAPI, PostgreSQL, Docker, GraphQL', 'education': 'B.Tech CSE', 'college': 'NSUT Delhi', 'degree': 'B.Tech', 'year': 2020, 'cgpa': 8.1, 'backlogs': 0, 'source': 'LinkedIn', 'status': 'Joined', 'stage': 'Joined', 'verification': 'Verified', 'eligibility': 'Eligible', 'confidence': 95, 'location': 'Delhi', 'avatar': 'green'},
]

interviews_data = [
    {'candidate_idx': 0, 'interviewer': 'Amit Kumar', 'date': '2026-07-26', 'time': '10:00 AM', 'round': 'Technical Round', 'meet': 'https://meet.google.com/abc-defg-hij', 'status': 'Scheduled'},
    {'candidate_idx': 1, 'interviewer': 'Sonia Reddy', 'date': '2026-07-26', 'time': '11:30 AM', 'round': 'HR Round', 'meet': 'https://meet.google.com/klm-nopq-rst', 'status': 'Scheduled'},
    {'candidate_idx': 2, 'interviewer': 'Ravi Kumar', 'date': '2026-07-26', 'time': '02:00 PM', 'round': 'Technical Round', 'meet': 'https://meet.google.com/uvw-xyz-abc', 'status': 'Scheduled'},
    {'candidate_idx': 3, 'interviewer': 'Priya Sharma', 'date': '2026-07-26', 'time': '04:30 PM', 'round': 'Final Round', 'meet': 'https://meet.google.com/def-ghij-klm', 'status': 'Scheduled'},
    {'candidate_idx': 4, 'interviewer': 'Ravi Kumar', 'date': '2026-07-24', 'time': '09:30 AM', 'round': 'Technical Round', 'meet': 'https://meet.google.com/nop-qrst-uvw', 'status': 'Completed'},
    {'candidate_idx': 5, 'interviewer': 'Ankit Gupta', 'date': '2026-07-24', 'time': '03:00 PM', 'round': 'HR Round', 'meet': 'https://meet.google.com/xyz-abcd-efg', 'status': 'Completed'},
    {'candidate_idx': 10, 'interviewer': 'Priya Sharma', 'date': '2026-07-27', 'time': '10:00 AM', 'round': 'Technical Round', 'meet': 'https://meet.google.com/rst-uvwx-yz', 'status': 'Scheduled'},
    {'candidate_idx': 11, 'interviewer': 'Amit Kumar', 'date': '2026-07-28', 'time': '11:00 AM', 'round': 'Technical Round', 'meet': 'https://meet.google.com/lmn-opqr-stu', 'status': 'Scheduled'},
]

assessments_data = [
    {'candidate_idx': 0, 'name': 'Frontend Developer Assessment', 'type': 'Technical', 'score': 84, 'tech': 88, 'problem': 82, 'coding': 86, 'accuracy': 80, 'result': 'Pass', 'status': 'Completed'},
    {'candidate_idx': 1, 'name': 'Data Analyst Assessment', 'type': 'Technical', 'score': 78, 'tech': 75, 'problem': 80, 'coding': 0, 'accuracy': 82, 'result': 'Pass', 'status': 'Completed'},
    {'candidate_idx': 2, 'name': 'Python Coding Challenge', 'type': 'Coding', 'score': 91, 'tech': 0, 'problem': 90, 'coding': 93, 'accuracy': 88, 'result': 'Pass', 'status': 'Completed'},
    {'candidate_idx': 5, 'name': 'System Design Assessment', 'type': 'Technical', 'score': 45, 'tech': 50, 'problem': 42, 'coding': 0, 'accuracy': 48, 'result': 'Fail', 'status': 'Completed'},
    {'candidate_idx': 4, 'name': 'Backend API Design', 'type': 'Technical', 'score': 72, 'tech': 70, 'problem': 75, 'coding': 68, 'accuracy': 72, 'result': 'Pass', 'status': 'Completed'},
    {'candidate_idx': 6, 'name': 'Frontend Coding Test', 'type': 'Coding', 'score': 65, 'tech': 0, 'problem': 60, 'coding': 68, 'accuracy': 62, 'result': 'Pass', 'status': 'Completed'},
    {'candidate_idx': 9, 'name': 'Design Portfolio Review', 'type': 'Technical', 'score': 88, 'tech': 85, 'problem': 90, 'coding': 0, 'accuracy': 86, 'result': 'Pass', 'status': 'Completed'},
    {'candidate_idx': 7, 'name': 'SQL Assessment', 'type': 'Aptitude', 'score': None, 'tech': None, 'problem': None, 'coding': None, 'accuracy': None, 'result': 'Pending', 'status': 'Pending'},
]

documents_data = [
    {'candidate_idx': 3, 'type': 'Offer Letter', 'trigger': 'Selection', 'status': 'Generated'},
    {'candidate_idx': 0, 'type': 'Call-up Letter', 'trigger': 'Interview', 'status': 'Generated'},
    {'candidate_idx': 2, 'type': 'Offer Letter', 'trigger': 'Selection', 'status': 'Pending'},
    {'candidate_idx': 1, 'type': 'NDA', 'trigger': 'Pre-Interview', 'status': 'Awaiting Signature'},
    {'candidate_idx': 4, 'type': 'Shortlist Letter', 'trigger': 'Shortlisting', 'status': 'Generated'},
    {'candidate_idx': 7, 'type': 'Appointment Letter', 'trigger': 'Joining', 'status': 'Pending'},
    {'candidate_idx': 8, 'type': 'Internship Certificate', 'trigger': 'Completion', 'status': 'Generated'},
    {'candidate_idx': 11, 'type': 'NDA', 'trigger': 'Pre-Interview', 'status': 'Awaiting Signature'},
]

vct_data = [
    {'candidate_idx': 0, 'doc': 'Marksheet', 'extracted': 'CGPA: 8.2 | Backlogs: 0', 'confidence': 96, 'eligibility': 'Eligible', 'status': 'Verified', 'nm': True, 'dob': True, 'cgpa_ok': True, 'elig_ok': True, 'disc': ''},
    {'candidate_idx': 1, 'doc': 'Marksheet', 'extracted': 'CGPA: 7.8 | Backlogs: 0', 'confidence': 91, 'eligibility': 'Eligible', 'status': 'Pending Review', 'nm': True, 'dob': True, 'cgpa_ok': True, 'elig_ok': True, 'disc': ''},
    {'candidate_idx': 2, 'doc': 'Marksheet', 'extracted': 'CGPA: 6.9 | Backlogs: 1', 'confidence': 87, 'eligibility': 'Not Eligible', 'status': 'Flagged', 'nm': True, 'dob': False, 'cgpa_ok': False, 'elig_ok': False, 'disc': 'Resume CGPA: 7.5 - Marksheet CGPA: 6.9, DOB mismatch'},
    {'candidate_idx': 4, 'doc': 'Marksheet', 'extracted': 'CGPA: 7.5 | Backlogs: 0', 'confidence': 93, 'eligibility': 'Eligible', 'status': 'Verified', 'nm': True, 'dob': True, 'cgpa_ok': True, 'elig_ok': True, 'disc': ''},
    {'candidate_idx': 6, 'doc': 'Degree Certificate', 'extracted': 'CGPA: 7.2 | Backlogs: 0', 'confidence': 76, 'eligibility': 'Pending', 'status': 'Pending Review', 'nm': True, 'dob': False, 'cgpa_ok': True, 'elig_ok': False, 'disc': 'DOB pending verification'},
    {'candidate_idx': 7, 'doc': 'Marksheet', 'extracted': 'CGPA: 8.8 | Backlogs: 0', 'confidence': 97, 'eligibility': 'Eligible', 'status': 'Verified', 'nm': True, 'dob': True, 'cgpa_ok': True, 'elig_ok': True, 'disc': ''},
    {'candidate_idx': 8, 'doc': 'Marksheet', 'extracted': 'CGPA: 7.0 | Backlogs: 2', 'confidence': 60, 'eligibility': 'Not Eligible', 'status': 'Flagged', 'nm': True, 'dob': False, 'cgpa_ok': False, 'elig_ok': False, 'disc': 'OCR confidence low (60%), CGPA discrepancy, backlogs exceed limit'},
    {'candidate_idx': 10, 'doc': 'Marksheet', 'extracted': 'CGPA: 7.6 | Backlogs: 0', 'confidence': 88, 'eligibility': 'Eligible', 'status': 'Verified', 'nm': True, 'dob': True, 'cgpa_ok': True, 'elig_ok': True, 'disc': ''},
]

notifications_data = [
    {'type': 'applied', 'message': 'Rohan Mehta applied for Frontend Developer position', 'related_id': 6},
    {'type': 'vct', 'message': 'VCT verification required for Karan Joshi - records flagged', 'related_id': 8},
    {'type': 'interview', 'message': 'Interview with Rahul Sharma scheduled for 26 Jul at 10:00 AM', 'related_id': 0},
    {'type': 'document', 'message': 'Offer letter generated for Neha Gupta', 'related_id': 3},
    {'type': 'assessment', 'message': 'Aman Verma scored 91/100 in Python Coding Challenge', 'related_id': 2},
    {'type': 'status', 'message': 'Priya Singh moved to Assessment stage', 'related_id': 1},
    {'type': 'vct', 'message': '23 OCR records flagged - review required', 'related_id': 0},
    {'type': 'interview', 'message': '12 candidates awaiting eligibility review', 'related_id': 0},
]

def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(name='HR Admin', email='admin@recruitpro.com', role='Admin', avatar='HR')
        admin.set_password('admin123')
        db.session.add(admin)

        recruiter = User(name='Rekha Sharma', email='recruiter@recruitpro.com', role='Recruiter', avatar='RS')
        recruiter.set_password('recruiter123')
        db.session.add(recruiter)

        interviewer = User(name='Amit Kumar', email='interviewer@recruitpro.com', role='Interviewer', avatar='AK')
        interviewer.set_password('interviewer123')
        db.session.add(interviewer)

        candidates = []
        for cd in candidates_data:
            c = Candidate(
                name=cd['name'], email=cd['email'], phone=cd['phone'],
                position=cd['position'], experience_years=cd['exp'],
                skills=cd['skills'], education=cd['education'],
                college=cd['college'], degree=cd['degree'],
                graduation_year=cd['year'], cgpa=cd['cgpa'], backlogs=cd['backlogs'],
                source=cd['source'], status=cd['status'], stage=cd['stage'],
                verification_status=cd['verification'], eligibility=cd['eligibility'],
                ocr_confidence=cd['confidence'], location=cd['location'],
                avatar_color=cd['avatar'],
                applied_date=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(c)
            candidates.append(c)

        db.session.flush()

        for vd in vct_data:
            v = VCTRecord(
                candidate_id=candidates[vd['candidate_idx']].id,
                document_type=vd['doc'], extracted_data=vd['extracted'],
                ocr_confidence=vd['confidence'], eligibility=vd['eligibility'],
                verification_status=vd['status'],
                name_matched=vd['nm'], dob_matched=vd['dob'],
                cgpa_verified=vd['cgpa_ok'], eligibility_passed=vd['elig_ok'],
                discrepancy=vd['disc']
            )
            db.session.add(v)

        for iv in interviews_data:
            interview = Interview(
                candidate_id=candidates[iv['candidate_idx']].id,
                interviewer=iv['interviewer'],
                date=datetime.strptime(iv['date'], '%Y-%m-%d').date(),
                time=iv['time'], round_type=iv['round'],
                meet_link=iv['meet'], status=iv['status']
            )
            db.session.add(interview)

        for ad in assessments_data:
            a = Assessment(
                candidate_id=candidates[ad['candidate_idx']].id,
                name=ad['name'], type=ad['type'],
                score=ad['score'], max_score=100,
                technical_score=ad['tech'], problem_solving=ad['problem'],
                coding_score=ad['coding'], accuracy=ad['accuracy'],
                result=ad['result'], status=ad['status'],
                date=datetime.now() - timedelta(days=random.randint(1, 15))
            )
            db.session.add(a)

        for dd in documents_data:
            doc = Document(
                candidate_id=candidates[dd['candidate_idx']].id,
                type=dd['type'], triggered_by=dd['trigger'],
                status=dd['status'],
                generated_date=datetime.now() - timedelta(days=random.randint(1, 10))
            )
            db.session.add(doc)

        for nd in notifications_data:
            notif = Notification(
                type=nd['type'], message=nd['message'],
                related_id=nd['related_id'], is_read=False,
                created_at=datetime.now() - timedelta(hours=random.randint(1, 48))
            )
            db.session.add(notif)

        for i, c in enumerate(candidates):
            stage_idx = stages_order.index(c.stage) if c.stage in stages_order else 0
            for s in range(stage_idx + 1):
                event = TimelineEvent(
                    candidate_id=c.id,
                    event=f'Moved to {stages_order[s]}',
                    description=f'Candidate progressed to {stages_order[s]} stage',
                    stage=stages_order[s],
                    created_at=datetime.now() - timedelta(days=(stage_idx - s) * random.randint(2, 5) + 1)
                )
                db.session.add(event)

        db.session.commit()
        print(f'Seeded: {Candidate.query.count()} Candidates, {VCTRecord.query.count()} VCT, {Interview.query.count()} Interviews')
        print(f'{Assessment.query.count()} Assessments, {Document.query.count()} Documents, {Notification.query.count()} Notifications')

if __name__ == '__main__':
    seed()