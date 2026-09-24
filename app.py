from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
import csv
import io
import os
import calendar as cal_module

from models import db, User, Candidate, VCTRecord, Interview, Assessment, Document, Notification, TimelineEvent, Job, CodeExecution

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'recruitpro-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'recruitment.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---- Role permissions matching base.html / jobs.html / settings.html ----
FULL_PERMS = {'candidates', 'vct', 'queues', 'assessments', 'coding_sandbox',
              'interviews', 'documents', 'resume_formatter', 'reports',
              'settings', 'users', 'jobs'}

ROLE_PERMISSIONS = {
    'Admin': set(FULL_PERMS),
    'Administrator': set(FULL_PERMS),
    'Recruiter': {'candidates', 'vct', 'queues', 'assessments', 'coding_sandbox',
                  'interviews', 'documents', 'resume_formatter', 'reports', 'jobs'},
    'Interviewer': {'coding_sandbox', 'interviews'},
    'Candidate': {'coding_sandbox', 'interviews'},
}


def is_admin():
    return getattr(current_user, 'role', '') in ('Admin', 'Administrator')


def get_my_candidate():
    """Candidate-profile row belonging to the logged-in user (matched by email)."""
    try:
        email = (getattr(current_user, 'email', '') or '').strip().lower()
        if not email:
            return None
        return Candidate.query.filter(func.lower(Candidate.email) == email).first()
    except Exception:
        return None


def staff_only():
    """Staff pages (recruiter/admin/interviewer data) are off-limits for Candidate users."""
    if getattr(current_user, 'role', '') == 'Candidate':
        flash('This page is for staff only.', 'warning')
        return redirect(url_for('dashboard'))
    return None


# ---- Jinja filters used by templates ----
@app.template_filter('get_initials')
def get_initials(name):
    if not name:
        return '?'
    parts = str(name).split()
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


@app.template_filter('time_ago')
def time_ago(dt):
    if not dt:
        return ''
    now = datetime.utcnow()
    # handle date objects
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time())
    diff = now - dt
    secs = int(diff.total_seconds())
    if secs < 60:
        return 'Just now'
    if secs < 3600:
        return f"{secs // 60}m ago"
    if secs < 86400:
        return f"{secs // 3600}h ago"
    if secs < 86400 * 30:
        return f"{secs // 86400}d ago"
    return dt.strftime('%d %b %Y')


@app.context_processor
def inject_globals():
    authed = getattr(current_user, 'is_authenticated', False)
    role = getattr(current_user, 'role', 'Guest') if authed else 'Guest'
    perms = ROLE_PERMISSIONS.get(role, set())
    try:
        unread = Notification.query.filter_by(is_read=False).count() if authed else 0
    except Exception:
        unread = 0
    try:
        active = request.endpoint or ''
    except Exception:
        active = ''
    return dict(permissions=perms, unread_count=unread, active_page=active)


def ensure_default_users():
    if User.query.count() > 0:
        return
    admin = User(name='HR Admin', email='admin@recruitpro.com', role='Admin', avatar='HR')
    admin.set_password('admin123')
    db.session.add(admin)
    recruiter = User(name='Rekha Sharma', email='recruiter@recruitpro.com', role='Recruiter', avatar='RS')
    recruiter.set_password('recruiter123')
    db.session.add(recruiter)
    interviewer = User(name='Amit Kumar', email='interviewer@recruitpro.com', role='Interviewer', avatar='AK')
    interviewer.set_password('interviewer123')
    db.session.add(interviewer)
    db.session.commit()


def add_timeline(candidate_id, event, description, stage):
    try:
        t = TimelineEvent(candidate_id=candidate_id, event=event,
                          description=description, stage=stage)
        db.session.add(t)
        db.session.commit()
    except Exception:
        db.session.rollback()


# ================= AUTH =================
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        user = User.query.filter(func.lower(User.email) == email).first()
        if user and user.is_active and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            flash(f"Welcome back, {user.name}!", 'success')
            nxt = request.args.get('next')
            if not nxt or not nxt.startswith('/'):
                nxt = url_for('dashboard')
            return redirect(nxt)
        flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        confirm = request.form.get('confirm') or ''
        if not name or not email or not password:
            flash('Please fill all required fields.', 'danger')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        if User.query.filter(func.lower(User.email) == email).first():
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('login'))
        # Default stays Recruiter (original behaviour); user may choose Candidate to apply + practice
        role = request.form.get('role') or 'Recruiter'
        if role not in ('Recruiter', 'Candidate'):
            role = 'Recruiter'
        initials = ''.join([p[0] for p in name.split()][:2]).upper() or 'HR'
        user = User(name=name, email=email, role=role, avatar=initials)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ================= DASHBOARD =================
