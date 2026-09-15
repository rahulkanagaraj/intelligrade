"""
generate_sample_pdf.py
----------------------
Generates realistic University Examination PDFs using the user's 50 Aptitude & Reasoning questions.
Includes:
- University Headers & Titles
- Course Code, Date, Duration & Total Marks
- General Instructions & Boilerplate Text
- Multi-page structured questions (Q1..Q50 with options A, B, C, D)
- Headers and Footers (Page X of Y)
Used to test PDF Question Extraction scripts.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PDF_PATH = os.path.join(DATA_DIR, "sample_university_exam.pdf")

USER_50_QUESTIONS = [
    ("Q1.", "Statement: All students who attend the placement training practice aptitude regularly. Ravi attends the placement training. Which conclusion follows?<br/>A) Ravi will definitely get placed<br/>B) Ravi will score the highest marks<br/>C) Ravi practices aptitude regularly<br/>D) Ravi is the best student in the class"),
    ("Q2.", "Statement: The college increased training hours because students performed poorly in the aptitude test. What was the cause?<br/>A) Increased training hours<br/>B) College examination<br/>C) Poor performance in aptitude test<br/>D) Student attendance"),
    ("Q3.", "Statement: All students who submit assignments on time receive internal marks. Arun submitted his assignment on time. Conclusion:<br/>A) Arun will get full marks<br/>B) Arun will receive internal marks<br/>C) Arun will be absent<br/>D) Arun will not write the examination"),
    ("Q4.", "Statement: The road was closed because of heavy flooding. Which is the effect?<br/>A) Heavy flooding<br/>B) Rain<br/>C) Road closure<br/>D) Water"),
    ("Q5.", "Statement: Students are advised to carry an umbrella because rain is expected. What is the assumption?<br/>A) Students like umbrellas<br/>B) Umbrellas are expensive<br/>C) Students may get wet if it rains<br/>D) Students will not attend college"),
    ("Q6.", "Statement: All final-year students must attend the placement orientation programme. Which conclusion follows?<br/>A) Only selected students should attend<br/>B) Final-year students are required to attend<br/>C) First-year students must attend<br/>D) No student should attend"),
    ("Q7.", "Statement: The library extended its working hours during examinations. What is the most reasonable reason?<br/>A) Students stopped studying<br/>B) Students need more time to use library resources<br/>C) Teachers are absent<br/>D) Books are unavailable"),
    ("Q8.", "Statement: Ravi scored 85 marks because he practiced many questions. Which is the effect?<br/>A) Practice<br/>B) Questions<br/>C) 85 marks<br/>D) Examination"),
    ("Q9.", "Statement: If it rains heavily, the cricket match will be cancelled. It rained heavily. What can be concluded?<br/>A) The match definitely continued<br/>B) The match will be cancelled<br/>C) The players went home yesterday<br/>D) The match was played indoors"),
    ("Q10.", "Statement: All buses arriving after 9 AM are not allowed inside the campus. Bus A arrived at 9:30 AM. Conclusion:<br/>A) Bus A entered the campus<br/>B) Bus A is not allowed inside the campus<br/>C) Bus A arrived before 9 AM<br/>D) Bus A was empty"),
    ("Q11.", "Statement: The students requested additional aptitude classes before the placement test. Which assumption is most reasonable?<br/>A) Students dislike aptitude<br/>B) Students need additional preparation<br/>C) The placement test was cancelled<br/>D) Students have completed all preparation"),
    ("Q12.", "Statement: The computer lab was closed because the computers were being repaired. What is the cause?<br/>A) Lab closure<br/>B) Computer repair<br/>C) Students<br/>D) Examination"),
    ("Q13.", "Statement: Regular exercise improves physical fitness. Ravi exercises regularly. Which conclusion is reasonable?<br/>A) Ravi will become an athlete<br/>B) Ravi may improve his physical fitness<br/>C) Ravi will never become tired<br/>D) Ravi will win a competition"),
    ("Q14.", "Statement: Students who do not submit the form cannot participate in the event. Kumar did not submit the form. Conclusion:<br/>A) Kumar definitely participated<br/>B) Kumar cannot participate in the event<br/>C) Kumar organised the event<br/>D) Kumar submitted another form"),
    ("Q15.", "Which is the strongest argument for conducting mock interviews?<br/>A) They reduce the number of students<br/>B) They provide practice for real interviews<br/>C) They replace technical interviews<br/>D) They guarantee placement"),
    ("Q16.", "Statement: The college arranged additional buses because many students were travelling home. What is the cause?<br/>A) Additional buses<br/>B) College closure<br/>C) Many students travelling home<br/>D) Bus drivers"),
    ("Q17.", "Statement: Every student who clears the aptitude round proceeds to the technical round. Priya cleared the aptitude round. Conclusion:<br/>A) Priya failed the technical round<br/>B) Priya proceeds to the technical round<br/>C) Priya skipped the aptitude round<br/>D) Priya is already placed"),
    ("Q18.", "Which of the following is an assumption? Statement: 'Use a helmet while riding a bike.'<br/>A) Helmets are fashionable<br/>B) A helmet can provide protection in an accident<br/>C) Bikes are expensive<br/>D) Roads are always safe"),
    ("Q19.", "Statement: The college introduced a coding club after students requested more programming practice. Which conclusion is most reasonable?<br/>A) Students dislike programming<br/>B) Students wanted more programming practice<br/>C) Coding is no longer required<br/>D) The college cancelled programming classes"),
    ("Q20.", "Statement: All students who scored above 80% were selected for the next round. Ravi scored 85%. Conclusion:<br/>A) Ravi scored below 80%<br/>B) Ravi was selected for the next round<br/>C) Ravi did not attend the test<br/>D) Ravi failed the next round"),
    ("Q21.", "Statements: All engineers are graduates. Ravi is an engineer. Therefore:<br/>A) Ravi is a teacher<br/>B) Ravi is a student<br/>C) Ravi is a graduate<br/>D) Ravi is a doctor"),
    ("Q22.", "Statements: All laptops are computers. Some computers are expensive. Which conclusion definitely follows?<br/>A) All laptops are expensive<br/>B) Some laptops are expensive<br/>C) All laptops are computers<br/>D) No laptop is expensive"),
    ("Q23.", "Statements: Some students are programmers. All programmers are logical thinkers. Conclusion:<br/>A) All students are programmers<br/>B) Some students are logical thinkers<br/>C) No student is a programmer<br/>D) All logical thinkers are students"),
    ("Q24.", "Statements: No cats are dogs. Tom is a cat. Therefore:<br/>A) Tom is a dog<br/>B) Tom is not a dog<br/>C) Tom is both<br/>D) Cannot say"),
    ("Q25.", "Statements: All books are useful. Some books are novels. Which conclusion follows?<br/>A) All useful things are books<br/>B) Some novels are useful<br/>C) No novel is useful<br/>D) All novels are books"),
    ("Q26.", "Statements: All teachers are educated. Some educated people are writers. Which is definitely true?<br/>A) All teachers are writers<br/>B) Some teachers are writers<br/>C) All teachers are educated<br/>D) No teacher is educated"),
    ("Q27.", "Which relationship is correct?<br/>A) Dogs are outside Animals<br/>B) Dogs are a subset of Animals<br/>C) Animals are a subset of Dogs<br/>D) Dogs and Animals never overlap"),
    ("Q28.", "Which Venn relationship represents 'All roses are flowers'?<br/>A) Two separate circles<br/>B) Rose circle completely inside Flower circle<br/>C) Flower circle inside Rose circle<br/>D) Two overlapping circles with no complete inclusion"),
    ("Q29.", "Statements: Some cars are electric. All electric cars are vehicles. Conclusion:<br/>A) All cars are electric<br/>B) Some cars are vehicles<br/>C) No car is a vehicle<br/>D) All vehicles are electric cars"),
    ("Q30.", "Statements: All apples are fruits. All fruits are food. Therefore:<br/>A) All food is fruit<br/>B) All apples are food<br/>C) No apple is food<br/>D) Some food is not fruit"),
    ("Q31.", "Statements: No teachers are students. Ravi is a teacher. Therefore:<br/>A) Ravi is a student<br/>B) Ravi is not a student<br/>C) Ravi is both<br/>D) Ravi is a graduate"),
    ("Q32.", "Statements: Some programmers are gamers. Some gamers are athletes. Which statement is definitely true?<br/>A) All programmers are athletes<br/>B) Some programmers are gamers<br/>C) All athletes are programmers<br/>D) No gamer is a programmer"),
    ("Q33.", "If all A are B and all B are C, then:<br/>A) No A is C<br/>B) Some C are not A<br/>C) All A are C<br/>D) All C are A"),
    ("Q34.", "If no A is B, which statement is true?<br/>A) Every A is B<br/>B) A and B do not overlap<br/>C) Some A are B<br/>D) All B are A"),
    ("Q35.", "Statements: All doctors are professionals. Some doctors are teachers. Therefore:<br/>A) No doctor is a professional<br/>B) Some teachers are professionals<br/>C) All professionals are doctors<br/>D) No teacher is a doctor"),
    ("Q36.", "Which group is a subset of 'Vehicles'?<br/>A) Trees<br/>B) Books<br/>C) Cars<br/>D) Fruits"),
    ("Q37.", "Statements: Some engineers are managers. All managers are employees. Therefore:<br/>A) All engineers are employees<br/>B) Some engineers are employees<br/>C) No engineers are employees<br/>D) All employees are engineers"),
    ("Q38.", "All smartphones are electronic devices. Which statement is correct?<br/>A) All electronic devices are smartphones<br/>B) Every smartphone is an electronic device<br/>C) No smartphone is electronic<br/>D) Some smartphones are not devices"),
    ("Q39.", "No birds are mammals. Which statement is correct?<br/>A) All birds are mammals<br/>B) Birds and mammals are separate groups<br/>C) Some birds are mammals<br/>D) All mammals are birds"),
    ("Q40.", "Some students are athletes. What does this mean?<br/>A) Every student is an athlete<br/>B) No student is an athlete<br/>C) At least one student is an athlete<br/>D) Every athlete is a student"),
    ("Q41.", "If CAT is coded as DBU, how is DOG coded?<br/>A) DPH<br/>B) EPH<br/>C) EOG<br/>D) FPH"),
    ("Q42.", "If BOOK is coded as CPPL, how is PEN coded?<br/>A) ODM<br/>B) QFO<br/>C) PFM<br/>D) QEN"),
    ("Q43.", "If A = 1, B = 2, ..., Z = 26, what is the value of CAT?<br/>A) 22<br/>B) 24<br/>C) 25<br/>D) 26"),
    ("Q44.", "If the letters of a word are shifted one position forward, what is the code for MANGO?<br/>A) LZMFN<br/>B) NBOHP<br/>C) NANGP<br/>D) MBOHP"),
    ("Q45.", "If PEN = 35 using P=16, E=5, N=14, what is CAT?<br/>A) 22<br/>B) 24<br/>C) 25<br/>D) 26"),
    ("Q46.", "If + means × and × means +, find 4 + 3 × 2.<br/>A) 9<br/>B) 14<br/>C) 20<br/>D) 10"),
    ("Q47.", "If − means + and + means −, find 15 − 7.<br/>A) 8<br/>B) 22<br/>C) 105<br/>D) 7"),
    ("Q48.", "If @ means ÷, then 20 @ 5 = ?<br/>A) 100<br/>B) 4<br/>C) 15<br/>D) 25"),
    ("Q49.", "If # means × and $ means +, find 4 # 3 $ 2.<br/>A) 10<br/>B) 14<br/>C) 20<br/>D) 24"),
    ("Q50.", "Book : Read :: Food : ?<br/>A) Cook<br/>B) Eat<br/>C) Drink<br/>D) Buy")
]

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def build_sample_exam_pdf():
    ensure_data_dir()
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        alignment=1,
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1A365D')
    )
    
    subtitle_style = ParagraphStyle(
        'HeaderSubtitle',
        parent=styles['Normal'],
        alignment=1,
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#2D3748')
    )
    
    instruction_style = ParagraphStyle(
        'Instructions',
        parent=styles['Italic'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#4A5568')
    )
    
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=10,
        spaceAfter=4
    )
    
    question_style = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1A202C'),
        spaceBefore=6,
        spaceAfter=2
    )

    story = []
    
    # Page Header Info
    story.append(Paragraph("<b>DEPARTMENT OF PLACEMENT & REASONING ANALYTICS</b>", title_style))
    story.append(Paragraph("<b>NATIONAL INSTITUTE OF ADVANCED COMPETITIVE EXAMINATIONS</b>", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>REASONING & APTITUDE COMPREHENSIVE ASSESSMENT - 2026</b>", subtitle_style))
    story.append(Paragraph("<b>Course Code: APT-2026 | Total Questions: 50</b>", subtitle_style))
    story.append(Paragraph("Time Allowed: 2 Hours &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Maximum Marks: 100", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor('#1A365D'), spaceAfter=8))
    
    # Instructions Section
    story.append(Paragraph("<b>General Instructions:</b>", instruction_style))
    story.append(Paragraph("1. Answer all 50 questions carefully.", instruction_style))
    story.append(Paragraph("2. Each question carries 2 marks. Select the single best answer for each question.", instruction_style))
    story.append(Paragraph("3. Confidential Document - Do not remove exam paper from the examination hall.", instruction_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray, spaceAfter=10))
    
    # Add Questions
    story.append(Paragraph("<b>SECTION A: Logical Reasoning, Coding & Analytical Aptitude (50 Questions)</b>", section_style))
    
    for idx, (q_num, q_text) in enumerate(USER_50_QUESTIONS):
        story.append(Paragraph(f"<b>{q_num}</b> {q_text} [2 Marks]", question_style))
        story.append(Spacer(1, 3))
        if (idx + 1) % 10 == 0 and (idx + 1) < len(USER_50_QUESTIONS):
            story.append(PageBreak())

    doc.build(story)
    print(f"Sample University Exam PDF generated successfully at '{PDF_PATH}' with {len(USER_50_QUESTIONS)} questions!")
    return PDF_PATH

if __name__ == "__main__":
    build_sample_exam_pdf()
