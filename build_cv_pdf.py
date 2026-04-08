"""
Rebuild Fahad's CV with Liberation Sans (metric-compatible Arial replacement).
Font sizes matched to original PDF:
  - Name heading: ~20pt
  - Section headings: ~10pt bold
  - Contact / right-col dates: ~9pt
  - Body / bullets: ~9.8pt
  - Arrow ↗ superscript: ~8pt
"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos

WS = '/data/data/com.termux/files/home/.openclaw/workspace/'

class CV(FPDF):
    def header(self): pass
    def footer(self): pass

    def setup_fonts(self):
        self.add_font('ls',  '',  WS + 'LiberationSans-Regular.ttf')
        self.add_font('ls',  'B', WS + 'LiberationSans-Bold.ttf')
        self.add_font('ls',  'I', WS + 'LiberationSans-Italic.ttf')
        self.add_font('ls',  'BI',WS + 'LiberationSans-BoldItalic.ttf')
        # DejaVuSans as fallback for glyphs missing in LiberationSans (e.g. ↗)
        self.add_font('dv',  '',  WS + 'DejaVuSans.ttf')
        self.add_font('dv',  'B', WS + 'DejaVuSans-Bold.ttf')
        self.set_fallback_fonts(['dv'], exact_match=False)

    # ---- font helpers ----
    def rg(self, sz=9.8): self.set_font('ls','',sz);  self.set_text_color(0,0,0)
    def bd(self, sz=9.8): self.set_font('ls','B',sz); self.set_text_color(0,0,0)
    def it(self, sz=9.8): self.set_font('ls','I',sz); self.set_text_color(0,0,0)
    def gray(self):       self.set_text_color(80,80,80)
    def blue(self):       self.set_text_color(17,85,204)
    def black(self):      self.set_text_color(0,0,0)

    def sw(self, text, sz=9.8, style=''):
        """string width helper"""
        self.set_font('ls', style, sz)
        return self.get_string_width(text)

    # ---- building blocks ----
    def section_heading(self, text):
        self.ln(3.5)
        self.bd(10)
        self.cell(0, 5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(0,0,0)
        self.set_line_width(0.25)
        self.line(self.l_margin, self.get_y(), self.l_margin + self.epw, self.get_y())
        self.ln(2)

    def linked_cell(self, text, url, sz=9.8, style='', color='blue'):
        self.set_font('ls', style, sz)
        if color == 'blue': self.blue()
        else: self.black()
        w = self.get_string_width(text)
        x, y = self.get_x(), self.get_y()
        self.cell(w, 5, text)
        self.link(x, y, w, 5, url)
        self.black()

    def arrow(self, url, sz=8):
        """inline ↗ arrow linked"""
        self.set_font('ls', '', sz)
        self.blue()
        w = self.get_string_width(' ↗')
        x, y = self.get_x(), self.get_y()
        self.cell(w, 5, ' ↗')
        self.link(x, y, w, 5, url)
        self.black()

    def right_gray(self, text, sz=9):
        """right-aligned gray text on current line"""
        self.set_font('ls', '', sz)
        self.gray()
        w = self.get_string_width(text)
        # move to right edge
        self.set_x(self.l_margin + self.epw - w)
        self.cell(w, 5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.black()

    def two_col(self, left_fn, right_text, right_sz=9, line_h=5):
        """
        Draw right-aligned gray text first, then go back and draw left content.
        left_fn: callable that draws the left part (must stay within left_max_w)
        right_text: right-aligned gray string
        """
        y_start = self.get_y()
        # 1) measure right column
        self.set_font('ls', '', right_sz)
        rw = self.get_string_width(right_text)
        # 2) draw right column at far right
        self.set_xy(self.l_margin + self.epw - rw, y_start)
        self.gray()
        self.set_font('ls', '', right_sz)
        self.cell(rw, line_h, right_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.black()
        # 3) go back to y_start and draw left content (won't exceed right boundary)
        self.set_xy(self.l_margin, y_start)
        left_fn()
        # 4) ensure we're on the next line
        if self.get_y() == y_start:
            self.ln(line_h)

    def body_wrap(self, text, indent=5, sz=9.8):
        self.rg(sz)
        self.set_x(self.l_margin + indent)
        self.multi_cell(self.epw - indent, 4.8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def bullet_item(self, text, indent=5, sz=9.8):
        self.rg(sz)
        self.set_x(self.l_margin + indent)
        self.multi_cell(self.epw - indent, 4.8, '• ' + text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def project_entry(self, title, desc, url=None):
        # Title line (bold + optional arrow link)
        self.bd(9.8)
        tw = self.get_string_width(title + ' ')
        x0, y0 = self.get_x(), self.get_y()
        self.cell(tw, 5, title + ' ')
        if url:
            self.arrow(url, sz=8)
        self.ln()
        # Description
        self.body_wrap(desc, indent=0)
        self.ln(1)

    def skill_line(self, label, value, sz=9.8):
        self.bd(sz)
        lw = self.get_string_width(label + '  ')
        self.cell(lw, 5, label + '  ')
        self.rg(sz)
        self.multi_cell(self.epw - lw, 5, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def award_line(self, title, detail, url=None):
        self.bd(9.8)
        prefix = '• '
        pw = self.get_string_width(prefix)
        self.cell(pw, 5, prefix)
        if url:
            self.linked_cell(title, url, sz=9.8, style='B')
        else:
            self.cell(self.get_string_width(title), 5, title)
        self.rg(9.8)
        self.multi_cell(self.epw - pw - self.get_string_width(title), 5, '  ' + detail,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def cert_line(self, title, detail):
        self.bd(9.8)
        prefix = '• '
        pw = self.get_string_width(prefix)
        tw = self.get_string_width(title)
        self.cell(pw, 5, prefix)
        self.cell(tw, 5, title)
        self.rg(9.8)
        self.multi_cell(self.epw - pw - tw, 5, '  ' + detail,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# ─────────────────────────────────────────────────────────────────────────────
doc = CV(format='A4')
doc.set_margins(18, 15, 18)
doc.set_auto_page_break(True, 15)
doc.setup_fonts()
doc.add_page()

# ── HEADER ───────────────────────────────────────────────────────────────────
doc.bd(20)
doc.cell(0, 10, 'Muhammad Fahad Imdad', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# Contact line — centred, with individual links
contact = [
    ('+92 314 7800991',                          'tel:+923147800991'),
    ('   |   ',                                   None),
    ('fahadimdad966@gmail.com',                  'mailto:fahadimdad966@gmail.com'),
    ('   |   ',                                   None),
    ('linkedin.com/in/muhammadfahadimdad',        'https://linkedin.com/in/muhammadfahadimdad'),
    (' ↗',                                        'https://linkedin.com/in/muhammadfahadimdad'),
    ('   |   ',                                   None),
    ('fahadimdad.com',                            'https://fahadimdad.com/'),
    (' ↗',                                        'https://fahadimdad.com/'),
]
doc.set_font('ls', '', 9)
total_w = sum(doc.get_string_width(t) for t, _ in contact)
doc.set_x(doc.l_margin + (doc.epw - total_w) / 2)
for text, url in contact:
    w = doc.get_string_width(text)
    if url:
        doc.blue()
        x, y = doc.get_x(), doc.get_y()
        doc.cell(w, 5, text)
        doc.link(x, y, w, 5, url)
        doc.black()
    else:
        doc.gray()
        doc.cell(w, 5, text)
        doc.black()
doc.ln()
doc.ln(2)

def row(doc, left_fn, right_text, right_sz=9, h=5):
    """Draw right-aligned gray text, then left content on the same line."""
    y = doc.get_y()
    doc.set_font('ls', '', right_sz)
    rw = doc.get_string_width(right_text)
    # right side
    doc.set_xy(doc.l_margin + doc.epw - rw, y)
    doc.gray(); doc.set_font('ls', '', right_sz)
    doc.cell(rw, h, right_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    doc.black()
    # left side
    doc.set_xy(doc.l_margin, y)
    left_fn(doc.epw - rw)  # pass available width
    if doc.get_y() == y:
        doc.ln(h)

# ── EDUCATION ────────────────────────────────────────────────────────────────
doc.section_heading('EDUCATION')

row(doc,
    lambda w: (doc.bd(9.8), doc.cell(doc.get_string_width('Salim Habib University '), 5, 'Salim Habib University '), doc.arrow('https://shu.edu.pk/')),
    'Karachi, Pakistan')
row(doc,
    lambda w: (doc.rg(9.8), doc.cell(w, 5, 'B.S. in Computer Science – CGPA 3.68/4.0   |   Gold Medalist')),
    'March 2021 – May 2025')

doc.ln(1)

row(doc,
    lambda w: (doc.bd(9.8), doc.cell(doc.get_string_width('Private'), 5, 'Private')),
    'Karachi, Pakistan')
row(doc,
    lambda w: (doc.rg(9.8), doc.cell(w, 5, 'GCE AS & A Level')),
    'July 2019 – Nov 2020')

doc.ln(2)

# ── PROJECTS ─────────────────────────────────────────────────────────────────
doc.section_heading('PROJECTS')

projects = [
    ('Robotic Arm via LLMs',
     'Speech-controlled robotic arm simulator using LLMs, speech recognition, and forward kinematics for real-time 3D motion.',
     'https://www.fahadimdad.com/projects/ai-robotics/robotics-embodied-ai-systems'),
    ('Robotic Arm via Computer Vision',
     'Hand-tracking robotic arm using MediaPipe and OpenCV with gesture-based control and real-time visualization.',
     'https://www.fahadimdad.com/projects/ai-robotics/robotics-embodied-ai-systems'),
    ('AR Circuit Simulator',
     'AR-based electronic circuit simulator using Unity and ARCore; integrated AI model for hardware detection and virtual component overlay.',
     'https://www.fahadimdad.com/projects/immersive-tech-arvrxr'),
    ('AI-Powered Conversational Shopping Platform',
     'Full-stack e-commerce platform using React, FastAPI and Azure OpenAI with multi-agentic LLMs, LangChain, vector-based RAG, and context-aware recommendations.',
     'https://www.fahadimdad.com/projects/ai-robotics/conversational-agents-recommender-systems'),
    ('Medical Claim App',
     'AI-powered app using Azure OCR and Azure OpenAI to extract and validate medical prescriptions against company health policy.',
     'https://www.fahadimdad.com/projects/ai-robotics/multimodal-generative-ai-systems'),
    ('Brain Tumor Classification',
     'Deep learning model to classify brain tumors from MRI scans. Presented at Sindh HEC Research Showcase 2024.',
     None),
    ('Visual Defect Detection',
     'ResNet50-based classifier trained on MVTec AD dataset with a Streamlit UI for industrial defect recognition.',
     'https://www.fahadimdad.com/projects/ai-robotics/computer-vision-real-time-ai'),
    ('Vehicle Counting & Speed Detection (YOLOv8 & YOLOv11)',
     'Lane-wise vehicle counting (YOLOv8) and speed estimation (YOLOv11) with real-time vehicle tracking.',
     'https://www.fahadimdad.com/projects/ai-robotics/computer-vision-real-time-ai'),
    ('Fire Detection (YOLOv8)',
     'YOLOv8-based fire detection system trained on video footage for safety and incident analysis.',
     'https://www.fahadimdad.com/projects/ai-robotics/computer-vision-real-time-ai'),
    ('AI Medical Interview Platform',
     'Personalized interview simulator for radiology professionals using Google Gemini, voice-based Q&A with real-time transcription, rubric-based AI feedback, and computer vision proctoring for exam integrity.',
     'https://www.fahadimdad.com/projects/ai-robotics/multimodal-generative-ai-systems'),
]

for title, desc, url in projects:
    doc.project_entry(title, desc, url)

# ── EXPERIENCES ──────────────────────────────────────────────────────────────
doc.section_heading('EXPERIENCES')

def exp_block(doc, org, org_url, loc, role, dates, bullets):
    row(doc,
        lambda w: (doc.bd(9.8), doc.cell(doc.get_string_width(org + ' '), 5, org + ' '), doc.arrow(org_url)),
        loc)
    row(doc,
        lambda w: (doc.it(9.8), doc.cell(w, 5, role)),
        dates)
    for b in bullets:
        doc.bullet_item(b)
    doc.ln(1)

exp_block(doc, 'Beam AI', 'https://beam.ai/', 'Karachi, Pakistan',
          'AI Agent Engineer', 'Nov 2025 – Present', [
    'Designed and deployed autonomous AI agents replacing manual business processes with intelligent, fully automated systems.',
    'Built multi-step agent architectures using graph-based workflow systems, LLM orchestration, and external tool integration for enterprise clients including Booth & Partner and UNiDAYS.',
    'Implemented dynamic task routing, error handling, retry logic, and context management for long-running multi-step workflows.',
    'Integrated enterprise systems (Airtable, Slack, email) and developed evaluation frameworks with feedback loops for continuous improvement.',
])

exp_block(doc, 'Systems Limited', 'https://www.systemsltd.com/', 'Karachi, Pakistan',
          'AI & Data Science Intern', 'June 2025 – Oct 2025', [
    'Built AI solutions across Computer Vision, NLP, and Generative AI for enterprise use cases.',
    'Led development of Medical Claim App (Azure OCR + Azure OpenAI) and AI-powered chat shopping platform (React, Azure OpenAI).',
    'Trained and evaluated models using Python, Scikit-learn, TensorFlow and Keras; hands-on experience with Azure Machine Learning and Azure Cognitive Services.',
])

exp_block(doc, 'IEEE Computer Society, Salim Habib University',
          'https://www.fahadimdad.com/leadership/roles-responsibilities',
          'Karachi, Pakistan', 'Chairperson', 'July 2024 – Dec 2024', [
    'Led the chapter organising workshops, competitions, and networking events; expanded membership and industry-academia collaborations.',
])

exp_block(doc, 'IEEE SHU Student Branch, Salim Habib University',
          'https://www.fahadimdad.com/leadership/roles-responsibilities',
          'Karachi, Pakistan', 'Head of Operating Committees & Webmaster', 'Dec 2023 – Dec 2024', [
    'Organised TechNexus flagship event; developed Women in Engineering (WIE) Society, COMSOC, and EMBS within IEEE SHU.',
])

exp_block(doc, 'Smart City Lab, NCAI-NEDUET',
          'https://smartcitylab.neduet.edu.pk/',
          'Karachi, Pakistan', 'Research Intern', 'Mar 2023 – Aug 2023', [
    'Developed AR application for electronic circuit simulation using Unity, ARCore and AI; integrated AI model for hardware detection and virtual overlay superimposition.',
])

# ── LEADERSHIP ───────────────────────────────────────────────────────────────
doc.section_heading('LEADERSHIP ACTIVITIES')

row(doc,
    lambda w: (doc.bd(9.8), doc.cell(doc.get_string_width('NASA Space App Challenge '), 5, 'NASA Space App Challenge '), doc.arrow('https://www.fahadimdad.com/leadership/event-organization')),
    'Karachi, Pakistan')
row(doc,
    lambda w: (doc.it(9.8), doc.cell(w, 5, 'Organizer, Logistics Team Lead and Ambassador')),
    'Oct 2022 & Oct 2023')

doc.bullet_item('Organised NASA Space Apps Challenge at Salim Habib University (2022) and Habib University (2023); led logistics team ensuring smooth operations.')
doc.ln(2)

# ── SKILLS ───────────────────────────────────────────────────────────────────
doc.section_heading('SKILLS & LANGUAGE PROFICIENCIES')
doc.skill_line('Technologies:',
    'OpenCV, TensorFlow, Keras, Scikit-learn, PyTorch, MediaPipe, ARCore, Unity, LangChain, Hugging Face Transformers, Docker, Azure AI Services, Jupyter Notebook, Git, Flutter, Firebase, Arduino IDE')
doc.skill_line('Technical Skills:',
    'AI, Machine Learning, Deep Learning, Computer Vision, NLP, Agentic AI & LLM Orchestration, Robotics, AR/VR, Model Training & Evaluation, Data Analysis, Feature Engineering')
doc.skill_line('Programming Languages:', 'Python, C++, Java, JavaFX, Dart, C#, LaTeX')
doc.skill_line('Soft Skills:', 'Communication, Leadership, Problem-Solving, Critical Thinking, Team Management, Research')
doc.skill_line('Languages:', 'Sindhi (Native), Urdu (Native), English (Fluent)')
doc.ln(1)

# ── AWARDS ───────────────────────────────────────────────────────────────────
doc.section_heading('AWARDS')
doc.award_line('Gold Medal',
    '– Presented by Department of Information Technology, Salim Habib University')
doc.award_line('Galactic Problem Solver',
    '– Presented by NASA Space App Challenge (Oct 2022, Oct 2023)')
doc.award_line('Dean Honor Award ↗',
    '– Presented by Dean, Department of Information Technology, Salim Habib University (Spring 2021, Spring 2022, Fall 2022, Spring 2023, Fall 2023, Spring 2024, Fall 2024)',
    url='https://www.fahadimdad.com/achievements_2/academic-awards')
doc.ln(1)

# ── CERTIFICATIONS ───────────────────────────────────────────────────────────
doc.section_heading('ONLINE COURSES & CERTIFICATIONS')
doc.cert_line('AI Agents in LangGraph', '– DeepLearning.AI – Coursera')
doc.cert_line('Supervised Machine Learning: Regression and Classification', '– DeepLearning.AI – Coursera')
doc.cert_line('IBM RAG and Agentic AI', '– IBM – Coursera – ongoing')
doc.cert_line('IBM AI Developer', '– IBM – Coursera – ongoing')
doc.cert_line('Fundamentals of Agentic AI and DACA AI-First Development', '– Panaversity – ongoing')

# ── SAVE ─────────────────────────────────────────────────────────────────────
out = WS + 'Muhammad_Fahad_Imdad_CV_Updated.pdf'
doc.output(out)
print(f'Saved: {out}')