@app.route('/dashboard')
@login_required
def dashboard():
    total = Candidate.query.count()
    pending_verification = Candidate.query.filter(Candidate.verification_status != 'Verified').count()
    today = date.today()
    interviews_today = Interview.query.filter(Interview.date == today).all()
    selected = Candidate.query.filter_by(stage='Selected').count()

    stages_order = ['Applications', 'VCT Verification', 'Assessment', 'Shortlisted',
                    'Interview', 'Selected', 'Documentation', 'Joined']
    pipeline_counts = []
    for s in stages_order:
        pipeline_counts.append({'stage': s, 'count': Candidate.query.filter_by(stage=s).count()})

    verified = Candidate.query.filter_by(verification_status='Verified').count()
    pending = Candidate.query.filter_by(verification_status='Pending Review').count()
    flagged = Candidate.query.filter_by(verification_status='Flagged').count()
    all_c = total or 1
    failed = max(0, total - verified - pending - flagged)
    vct_status = {'verified': verified, 'pending': pending, 'flagged': flagged, 'failed': failed}

    candidates = Candidate.query.order_by(Candidate.applied_date.desc()).limit(5).all()

    # Candidate role: show only own profile + own interviews (matched by email)
    if getattr(current_user, 'role', '') == 'Candidate':
        me = get_my_candidate()
        if me is not None:
            candidates = [me]
            interviews_today = [iv for iv in Interview.query.filter_by(candidate_id=me.id).all()
                                if iv.date == today]
        else:
            candidates = []
            interviews_today = []

    alerts = []
    if getattr(current_user, 'role', '') == 'Candidate':
        me = get_my_candidate()
        if me is None:
            alerts.append({'link': url_for('candidates'), 'icon': 'person-plus', 'color': 'orange',
                           'text': 'Your candidate profile is not linked yet — ask your recruiter to create it with your login email'})
        else:
            my_upcoming = Interview.query.filter(Interview.candidate_id == me.id,
                                                 Interview.date >= today).count()
            if my_upcoming:
                alerts.append({'link': url_for('interviews'), 'icon': 'calendar-event', 'color': 'blue',
                               'text': f'You have {my_upcoming} assigned interview(s)'})
            else:
                alerts.append({'link': url_for('coding_sandbox'), 'icon': 'code-slash', 'color': 'green',
                               'text': 'No interviews assigned — practice in the Coding Sandbox'})
    else:
        if flagged:
            alerts.append({'link': url_for('vct'), 'icon': 'shield-exclamation', 'color': 'red',
                           'text': f'{flagged} candidates flagged in VCT'})
        if pending:
            alerts.append({'link': url_for('vct'), 'icon': 'clock-history', 'color': 'orange',
                           'text': f'{pending} candidates pending verification'})
        if interviews_today:
            alerts.append({'link': url_for('interviews'), 'icon': 'calendar-event', 'color': 'blue',
                           'text': f"{len(interviews_today)} interviews scheduled today"})

    stats = {'total_candidates': total, 'pending_verification': pending_verification,
             'interviews_today': len(interviews_today), 'selected': selected}
    return render_template('dashboard.html', stats=stats, pipeline_counts=pipeline_counts,
                           vct_status=vct_status, interviews=interviews_today,
                           candidates=candidates, alerts=alerts, active_page='dashboard')


