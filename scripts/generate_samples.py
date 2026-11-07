"""Regenerate eight entirely fictional dummy resumes across TXT, DOCX, PDF formats."""
from pathlib import Path
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1] / 'resumes'
ROOT.mkdir(exist_ok=True)
DATA = [
    ('Aarav Mehta', 'Python Backend Engineer', 'Python, FastAPI, PostgreSQL, Docker', '3 years building REST APIs and batch processing jobs', 'pdf'),
    ('Maya Kapoor', 'Frontend React Developer', 'React, TypeScript, Redux, CSS', '4 years building accessible dashboards and design systems', 'docx'),
    ('Rohan Shah', 'Full Stack Engineer', 'Python, Django, React, PostgreSQL', '5 years developing end-to-end web applications', 'txt'),
    ('Anika Rao', 'Data Analyst', 'Python, Pandas, SQL, Power BI', '2 years preparing automated analytics reports', 'pdf'),
    ('Kabir Sethi', 'Java Engineer', 'Java, Spring Boot, MySQL, AWS', '6 years building scalable microservices', 'docx'),
    ('Sara Fernandes', 'QA Automation Engineer', 'Python, Pytest, Selenium, Playwright', '3 years building automated test suites', 'txt'),
    ('Dev Nair', 'DevOps Engineer', 'Terraform, AWS, Kubernetes, Linux', '4 years managing CI/CD and infrastructure', 'pdf'),
    ('Isha Verma', 'Node.js Backend Engineer', 'Node.js, Express, MongoDB, Redis', '4 years designing REST APIs and background workers', 'docx'),
]
for i, (name, title, skills, experience, fmt) in enumerate(DATA, 1):
    text = f'{name}\nRole: {title}\nSkills: {skills}\nExperience: {experience}\nEducation: Bachelor of Engineering\nPortfolio: example.invalid/{i}\n'
    dest = ROOT / f'{i:02d}_{name.lower().replace(" ", "_")}.{fmt}'
    if fmt == 'txt':
        dest.write_text(text, encoding='utf-8')
    elif fmt == 'docx':
        doc = Document()
        doc.add_heading(name, 0)
        for line in text.splitlines()[1:]:
            doc.add_paragraph(line)
        doc.save(dest)
    else:
        pdf = canvas.Canvas(str(dest), pagesize=A4)
        y = 785
        for line in text.splitlines():
            pdf.drawString(54, y, line)
            y -= 24
        pdf.save()
print(f'Generated {len(DATA)} fictional resumes in {ROOT}')