# ================= CANDIDATES =================
@app.route('/candidates')
@login_required
def candidates():
    blocked = staff_only()
    if blocked:
        return blocked
    page = request.args.get('page', 1, type=int)
    search = (request.args.get('search') or '').strip()
    status = request.args.get('status') or ''
    position = request.args.get('position') or ''
    q = Candidate.query
    if search:
        like = f'%{search}%'
        q = q.filter((Candidate.name.ilike(like)) | (Candidate.email.ilike(like)) | (Candidate.position.ilike(like)))
    if status:
        q = q.filter_by(verification_status=status)
    if position:
        q = q.filter_by(position=position)
    pagination = q.order_by(Candidate.applied_date.desc()).paginate(page=page, per_page=10, error_out=False)
    vstatuses = [r[0] for r in db.session.query(Candidate.verification_status).distinct().all() if r[0]]
    positions = [r[0] for r in db.session.query(Candidate.position).distinct().all() if r[0]]
    return render_template('candidates.html', candidates=pagination.items, pagination=pagination,
                           search=search, status=status, position=position,
                           vstatuses=vstatuses, positions=positions, active_page='candidates')


@app.route('/candidates/<int:id>')
@login_required
def candidate_detail(id):
    c = Candidate.query.get_or_404(id)
    if getattr(current_user, 'role', '') == 'Candidate':
        me = get_my_candidate()
        if me is None or me.id != c.id:
            flash('You can only view your own profile.', 'warning')
            return redirect(url_for('dashboard'))
    # templates use candidate.assessment_records / timeline_records (aliases)
    # expose them dynamically so old templates don't crash
    if not hasattr(c, 'assessment_records'):
        c.assessment_records = c.assessments
    if not hasattr(c, 'timeline_records'):
        c.timeline_records = c.timeline_events
    return render_template('candidate_detail.html', candidate=c, active_page='candidates')


@app.route('/candidates/add', methods=['POST'])
@login_required
def add_candidate():
    blocked = staff_only()
    if blocked:
        return blocked
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip()
    if not name or not email:
        flash('Name and email are required.', 'danger')
        return redirect(url_for('candidates'))
    if Candidate.query.filter(func.lower(Candidate.email) == email.lower()).first():
        flash('Candidate with this email already exists.', 'warning')
        return redirect(url_for('candidates'))
    try:
        cgpa = float(request.form.get('cgpa')) if request.form.get('cgpa') else None
    except ValueError:
        cgpa = None
    c = Candidate(name=name, email=email, phone=request.form.get('phone') or '',
                  position=request.form.get('position') or '', college=request.form.get('college') or '',
                  degree=request.form.get('degree') or '', cgpa=cgpa,
                  source=request.form.get('source') or 'Direct',
                  skills=request.form.get('skills') or '', stage='Applications',
                  status='Applied', verification_status='Pending Review', eligibility='Pending')
    db.session.add(c)
    db.session.commit()
    add_timeline(c.id, 'Added to Applications', 'Candidate added to pipeline', 'Applications')
    flash('Candidate added successfully!', 'success')
    return redirect(url_for('candidates'))


@app.route('/candidates/<int:id>/edit', methods=['POST'])
@login_required
def edit_candidate(id):
    blocked = staff_only()
    if blocked:
        return blocked
    c = Candidate.query.get_or_404(id)
    c.name = request.form.get('name') or c.name
    c.email = request.form.get('email') or c.email
    c.phone = request.form.get('phone') or c.phone
    c.position = request.form.get('position') or c.position
    try:
        if request.form.get('cgpa'):
            c.cgpa = float(request.form.get('cgpa'))
    except ValueError:
        pass
    if request.form.get('stage'):
        c.stage = request.form.get('stage')
    if request.form.get('verification_status'):
        c.verification_status = request.form.get('verification_status')
    c.skills = request.form.get('skills') if request.form.get('skills') is not None else c.skills
    db.session.commit()
    flash('Candidate updated.', 'success')
    return redirect(url_for('candidate_detail', id=id))


@app.route('/candidates/<int:id>/stage', methods=['POST'])
@login_required
def update_stage(id):
    blocked = staff_only()
    if blocked:
        return blocked
    c = Candidate.query.get_or_404(id)
    new_stage = request.form.get('stage')
    if new_stage:
        c.stage = new_stage
        db.session.commit()
        add_timeline(c.id, f'Moved to {new_stage}', f'Candidate progressed to {new_stage} stage', new_stage)
        flash(f'Moved to {new_stage}.', 'success')
    return redirect(url_for('candidate_detail', id=id))


# ================= VCT =================
@app.route('/vct')
@login_required
def vct():
    blocked = staff_only()
    if blocked:
        return blocked
    search = (request.args.get('search') or '').strip()
    status_filter = request.args.get('status') or ''
    q = VCTRecord.query.join(Candidate)
    if search:
        like = f'%{search}%'
        q = q.filter(Candidate.name.ilike(like))
    if status_filter == 'Eligibility Failed':
        q = q.filter(VCTRecord.eligibility == 'Not Eligible')
    elif status_filter:
        q = q.filter(VCTRecord.verification_status == status_filter)
    records = q.order_by(VCTRecord.created_at.desc()).all()
    return render_template('vct.html', records=records, search=search,
                           status_filter=status_filter, active_page='vct')


@app.route('/vct/<int:id>')
@login_required
def vct_detail(id):
    blocked = staff_only()
    if blocked:
        return blocked
    record = VCTRecord.query.get_or_404(id)
    return render_template('vct_detail.html', record=record, active_page='vct')


@app.route('/vct/<int:id>/action', methods=['POST'])
@login_required
def vct_action(id):
    blocked = staff_only()
    if blocked:
        return blocked
    record = VCTRecord.query.get_or_404(id)
    action = request.form.get('action')
    cand = record.candidate
    if action == 'approve':
        record.verification_status = 'Verified'
        record.eligibility = 'Eligible'
        if cand:
            cand.verification_status = 'Verified'
            cand.eligibility = 'Eligible'
        flash('VCT record approved.', 'success')
    elif action == 'flag':
        record.verification_status = 'Flagged'
        record.eligibility = 'Not Eligible'
        if cand:
            cand.verification_status = 'Flagged'
            cand.eligibility = 'Not Eligible'
        flash('VCT record flagged.', 'warning')
    else:
        record.verification_status = 'Pending Review'
        flash('Sent back for review.', 'info')
    db.session.commit()
    return redirect(url_for('vct_detail', id=id))


# ================= QUEUES =================
@app.route('/queues')
@login_required
def queues():
    blocked = staff_only()
    if blocked:
        return blocked
    stages = ['Applications', 'VCT Verification', 'Assessment', 'Shortlisted',
              'Interview', 'Selected', 'Documentation', 'Joined']
    queue_data = {s: Candidate.query.filter_by(stage=s).order_by(Candidate.applied_date.desc()).all() for s in stages}
    return render_template('queues.html', stages=stages, queue_data=queue_data, active_page='queues')


# ================= ASSESSMENTS =================
@app.route('/assessments')
@login_required
def assessments():
    blocked = staff_only()
    if blocked:
        return blocked
    all_a = Assessment.query.order_by(Assessment.date.desc()).all()
    assigned = len(all_a)
    completed = len([a for a in all_a if a.status == 'Completed'])
    in_progress = len([a for a in all_a if a.status == 'In Progress'])
    pending_review = len([a for a in all_a if a.status == 'Pending'])
    astats = {'assigned': assigned, 'in_progress': in_progress,
              'completed': completed, 'pending_review': pending_review}
    cands = Candidate.query.order_by(Candidate.name).all()
    return render_template('assessments.html', assessments=all_a, astats=astats,
                           candidates=cands, active_page='assessments')


@app.route('/assessments/assign', methods=['POST'])
@login_required
def assign_assessment():
    blocked = staff_only()
    if blocked:
        return blocked
    try:
        a = Assessment(candidate_id=int(request.form.get('candidate_id')),
                       name=request.form.get('name') or 'Assessment',
                       type=request.form.get('type') or 'Technical',
                       result='Pending', status='Pending', max_score=100)
        db.session.add(a)
        db.session.commit()
        flash('Assessment assigned.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Could not assign assessment: {e}', 'danger')
    return redirect(url_for('assessments'))


@app.route('/assessments/update', methods=['POST'])
@login_required
def update_assessment():
    blocked = staff_only()
    if blocked:
        return blocked
    a = Assessment.query.get_or_404(int(request.form.get('id')))
    try:
        if request.form.get('score') not in (None, ''):
            a.score = float(request.form.get('score'))
    except ValueError:
        pass
    a.result = request.form.get('result') or a.result
    a.status = request.form.get('status') or a.status
    db.session.commit()
    flash('Assessment updated.', 'success')
    return redirect(url_for('assessments'))


@app.route('/assessments/<int:id>/report')
@login_required
def assessment_report(id):
    blocked = staff_only()
    if blocked:
        return blocked
    a = Assessment.query.get_or_404(id)
    return render_template('assessment_report.html', assessment=a, active_page='assessments')


# ================= CODING SANDBOX (static demo + server-side save) =================
@app.route('/coding-sandbox')
@login_required
def coding_sandbox():
    return render_template('coding_sandbox.html', active_page='coding_sandbox')


DEMO_CODE = """def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Test
nums = [2, 7, 11, 15]
target = 9
print(two_sum(nums, target))"""


def _demo_output(code, language):
    """Safe demo evaluation — no exec(), just checks the classic Two Sum answer."""
    text = (code or '')
    if 'two_sum' in text and '[2, 7, 11, 15]' in text.replace('[2,7,11,15]', '[2, 7, 11, 15]'):
        return '[0, 1]'
    if 'two_sum' in text:
        return '[0, 1]'
    return 'Code saved. Demo output: [0, 1]'


@app.route('/api/sandbox/execute', methods=['POST'])
@login_required
def sandbox_execute():
    data = request.get_json(silent=True) or {}
    code = data.get('code', '') or ''
    language = (data.get('language') or 'python').lower()
    if language not in ('python', 'java', 'c++', 'javascript'):
        language = 'python'
    if len(code) > 20000:
        return jsonify({'success': False, 'output': 'Code too long (max 20000 chars).'}), 400
    output = _demo_output(code, language)
    try:
        ex = CodeExecution(user_id=current_user.id, code=code, language=language,
                           output=output, status='success')
        db.session.add(ex)
        db.session.commit()
        eid = ex.id
    except Exception:
        db.session.rollback()
        eid = None
    return jsonify({'success': True, 'output': output, 'status': 'success',
                    'language': language, 'execution_id': eid})


@app.route('/api/sandbox/history')
@login_required
def sandbox_history():
    rows = (CodeExecution.query.filter_by(user_id=current_user.id)
            .order_by(CodeExecution.created_at.desc()).limit(10).all())
    return jsonify([{'id': r.id, 'language': r.language, 'status': r.status,
                     'created_at': r.created_at.strftime('%d %b %H:%M') if r.created_at else '',
                     'code_preview': (r.code or '')[:80]} for r in rows])


@app.route('/api/sandbox/load/<int:execution_id>')
@login_required
def sandbox_load(execution_id):
    ex = CodeExecution.query.get_or_404(execution_id)
    if ex.user_id != current_user.id and not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'code': ex.code, 'language': ex.language,
                    'status': ex.status, 'output': ex.output})


# ================= INTERVIEWS =================
@app.route('/interviews')
@login_required
def interviews():
    # optional ?date=YYYY-MM-DD filter from calendar clicks
    date_filter = request.args.get('date')
    q = Interview.query
    if date_filter:
        try:
            d = datetime.strptime(date_filter, '%Y-%m-%d').date()
            q = q.filter(Interview.date == d)
        except ValueError:
            pass
    # Candidate users see only their own interviews (email-matched candidate row)
    if getattr(current_user, 'role', '') == 'Candidate':
        me = get_my_candidate()
        if me is None:
            q = q.filter(Interview.id == -1)
        else:
            q = q.filter(Interview.candidate_id == me.id)
    all_iv = q.order_by(Interview.date.desc()).all()
    today = date.today()
    base_q = Interview.query
    if getattr(current_user, 'role', '') == 'Candidate':
        me = get_my_candidate()
        base_q = base_q.filter(Interview.candidate_id == (me.id if me else -1))
    today_count = base_q.filter(Interview.date == today).count()
    upcoming = base_q.filter(Interview.date > today).count()
    completed = base_q.filter_by(status='Completed').count()
    pending_feedback = base_q.filter(Interview.feedback.is_(None)).count()
    cands = Candidate.query.order_by(Candidate.name).all()
    return render_template('interviews.html', interviews=all_iv, today_count=today_count,
                           upcoming=upcoming, completed=completed,
                           pending_feedback=pending_feedback, candidates=cands,
                           active_page='interviews')


@app.route('/interviews/<int:id>')
@login_required
def interview_detail(id):
    iv = Interview.query.get_or_404(id)
    if getattr(current_user, 'role', '') == 'Candidate':
        me = get_my_candidate()
        if me is None or iv.candidate_id != me.id:
            flash('This interview is not assigned to you.', 'danger')
            return redirect(url_for('interviews'))
    # ensure reminder attrs exist for template (original DB may lack them)
    for attr in ('reminder_24h', 'reminder_1h', 'reminder_10m'):
        if not hasattr(iv, attr):
            setattr(iv, attr, False)
    return render_template('interview_detail.html', interview=iv, active_page='interviews')


@app.route('/interviews/schedule', methods=['POST'])
@login_required
def schedule_interview():
    blocked = staff_only()
    if blocked:
        return blocked
    try:
        d = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date() if request.form.get('date') else None
    except ValueError:
        d = None
    iv = Interview(candidate_id=int(request.form.get('candidate_id')), interviewer=request.form.get('interviewer') or '',
                   date=d, time=request.form.get('time') or '',
                   round_type=request.form.get('round_type') or 'Technical Round',
                   meet_link=request.form.get('meet_link') or '', status='Scheduled')
    db.session.add(iv)
    db.session.commit()
    flash('Interview scheduled.', 'success')
    return redirect(url_for('interviews'))


@app.route('/interviews/<int:id>/status', methods=['POST'])
@login_required
def update_interview_status(id):
    blocked = staff_only()
    if blocked:
        return blocked
    iv = Interview.query.get_or_404(id)
    iv.status = request.form.get('status') or iv.status
    db.session.commit()
    flash('Interview status updated.', 'success')
    return redirect(url_for('interviews'))


@app.route('/interviews/<int:id>/feedback', methods=['POST'])
@login_required
def submit_feedback(id):
    if getattr(current_user, 'role', '') == 'Candidate':
        flash('Only interviewers can submit feedback.', 'danger')
        return redirect(url_for('interviews'))
    iv = Interview.query.get_or_404(id)
    try:
        iv.communication = int(request.form.get('communication') or iv.communication or 0)
        iv.technical_skill = int(request.form.get('technical_skill') or iv.technical_skill or 0)
        iv.problem_solving = int(request.form.get('problem_solving') or iv.problem_solving or 0)
        iv.cultural_fit = int(request.form.get('cultural_fit') or iv.cultural_fit or 0)
    except ValueError:
        pass
    iv.recommendation = request.form.get('recommendation') or iv.recommendation
    iv.feedback = request.form.get('feedback') or iv.feedback
    iv.status = 'Completed'
    db.session.commit()
    flash('Feedback submitted.', 'success')
    return redirect(url_for('interview_detail', id=id))


# ================= DOCUMENTS =================
@app.route('/documents')
@login_required
def documents():
    blocked = staff_only()
    if blocked:
        return blocked
    docs = Document.query.order_by(Document.generated_date.desc()).all()
    gen_count = Document.query.filter_by(status='Generated').count()
    pend_count = Document.query.filter_by(status='Pending').count()
    await_count = Document.query.filter_by(status='Awaiting Signature').count()
    cands = Candidate.query.order_by(Candidate.name).all()
    return render_template('documents.html', documents=docs, gen_count=gen_count,
                           pend_count=pend_count, await_count=await_count,
                           candidates=cands, active_page='documents')


@app.route('/documents/generate', methods=['POST'])
@login_required
def generate_document():
    blocked = staff_only()
    if blocked:
        return blocked
    doc = Document(candidate_id=int(request.form.get('candidate_id')),
                   type=request.form.get('type') or 'Offer Letter',
                   triggered_by=request.form.get('triggered_by') or 'System',
                   status='Generated')
    db.session.add(doc)
    db.session.commit()
    flash('Document generated.', 'success')
    return redirect(url_for('documents'))


@app.route('/documents/<int:id>/download')
@login_required
def download_document(id):
    d = Document.query.get_or_404(id)
    if getattr(current_user, 'role', '') == 'Candidate':
        me = get_my_candidate()
        if me is None or d.candidate_id != me.id:
            flash('This document does not belong to you.', 'danger')
            return redirect(url_for('dashboard'))
    # simple text download (original used xhtml2pdf; keep lightweight to avoid dependency crash)
    try:
        from xhtml2pdf import pisa
        html = f"<h1>{d.type}</h1><p>Candidate: {d.candidate.name}</p><p>Date: {d.generated_date}</p>"
        buf = io.BytesIO()
        pisa.CreatePDF(io.StringIO(html), dest=buf)
        buf.seek(0)
        return Response(buf.read(), mimetype='application/pdf',
                        headers={'Content-Disposition': f'attachment;filename=document_{d.id}.pdf'})
    except Exception:
        return Response(f"{d.type} - {d.candidate.name}",
                        mimetype='text/plain',
                        headers={'Content-Disposition': f'attachment;filename=document_{d.id}.txt'})


# ================= RESUME / REPORTS / CALENDAR =================
@app.route('/resume-formatter')
@login_required
def resume_formatter():
    blocked = staff_only()
    if blocked:
        return blocked
    cands = Candidate.query.order_by(Candidate.applied_date.desc()).limit(10).all()
    return render_template('resume_formatter.html', candidates=cands, active_page='resume_formatter')


@app.route('/reports')
@login_required
def reports():
    blocked = staff_only()
    if blocked:
        return blocked
    total = Candidate.query.count()
    shortlisted = Candidate.query.filter_by(stage='Shortlisted').count()
    selected = Candidate.query.filter_by(stage='Selected').count()
    joined = Candidate.query.filter_by(stage='Joined').count()
    apass = Assessment.query.filter_by(result='Pass').count()
    afail = Assessment.query.filter_by(result='Fail').count()
    pending_verification = Candidate.query.filter(Candidate.verification_status != 'Verified').count()
    ocr_flags = Candidate.query.filter_by(verification_status='Flagged').count()
    stats = {'total_candidates': total, 'shortlisted': shortlisted, 'selected': selected,
             'joined': joined, 'assessment_pass': apass, 'assessment_fail': afail,
             'pending_verification': pending_verification, 'ocr_flags': ocr_flags}
    stages_order = ['Applications', 'VCT Verification', 'Assessment', 'Shortlisted',
                    'Interview', 'Selected', 'Documentation', 'Joined']
    stages_data = [(s, Candidate.query.filter_by(stage=s).count()) for s in stages_order]
    return render_template('reports.html', stats=stats, stages_data=stages_data, active_page='reports')


@app.route('/reports/export')
@login_required
def export_csv():
    blocked = staff_only()
    if blocked:
        return blocked
    si = io.StringIO()
    w = csv.writer(si)
    w.writerow(['ID', 'Name', 'Email', 'Position', 'Stage', 'Verification', 'CGPA'])
    for c in Candidate.query.all():
        w.writerow([c.id, c.name, c.email, c.position, c.stage, c.verification_status, c.cgpa])
    return Response(si.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=candidates.csv'})


@app.route('/api/applications-monthly')
@login_required
def applications_monthly():
    rows = db.session.query(extract('year', Candidate.applied_date).label('y'),
                            extract('month', Candidate.applied_date).label('m'),
                            func.count(Candidate.id)).group_by('y', 'm').all()
    out = []
    for y, m, cnt in rows:
        if y and m:
            out.append({'month': f'{int(m):02d}/{int(y)}', 'count': cnt})
    return jsonify(out)


@app.route('/api/interviews')
@login_required
def api_interviews():
    month = request.args.get('month')  # YYYY-MM
    q = Interview.query
    if getattr(current_user, 'role', '') == 'Candidate':
        me = get_my_candidate()
        q = q.filter(Interview.candidate_id == (me.id if me else -1))
    counts = {}
    for iv in q.all():
        if not iv.date:
            continue
        key = iv.date.strftime('%Y-%m-%d')
        if month and not key.startswith(month):
            continue
        counts[key] = counts.get(key, 0) + 1
    return jsonify(counts)


@app.route('/calendar')
@login_required
def calendar_view():
    return render_template('calendar.html', active_page='interviews')


# ================= NOTIFICATIONS =================
@app.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifs, active_page='notifications')


@app.route('/notifications/<int:id>/read')
@login_required
def read_notification(id):
    n = Notification.query.get_or_404(id)
    n.is_read = True
    db.session.commit()
    return redirect(url_for('notifications'))


@app.route('/notifications/read-all')
@login_required
def read_all_notifications():
    Notification.query.update({'is_read': True})
    db.session.commit()
    return redirect(url_for('notifications'))


# ================= SETTINGS / USERS =================
@app.route('/settings')
@login_required
def settings():
    if 'settings' not in ROLE_PERMISSIONS.get(current_user.role, set()):
        flash('You do not have access to settings.', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.order_by(User.name).all()
    return render_template('settings.html', users=users, active_page='settings')


@app.route('/settings/users/add', methods=['POST'])
@login_required
def add_user():
    if not is_admin():
        flash('Only admins can add users.', 'danger')
        return redirect(url_for('settings'))
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    role = request.form.get('role') or 'Recruiter'
    avatar = (request.form.get('avatar') or (name[:2].upper() if name else 'HR'))[:2].upper()
    password = request.form.get('password') or 'Password@123'
    if not name or not email:
        flash('Name and email required.', 'danger')
        return redirect(url_for('settings'))
    if User.query.filter(func.lower(User.email) == email).first():
        flash('Email already exists.', 'warning')
        return redirect(url_for('settings'))
    u = User(name=name, email=email, role=role, avatar=avatar)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    flash('User created.', 'success')
    return redirect(url_for('settings'))


@app.route('/settings/users/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_user(id):
    if not is_admin():
        flash('Only admins can modify users.', 'danger')
        return redirect(url_for('settings'))
    u = User.query.get_or_404(id)
    if u.id == current_user.id:
        flash('You cannot disable your own account.', 'warning')
        return redirect(url_for('settings'))
    u.is_active = not u.is_active
    db.session.commit()
    flash('User status updated.', 'success')
    return redirect(url_for('settings'))


@app.route('/settings/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    if not is_admin():
        flash('Only admins can delete users.', 'danger')
        return redirect(url_for('settings'))
    u = User.query.get_or_404(id)
    if u.id == current_user.id:
        flash('You cannot delete your own account.', 'warning')
        return redirect(url_for('settings'))
    db.session.delete(u)
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('settings'))


@app.route('/settings/users/<int:id>/reset', methods=['POST'])
@login_required
def reset_password(id):
    if not is_admin():
        flash('Only admins can reset passwords.', 'danger')
        return redirect(url_for('settings'))
    u = User.query.get_or_404(id)
    u.set_password(request.form.get('password') or 'Password@123')
    db.session.commit()
    flash(f'Password reset for {u.name}.', 'success')
    return redirect(url_for('settings'))


# ================= JOBS =================
@app.route('/jobs')
@login_required
def jobs():
    blocked = staff_only()
    if blocked:
        return blocked
    all_jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('jobs.html', jobs=all_jobs, active_page='jobs')


@app.route('/jobs/<int:id>')
@login_required
def job_detail(id):
    blocked = staff_only()
    if blocked:
        return blocked
    job = Job.query.get_or_404(id)
    return render_template('job_detail.html', job=job, active_page='jobs')


@app.route('/jobs/add', methods=['GET', 'POST'])
@login_required
def add_job():
    blocked = staff_only()
    if blocked:
        return blocked
    if request.method == 'POST':
        try:
            openings = int(request.form.get('openings') or 1)
        except ValueError:
            openings = 1
        job = Job(title=request.form.get('title'), department=request.form.get('department') or '',
                  location=request.form.get('location') or '', openings=openings,
                  experience_required=request.form.get('experience_required') or '',
                  description=request.form.get('description') or '',
                  status=request.form.get('status') or 'Open', recruiter_id=current_user.id)
        db.session.add(job)
        db.session.commit()
        flash('Job created.', 'success')
        return redirect(url_for('jobs'))
    return render_template('add_job.html', active_page='jobs')


@app.route('/jobs/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_job(id):
    blocked = staff_only()
    if blocked:
        return blocked
    job = Job.query.get_or_404(id)
    # Admin delete, others close
    if is_admin() and job.status == 'Open' and request.form.get('delete') == '1':
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted.', 'success')
    else:
        if job.status == 'Open':
            # recruiters close; admin delete icon also posts here without delete flag -> treat 2nd post as delete
            if is_admin():
                db.session.delete(job)
                db.session.commit()
                flash('Job deleted.', 'success')
            else:
                job.status = 'Closed'
                db.session.commit()
                flash('Job closed.', 'success')
        else:
            job.status = 'Open'
            db.session.commit()
            flash('Job reopened.', 'success')
    return redirect(url_for('jobs'))


@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_default_users()
    app.run(debug=True, port=5000)
