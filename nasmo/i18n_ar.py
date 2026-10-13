"""Arabic dictionary. Keys are the exact English UI texts.

What stays in English on purpose: mission questions, code, mission titles, usernames, links and the
certificates (names are English). Everything else the student or teacher reads is translated.
Student-facing texts speak to a girl (feminine forms) because the lab is for female students."""
import re

AR: dict[str, str] = {}
PATTERNS: list = []
KEEP_RX = [
    re.compile(r"https?://"), re.compile(r"internal:"), re.compile(r"[`\\]"), re.compile(r"^[+\-]?\d+ ?XP$"),
    re.compile(r"^demo_\d$"), re.compile(r"\(DEMO\)|\(demo_\d\)"), re.compile(r"^Demo Student [A-Z]$"),
    re.compile(r"^Option \d$"), re.compile(r"[;{}<>=]|#include|cout|int main"), re.compile(r"^[\d\W_]+$"),
    re.compile(r"^NIL-"), re.compile(r"^\*\*.+\*\* \(.+\)$"), re.compile(r"^(?:[^A-Za-z]|\b[A-Za-z]\b)+$"), re.compile(r"\bNIL-2026-"),
]


def KEEP() -> set:
    """Titles that come from the content and stay in English."""
    global _KEEP
    if _KEEP is None:
        from .content.missions import MISSIONS
        from .content.stages import STAGES
        k = {"C++", "Nasmo", "Nova", "Nasmo Informatics", "Think .. Code .. Compete", "Think. Code. Compete.", "PDF", "CSV", "Excel", "HTML", "XP", "OK"}
        k |= {m["title"] for m in MISSIONS}
        for s in STAGES:
            for t in s.get("topics", []):
                k.add(t[0])
        _KEEP = k
    return _KEEP


_KEEP = None


def add(d: dict[str, str]) -> None:
    AR.update(d)


def pat(rx: str, fn) -> None:
    PATTERNS.append((re.compile(rx, re.S), fn))


# ------------------------------------------------------------------ navigation and general
add({
    "Home": "الرئيسية", "About": "عن المختبر", "Resources": "المراجع", "Login": "تسجيل الدخول",
    "Logout": "تسجيل الخروج", "Student Login": "دخول الطالبة", "Teacher Login": "دخول المعلمة",
    "Adventure Map": "خريطة المغامرة", "Trophy Room": "غرفة الكؤوس", "My Progress": "تقدّمي",
    "My Certificates": "شهاداتي", "Certificates": "الشهادات", "Account Settings": "إعدادات الحساب",
    "Teacher Dashboard": "لوحة المعلمة", "Dashboard": "لوحة المعلمة", "Students": "الطالبات",
    "Missions and Content": "المهمات والمحتوى", "Settings": "الإعدادات", "Progress Reports": "تقارير التقدّم",
    "Motion: on": "الحركة: تعمل", "Motion: off": "الحركة: متوقفة", "☀ Light": "☀ فاتح", "🌙 Dark": "🌙 داكن",
    "Light": "فاتح", "Dark": "داكن", "🔊 Sound: on": "🔊 الصوت: يعمل", "🔇 Sound: off": "🔇 الصوت: متوقف",
    "Local mode: data is saved on this computer only.": "الوضع المحلي: تُحفظ البيانات على هذا الجهاز فقط.",
    "Signed in as": "مسجّلة الدخول باسم", "Student": "طالبة", "Teacher": "معلمة",
    "Welcome to": "مرحبًا بكِ في",
    "Start Your Journey →": "ابدئي رحلتك ←", "Start": "ابدئي", "Play ▶": "العبي ◀", "Enter ▶": "ادخلي ◀",
    "Think": "فكّري", "Code": "برمجي", "Compete": "نافسي",
    "Sign in": "تسجيل الدخول", "Username": "اسم المستخدم", "Password": "كلمة المرور", "Name": "الاسم",
    "Enter your username": "أدخلي اسم المستخدم", "Enter your password": "أدخلي كلمة المرور",
    "Choose a username": "اختاري اسم مستخدم", "Choose a password": "اختاري كلمة مرور",
    "Repeat password": "أعيدي كلمة المرور", "Repeat your password": "أعيدي كتابة كلمة المرور",
    "Example: Sara Ahmed": "مثال: Sara Ahmed", "Example: sara_2026": "مثال: sara_2026",
    "Your name (in English)": "اسمكِ (بالإنجليزية)", "Create account": "إنشاء الحساب",
    "Setup code": "رمز الإعداد", "Create teacher account": "إنشاء حساب المعلمة",
    "Enter a username": "أدخلي اسم المستخدم", "Enter a password": "أدخلي كلمة المرور",
    "Enter a temporary password": "أدخلي كلمة مرور مؤقتة",
    "← Home": "→ الرئيسية", "⌂  Home": "⌂  الرئيسية",
    "Search": "بحث", "Type": "النوع", "Stage": "المرحلة", "All stages": "كل المراحل", "Other": "أخرى",
    "Status": "الحالة", "Score": "الدرجة", "Result": "النتيجة", "Question": "السؤال", "Step": "الخطوة",
    "Steps": "الخطوات", "Title": "العنوان", "Description (optional)": "الوصف (اختياري)",
    "Short description": "وصف مختصر", "Mission": "المهمة", "Missions": "المهمات", "Progress": "التقدّم",
    "Content": "المحتوى", "Programs": "البرامج", "When": "الوقت", "Why": "السبب", "Attempts": "المحاولات",
    "Hide": "إخفاء", "Delete": "حذف", "Active": "نشطة", "Completed": "مكتملة", "Started": "بدأت",
    "Not started": "لم تبدأ", "Unlocked": "مفتوح", "Not yet": "ليس بعد", "Correct": "صحيحة", "Wrong": "خاطئة",
    "Show": "إظهار", "Last activity": "آخر نشاط", "Last sign-in": "آخر دخول",
    "Display name": "الاسم الظاهر", "Student name": "اسم الطالبة", "Teacher name": "اسم المعلمة",
    "Save name": "حفظ الاسم", "English": "English", "Small Steps": "خطوات صغيرة", "Big Programs": "برامج كبيرة", "Save settings": "حفظ الإعدادات", "Change password": "تغيير كلمة المرور",
    "Current password": "كلمة المرور الحالية", "New password": "كلمة المرور الجديدة",
    "Repeat new password": "أعيدي كلمة المرور الجديدة", "Name updated.": "تم تحديث الاسم.",
    "Account actions": "إجراءات الحساب", "Student details": "بيانات الطالبة",
    "Manage your display name and password securely.": "أدّي اسمكِ الظاهر وكلمة مرورك بأمان.",
    "Lab rules and your account.": "قواعد المختبر وحسابكِ.",
})
AR["Manage your display name and password securely."] = "إدارة اسمكِ الظاهر وكلمة مرورك بأمان."

# ------------------------------------------------------------------ home / about / login
add({
    "Access the dashboard and manage students.": "ادخلي إلى لوحة المعلمة وأدّي حسابات الطالبات.",
    "Sign in to continue your training. Your progress is saved to your account.":
        "سجّلي دخولكِ لمتابعة تدريبكِ. يُحفظ تقدّمكِ في حسابكِ.",
    "Sign in as a student to open the missions and save your progress.":
        "سجّلي الدخول كطالبة لفتح المهمات وحفظ تقدّمكِ.",
    "Sign in as a student, then press Start Your Journey to open your stages.":
        "سجّلي الدخول كطالبة ثم اضغطي «ابدئي رحلتك» لفتح مراحلكِ.",
    "An interactive learning environment to prepare students for Nasmo Informatics 2 Competition — C++ Track (Fundamentals and Stages 1–4).":
        "بيئة تعلّم تفاعلية لتحضير الطالبات لمسابقة نسمو معلوماتيًا 2 — مسار C++ (الأساسيات والمراحل 1–4).",
    "Nasmo Informatics Lab is an interactive training space designed to help students prepare for the Nasmo Informatics 2 competition in the C++ track. The learning journey is organized into Fundamentals and Stages 1–4, with short practical missions.":
        "مختبر نسمو معلوماتيًا مساحة تدريب تفاعلية تساعد الطالبات على الاستعداد لمسابقة نسمو معلوماتيًا 2 في مسار C++. رحلة التعلّم مقسّمة إلى الأساسيات والمراحل 1–4، بمهمات عملية قصيرة.",
    "Students practise reading code, predicting output, debugging, completing code, solving problems, and explaining their reasoning.":
        "تتدرّب الطالبات على قراءة الكود، وتوقّع المخرجات، وإصلاح الأخطاء، وإكمال الكود، وحل المسائل، وشرح تفكيرهن.",
    "Answers and scores are saved to the student account, allowing students to leave and continue their training later.":
        "تُحفظ الإجابات والدرجات في حساب الطالبة، فتستطيع التوقف ومتابعة تدريبها لاحقًا.",
    "Missions and certificates are internal training resources created for this lab. They are not official materials or certificates of the Nasmo competition, Tuwaiq Academy, or the Ministry of Education. Links to the official Nasmo booklet are provided for reference.":
        "المهمات والشهادات موارد تدريب داخلية أُنشئت لهذا المختبر، وليست مواد أو شهادات رسمية من مسابقة نسمو أو أكاديمية طويق أو وزارة التعليم. روابط كتيّب نسمو الرسمي مرفقة للرجوع إليها.",
    "These certificates are issued by the lab for training purposes. They are not official certificates of Nasmo, Tuwaiq Academy or the Ministry of Education.":
        "تصدر هذه الشهادات من المختبر لأغراض التدريب، وليست شهادات رسمية من نسمو أو أكاديمية طويق أو وزارة التعليم.",
    "### About the Lab": "### عن المختبر", "### Learn by doing": "### تعلّمي بالتطبيق",
    "### Track your progress": "### تابعي تقدّمكِ", "### About the learning materials": "### عن مواد التعلّم",
    "DESIGN & EDUCATIONAL SUPERVISION": "التصميم والإشراف التربوي",
    "At least 6 characters, with English letters and at least one symbol. Allowed symbols: @  #  $  %  &  *  _  -  .  !  ?":
        "6 خانات على الأقل، من أحرف إنجليزية ورمز واحد على الأقل. الرموز المسموحة: @  #  $  %  &  *  _  -  .  !  ?",
    "3-32 characters: English letters, digits, _ . -": "من 3 إلى 32 خانة: أحرف إنجليزية وأرقام و _ . -",
    "Please write your name in English letters (A-Z), as it will appear on your certificate.":
        "يرجى كتابة اسمكِ بأحرف إنجليزية (A-Z)، فهو الذي سيظهر في شهادتكِ.",
    "Please write your name in English letters (A-Z).": "يرجى كتابة اسمكِ بأحرف إنجليزية (A-Z).",
    "No teacher account exists yet. Create the first one with the setup code (the NASMO_SETUP_CODE setting, or data/setup_code.txt, also printed in the console).":
        "لا يوجد حساب معلمة بعد. أنشئي أول حساب باستخدام رمز الإعداد (إعداد NASMO_SETUP_CODE أو الملف data/setup_code.txt، ويظهر أيضًا في نافذة التشغيل).",
    "No teacher account exists yet. Create the first one here: choose a username and a password.":
        "لا يوجد حساب معلمة بعد. أنشئي أول حساب هنا: اختاري اسم مستخدم وكلمة مرور.",
})
add({
    "Wrong username or password.": "اسم المستخدم أو كلمة المرور غير صحيحة.",
    "Wrong setup code.": "رمز الإعداد غير صحيح.",
    "This username is already taken.": "اسم المستخدم هذا مستخدم من قبل.",
    "The two passwords do not match.": "كلمتا المرور غير متطابقتين.",
    "Current password is wrong.": "كلمة المرور الحالية غير صحيحة.",
    "Password must be at least 6 characters.": "يجب ألا تقل كلمة المرور عن 6 خانات.",
    "Password must be at least 10 characters.": "يجب ألا تقل كلمة المرور عن 10 خانات.",
    "Password must contain at least one symbol: @ # $ % & * _ - . ! ?":
        "يجب أن تحتوي كلمة المرور على رمز واحد على الأقل: @ # $ % & * _ - . ! ?",
    "Username must be 3-32 characters: English letters, digits, dot, dash or underscore.":
        "يجب أن يكون اسم المستخدم من 3 إلى 32 خانة: أحرف إنجليزية وأرقام ونقطة وشرطة وشرطة سفلية.",
    "Student created. Give them the username and the temporary password.":
        "تم إنشاء حساب الطالبة. أعطيها اسم المستخدم وكلمة المرور المؤقتة.",
    "Students can create their own accounts": "يمكن للطالبات إنشاء حساباتهن بأنفسهن",
})

# ------------------------------------------------------------------ worlds, quests, game
add({
    "Code Camp": "معسكر الكود", "Logic Forest": "غابة المنطق", "Data Caves": "كهوف البيانات",
    "Mystic Maze": "المتاهة الغامضة", "Graph Galaxy": "مجرّة الرسوم",
    "Light the campfire: learn the basics.": "أشعلي نار المعسكر: تعلّمي الأساسيات.",
    "Find your way through patterns and puzzles.": "اعثري على طريقكِ بين الأنماط والألغاز.",
    "Dig up sets, maps and fast sorting.": "استخرجي المجموعات والخرائط والفرز السريع.",
    "Search every path and remember the best.": "جرّبي كل مسار واحتفظي بأفضلها.",
    "Connect the stars: graphs and trees.": "اربطي النجوم: الرسوم والأشجار.",
    "Choose your world": "اختاري عالمكِ", "Back to the world": "العودة إلى العالم",
    "Finish every quest here to win the crown.": "أنهي كل التحديات هنا لتنالي التاج.",
    "Continue your quest ▶": "تابعي تحدّيكِ ◀", "Continue learning": "تابعي التعلّم",
    "Next quest": "التحدّي التالي", "Next quest ▶": "التحدّي التالي ◀", "Keep adventuring ▶": "واصلي المغامرة ◀",
    "Open the Trophy Room 🏆": "افتحي غرفة الكؤوس 🏆", "Trophy Room 🏆": "غرفة الكؤوس 🏆",
    "Everything you earn on your adventure lives here.": "كل ما تجمعينه في مغامرتكِ تجدينه هنا.",
    "Every quest you finish drops one item. More stars means a better frame.":
        "كل تحدٍّ تنهينه يمنحكِ غرضًا. كلما زادت النجوم صار إطاره أجمل.",
    "YOU ARE HERE": "أنتِ هنا", "Mission completed!": "اكتملت المهمة!", "Code Camp cleared!": "تم إنجاز معسكر الكود!",
    "You earned the world crown.": "نلتِ تاج العالم.", "First try bonus!": "مكافأة المحاولة الأولى!",
    "Perfect run! Three stars and no slips.": "إنجاز مثالي! ثلاث نجوم بلا أي خطأ.",
    "Great job! Two stars. Can you get all three?": "أحسنتِ! نجمتان. هل تستطيعين نيل الثلاث؟",
    "Your rank": "رتبتكِ", "Ranks": "الرتب", "Your progress": "تقدّمكِ", "Quests cleared": "التحديات المنجزة",
    "Stars": "النجوم", "stars": "نجوم", "Stars here": "النجوم هنا", "XP": "XP", "XP earned": "نقاط XP المكتسبة",
    "day streak": "أيام متتالية", "loot": "غنائم", "trophies": "كؤوس", "Trophies": "الكؤوس", "Still to earn": "ما زال أمامكِ",
    "Missions completed": "المهمات المكتملة", "Missions remaining": "المهمات المتبقية", "Students finished": "طالبات أنهين",
    "Students started": "طالبات بدأن",
    "Code Rookie": "مبرمجة مبتدئة", "Bit Explorer": "مستكشفة البت", "Loop Ranger": "فارسة الحلقات",
    "Logic Knight": "فارسة المنطق", "Array Wizard": "ساحرة المصفوفات", "Algorithm Hero": "بطلة الخوارزميات",
    "Graph Master": "سيدة الرسوم", "Nasmo Champion": "بطلة نسمو",
    "Pixel Cape": "عباءة البكسل", "Golden Keyboard": "لوحة المفاتيح الذهبية", "Bug Net": "شبكة صيد الأخطاء",
    "Turbo Sneakers": "حذاء التيربو", "Crystal Compiler": "المترجم الكريستالي", "Rocket Mouse": "ماوس الصاروخ",
    "Magic Semicolon": "الفاصلة المنقوطة السحرية", "Robo Pet": "الحيوان الروبوتي", "Lucky Loop": "الحلقة المحظوظة",
    "Binary Medal": "ميدالية الثنائي", "Neon Headset": "سماعة النيون", "Code Compass": "بوصلة الكود",
    "Star Map": "خريطة النجوم", "Dragon Debugger": "تنين إصلاح الأخطاء", "Time Crystal": "كريستالة الزمن",
    "Hero Shield": "درع البطلة", "Wizard Hat": "قبعة الساحرة", "Comet Pen": "قلم المذنّب",
    "Galaxy Badge": "شارة المجرّة", "Champion Crown": "تاج البطلة",
    "First Spark": "الشرارة الأولى", "Sharp Shooter": "الرامية الماهرة", "Step Climber": "متسلقة الخطوات",
    "Mission Maker": "صانعة المهمات", "Hat-trick": "ثلاثية", "High Five": "خمسة نجوم",
    "Code Champion": "بطلة الكود", "Perfectionist": "المتقنة", "Star Collector": "جامعة النجوم",
    "Galaxy Keeper": "حارسة المجرّة", "Never Give Up": "لا تستسلمي", "C++ Coder": "مبرمجة C++",
    "On Fire": "مشتعلة", "Unstoppable": "لا تتوقف", "Nasmo Legend": "أسطورة نسمو",
    "Solve your first step": "حلّي أول خطوة", "Solve 5 steps on the first try": "حلّي 5 خطوات من المحاولة الأولى",
    "Solve 25 steps": "حلّي 25 خطوة", "Complete your first mission": "أكملي أول مهمة",
    "Complete 3 missions": "أكملي 3 مهمات", "Complete 5 missions": "أكملي 5 مهمات",
    "Complete 10 missions": "أكملي 10 مهمات", "Finish a mission with 3 stars": "أنهي مهمة بثلاث نجوم",
    "Collect 10 stars": "اجمعي 10 نجوم", "Collect 30 stars": "اجمعي 30 نجمة",
    "Solve a step after two wrong tries": "حلّي خطوة بعد محاولتين خاطئتين",
    "Solve a step by writing code": "حلّي خطوة بكتابة الكود", "Learn 3 days in a row": "تعلّمي 3 أيام متتالية",
    "Learn 7 days in a row": "تعلّمي 7 أيام متتالية", "Complete every mission": "أكملي كل المهمات",
    "Bronze": "برونزي", "Silver": "فضي", "Gold": "ذهبي",
    "Almost there. Read it once more.": "اقتربتِ. اقرئيها مرة أخرى.",
    "No problem, every coder tries again.": "لا بأس، كل مبرمجة تعيد المحاولة.",
    "Check the hint if you want a nudge.": "انظري إلى التلميح إن أردتِ دفعة صغيرة.",
    "Look at the code line by line.": "راجعي الكود سطرًا سطرًا.",
    "Nice! That is exactly right.": "رائع! هذا هو الصحيح تمامًا.",
    "Boom! Your brain is on fire.": "رائع! عقلكِ مشتعل.",
    "Clean solve. Keep going!": "حلّ نظيف. واصلي!",
    "Yes! You are leveling up.": "نعم! أنتِ تتقدّمين في المستوى.",
    "Great thinking, coder!": "تفكير ممتاز أيتها المبرمجة!",
    "That one was tricky and you got it.": "كانت صعبة ونجحتِ فيها.",
    "Not quite - try again.": "ليست تمامًا - حاولي مرة أخرى.",
    "🎁 Finish for +100 XP and up to 3 ★": "🎁 أنهيها لتنالي +100 XP وحتى 3 ★",
    "Start the quest": "ابدئي التحدّي", "Finish mission ✓": "إنهاء المهمة ✓",
    "Next step →": "الخطوة التالية ←", "← Previous step": "→ الخطوة السابقة",
    "Check answer": "تحقّقي من الإجابة", "Need a hint?": "تحتاجين تلميحًا؟", "Explanation": "الشرح",
    "Your answer": "إجابتكِ", "Your final answer": "إجابتكِ النهائية",
    "Your C++ solution (saved for your teacher)": "حلّكِ بلغة C++ (يُحفظ لمعلمتكِ)",
    "Choose the Correct Answer": "اختاري الإجابة الصحيحة", "Understand the Code": "افهمي الكود",
    "Predict the Output": "توقّعي المخرجات", "Find the Bug": "اعثري على الخطأ", "Complete the Code": "أكملي الكود",
    "Solve the Problem": "حلّي المسألة", "**Step 1 · Understand the Code**": "**الخطوة 1 · افهمي الكود**",
    "**Step 2 · Predict the Output**": "**الخطوة 2 · توقّعي المخرجات**",
    "Code example": "مثال بالكود", "Sara · saved to your account": "Sara · محفوظ في حسابكِ",
    "Open My Certificates to view it.": "افتحي «شهاداتي» لعرضها.",
    "Algorithm review": "مراجعة الخوارزمية",
})

# ------------------------------------------------------------------ resources, certificates
add({
    "Official Nasmo topic": "موضوع نسمو الرسمي", "Training guide": "دليل تدريبي", "Video": "فيديو", "Videos": "فيديوهات",
    "Worksheet": "ورقة عمل", "C++ reference": "مرجع C++", "Practice problems": "مسائل تدريبية", "Official Nismo Topics": "مواضيع نسمو الرسمية",
    "Official Nasmo topics and the materials your teacher added.": "مواضيع نسمو الرسمية والمواد التي أضافتها معلمتكِ.",
    "Search by title or description": "ابحثي بالعنوان أو الوصف",
    "No resources match. Try clearing the filters.": "لا توجد مراجع مطابقة. جرّبي مسح عوامل التصفية.",
    "Open link ↗": "فتح الرابط ↖", "Link (https://…)": "الرابط (https://…)", "Add resource": "إضافة مرجع",
    "Add a resource": "إضافة مرجع", "Nasmo booklets - Introduction": "كتيّبات نسمو - مقدمة",
    "[Official Nasmo booklet – introduction](https://nsmobooklets.mawhiba.sa/en/learn/overview/introduction.html)":
        "[كتيّب نسمو الرسمي – مقدمة](https://nsmobooklets.mawhiba.sa/en/learn/overview/introduction.html)",
    "Interactive Kit - Training Guide": "الحقيبة التفاعلية - دليل التدريب",
    "Certificate": "الشهادة", "Certificate designs": "تصاميم الشهادات",
    "Certificate designs students can choose from": "تصاميم الشهادات التي تختار منها الطالبات",
    "Your certificates": "شهاداتكِ", "Use this design": "استخدمي هذا التصميم", "✓ Selected": "✓ مختار",
    "Download certificate (HTML)": "تحميل الشهادة (HTML)",
    "To get a PDF: open the downloaded file, press Print and choose Save as PDF.":
        "للحصول على PDF: افتحي الملف المحمّل واضغطي طباعة ثم اختاري الحفظ بصيغة PDF.",
    "No certificates yet. Complete all missions of a stage to earn its certificate.":
        "لا توجد شهادات بعد. أكملي كل مهمات مرحلة لتنالي شهادتها.",
    "No certificates have been earned yet.": "لم تحصل أي طالبة على شهادة بعد.",
    "Look at the four designs and choose the one you like. Your certificate is issued only after you complete every mission of a stage; then it appears below in the design you chose (you can change it at any time).":
        "شاهدي التصاميم الأربعة واختاري ما يعجبكِ. تصدر شهادتكِ فقط بعد إكمال كل مهمات مرحلة، ثم تظهر أدناه بالتصميم الذي اخترتِه (ويمكنكِ تغييره في أي وقت).",
    "Internal training certificates earned in the lab.": "شهادات تدريب داخلية نلتِها في المختبر.",
    "Internal training certificates issued to students.": "شهادات تدريب داخلية صادرة للطالبات.",
    "A certificate is issued automatically when a student completes every mission of a stage with an average score of at least 60% (change it in Settings).":
        "تصدر الشهادة تلقائيًا عندما تكمل الطالبة كل مهمات مرحلة بمعدل لا يقل عن 60% (يمكن تغييره من الإعدادات).",
    "**Royal Purple** - Classic double border in the lab's purple and blue.": "**Royal Purple** - إطار مزدوج كلاسيكي بلون المختبر البنفسجي والأزرق.",
    "**Galaxy Night** - Dark space sky with glowing stars and neon accents.": "**Galaxy Night** - سماء فضاء داكنة بنجوم متوهجة ولمسات نيون.",
    "**Golden Honor** - Warm cream paper, gold frame and a laurel seal.": "**Golden Honor** - ورق كريمي دافئ وإطار ذهبي وختم من أغصان الغار.",
    "**Adventure Quest** - Bright and playful, with the Nova robot and stars.": "**Adventure Quest** - مشرق ومرح، مع الروبوت نوفا والنجوم.",
    "Certificate PREVIEW": "معاينة الشهادة",
})

# ------------------------------------------------------------------ teacher
add({
    "How the class is doing, stage by stage and mission by mission.": "كيف حال الطالبات، مرحلة بمرحلة ومهمة بمهمة.",
    "Real numbers from your students' saved progress.": "أرقام حقيقية من تقدّم طالباتكِ المحفوظ.",
    "Search, review, manage and export.": "ابحثي وراجعي وأدّي وصدّري.",
    "Show or hide missions, add your own, and manage resources.": "أظهري المهمات أو أخفيها، وأضيفي مهماتكِ، وأدّي المراجع.",
    "Demo data": "بيانات تجريبية", "Load demo data": "تحميل بيانات تجريبية", "Remove demo data": "حذف البيانات التجريبية",
    "Include demo data in the numbers": "احتساب البيانات التجريبية ضمن الأرقام",
    "DEMO DATA is included in these numbers. Turn it off to see real students only.":
        "البيانات التجريبية محتسبة ضمن هذه الأرقام. أوقفيها لرؤية الطالبات الحقيقيات فقط.",
    "Demo students are clearly named 'Demo Student …', cannot sign in, and are never mixed into the numbers unless you switch the option above on.":
        "الطالبات التجريبيات أسماؤهن «Demo Student …» ولا يمكنهن الدخول، ولا يدخلن في الأرقام إلا إذا فعّلتِ الخيار أعلاه.",
    "Demo student: no account actions (it cannot sign in). Remove all demo data from the Dashboard.":
        "طالبة تجريبية: لا توجد إجراءات للحساب (لا تستطيع الدخول). احذفي كل البيانات التجريبية من لوحة المعلمة.",
    "No students yet.": "لا توجد طالبات بعد.", "No students yet, so there is nothing to report.": "لا توجد طالبات بعد، فلا يوجد ما يُعرض في التقرير.",
    "No students yet. Students can create their own account from Student Login, or you can add them in Students. You can also load demo data to see how the dashboard looks.":
        "لا توجد طالبات بعد. تستطيع الطالبات إنشاء حساباتهن من «دخول الطالبة»، أو يمكنكِ إضافتهن من «الطالبات». ويمكنكِ أيضًا تحميل بيانات تجريبية لرؤية شكل اللوحة.",
    "No answers yet.": "لا توجد إجابات بعد.", "Recent answers": "أحدث الإجابات",
    "Nobody needs follow-up right now.": "لا توجد طالبات بحاجة إلى متابعة الآن.",
    "Students who need follow-up": "طالبات بحاجة إلى متابعة", "no activity for 7+ days": "لا نشاط منذ 7 أيام أو أكثر",
    "Active (7 days)": "نشطات (7 أيام)", "Average progress": "متوسط التقدّم", "Average score": "متوسط الدرجات",
    "Answer accuracy": "دقة الإجابات", "By stage": "حسب المرحلة", "Progress by stage": "التقدّم حسب المرحلة",
    "Wrong answers": "الإجابات الخاطئة", "Review questions": "أسئلة تحتاج مراجعة",
    "Add a student account": "إضافة حساب طالبة", "Create student": "إنشاء حساب الطالبة",
    "Temporary password (at least 6 characters)": "كلمة مرور مؤقتة (6 خانات على الأقل)",
    "Password (at least 10 characters)": "كلمة المرور (10 خانات على الأقل)",
    "Add another teacher": "إضافة معلمة أخرى", "Search by name or username": "ابحثي بالاسم أو اسم المستخدم",
    "Choose a student": "اختاري طالبة", "Disable account": "تعطيل الحساب", "Reset password": "إعادة تعيين كلمة المرور",
    "Delete this student": "حذف هذه الطالبة", "Delete permanently": "حذف نهائي",
    "This permanently deletes the account, progress, answers and certificates. It cannot be undone.":
        "سيُحذف الحساب والتقدّم والإجابات والشهادات نهائيًا، ولا يمكن التراجع.",
    "Export students (CSV)": "تصدير الطالبات (CSV)", "Export all answers (CSV)": "تصدير كل الإجابات (CSV)",
    "Download Complete Analysis (Excel)": "تحميل التحليل الكامل (Excel)",
    "Download Complete Analysis (PDF)": "تحميل التحليل الكامل (PDF)",
    "Download Student Progress PDF": "تحميل تقرير تقدّم الطالبة (PDF)",
    "Add a mission": "إضافة مهمة", "Add mission": "إضافة مهمة", "Mission title": "عنوان المهمة",
    "Code to show (optional)": "كود للعرض (اختياري)", "Correct option": "الخيار الصحيح",
    "Explanation (English)": "الشرح (بالإنجليزية)", "Explanation (Arabic)": "الشرح (بالعربية)",
    "A teacher-made mission has one multiple-choice question.": "المهمة التي تنشئها المعلمة تحتوي سؤال اختيار من متعدد واحدًا.",
    "Minimum average score for a certificate (%)": "أدنى معدل للحصول على شهادة (%)",
    "Days without activity before a student needs follow-up": "عدد أيام الانقطاع قبل أن تحتاج الطالبة إلى متابعة",
    "Teacher preview - nothing is saved": "معاينة المعلمة - لا يُحفظ شيء",
    "Teacher preview: open any world and quest; nothing is saved.": "معاينة المعلمة: افتحي أي عالم وتحدٍّ؛ لا يُحفظ شيء.",
    "Teacher preview: you can open every quest and check answers, but nothing is saved.":
        "معاينة المعلمة: يمكنكِ فتح كل التحديات وفحص الإجابات، لكن لا يُحفظ شيء.",
    "Created 6 demo students.": "تم إنشاء 6 طالبات تجريبيات.",
})

# ------------------------------------------------------------------ patterns with numbers and names
def _n(m, i=1):
    return m.group(i)


pat(r"(\d+)% of the lab", lambda m: f"{m[1]}% من المختبر")
pat(r"(\d+)/(\d+) [Mm]issions", lambda m: f"{m[1]}/{m[2]} مهمات")
pat(r"(\d+) Missions", lambda m: f"{m[1]} مهمات")
pat(r"(\d+)/(\d+) steps", lambda m: f"{m[1]}/{m[2]} خطوات")
pat(r"(\d+) steps", lambda m: f"{m[1]} خطوات")
pat(r"(\d+) XP to", lambda m: f"متبقّي {m[1]} XP للوصول إلى")
pat(r"Backpack · (\d+/\d+)", lambda m: f"الحقيبة · {m[1]}")
pat(r"Trophies · (\d+/\d+)", lambda m: f"الكؤوس · {m[1]}")
pat(r"QUEST (\d+)", lambda m: f"التحدّي {m[1]}")
pat(r"Stage (\d+)", lambda m: f"المرحلة {m[1]}")
pat(r"Enter Stage (\d+)", lambda m: f"ادخلي المرحلة {m[1]}")
pat(r"Enter Fundamentals", lambda m: "ادخلي الأساسيات")
pat(r"← Stage (\d+)", lambda m: f"→ المرحلة {m[1]}")
pat(r"← Fundamentals", lambda m: "→ الأساسيات")
pat(r"← Adventure Map", lambda m: "→ خريطة المغامرة")
pat(r"🔥 (\d+) in a row", lambda m: f"🔥 {m[1]} متتالية")
pat(r"LEVEL UP! Level (\d+)", lambda m: f"ارتفع مستواكِ! المستوى {m[1]}")
pat(r"(?:🐣|🌀|🧭|🛡️|🧙|🦸|🕸️|👑)? ?Level (\d+) · (.+)", lambda m: f"المستوى {m[1]} · {_t(m[2])}")
pat(r"You are now an? (.+)\.", lambda m: f"أصبحتِ الآن {_t(m[1])}.")
pat(r"New trophy: (.+)", lambda m: f"كأس جديد: {_t(m[1])}")
pat(r"New certificate: (.+)", lambda m: f"شهادة جديدة: {_t(m[1])}")
pat(r"Complete: (.+)", lambda m: f"أكملي: {_t(m[1])}")
pat(r"Complete every mission in (.+)", lambda m: f"أكملي كل المهمات في {_t(m[1])}")
pat(r"(.+) Conqueror", lambda m: f"فاتحة {_t(m[1])}")
pat(r"(.+) crown", lambda m: f"تاج {_t(m[1])}")
pat(r"Continue learning: (.+?) →", lambda m: f"تابعي التعلّم: {_t(m[1])} ←")
pat(r"Your next quest is waiting: (.+?)\. Ready\?", lambda m: f"تحدّيكِ التالي ينتظركِ: {_t(m[1])}. هل أنتِ جاهزة؟")
pat(r"Correct! (.+?)\s*Step score: (\d+)%\.", lambda m: f"إجابة صحيحة! {_t(m[1])} درجة الخطوة: {m[2]}%.")
pat(r"Correct! Step score: (\d+)%\.", lambda m: f"إجابة صحيحة! درجة الخطوة: {m[1]}%.")
pat(r"Username: (.+)", lambda m: f"اسم المستخدم: {m[1]}")
pat(r"Type the username \((.+)\) to confirm", lambda m: f"اكتبي اسم المستخدم ({m[1]}) للتأكيد")
pat(r"Most wrong answers: (.+)", lambda m: f"أكثر الإجابات الخاطئة: {m[1]}")
pat(r"stuck on (\S+) / step (\S+) \((\d+) wrong tries\)", lambda m: f"متعثرة في {m[1]} / الخطوة {m[2]} ({m[3]} محاولات خاطئة)")
pat(r"Created (\d+) demo students\.", lambda m: f"تم إنشاء {m[1]} طالبات تجريبيات.")
pat(r"(Bronze|Silver|Gold) · (.+)", lambda m: f"{_t(m[1])} · {_t(m[2])}")
pat(r"(\d+)% of (.+)", lambda m: f"{m[1]}% من {_t(m[2])}")


def _t(s: str) -> str:
    """Translate a piece used inside a pattern (falls back to the original)."""
    from .i18n import _resolve
    return _resolve(s.strip()) or s


# stage names and subtitles (mission titles stay English)
add({
    "Fundamentals": "الأساسيات", "Build a Strong Foundation": "ابني أساسًا متينًا",
    "Modular Algorithms": "الخوارزميات المعيارية", "Data Structures & Algorithms": "هياكل البيانات والخوارزميات",
    "Advanced Problem Solving": "حل المسائل المتقدم", "Graphs & Advanced Structures": "الرسوم والهياكل المتقدمة",
    "Training Completion": "إتمام التدريب", "Full Training Completion": "إتمام التدريب الكامل",
    "The C++ essentials: program structure, types, input/output, decisions, loops, functions, arrays and vectors.":
        "أساسيات C++‎: بنية البرنامج، والأنواع، والإدخال والإخراج، والقرارات، والحلقات، والدوال، والمصفوفات، والمتجهات.",
    "Five core problem-solving patterns that appear again and again.": "خمسة أنماط أساسية لحل المسائل تتكرر باستمرار.",
    "Containers, bits, complexity, sorting and searching.": "الحاويات، والبتات، والتعقيد، والفرز، والبحث.",
    "Search, dynamic programming and number theory.": "البحث، والبرمجة الديناميكية، ونظرية الأعداد.",
    "Graphs, trees and advanced data structures.": "الرسوم، والأشجار، وهياكل البيانات المتقدمة.",
    "Nasmo Informatics Lab - Full Training Completion": "مختبر نسمو معلوماتيًا - إتمام التدريب الكامل",
})

# ------------------------------------------------------------------ messages and remaining texts
add({
    "Choose a stage.": "اختاري مرحلة.", "Choose which option is correct.": "حدّدي الخيار الصحيح.",
    "Give between 2 and 6 answer options.": "أدخلي من 2 إلى 6 خيارات للإجابة.",
    "Mission not found.": "المهمة غير موجودة.", "Only teacher-made missions can be deleted.": "يمكن حذف المهمات التي أنشأتها المعلمة فقط.",
    "Please write the question.": "اكتبي السؤال من فضلك.", "Student not found.": "الطالبة غير موجودة.",
    "Title must be 3-80 characters.": "يجب أن يكون العنوان من 3 إلى 80 خانة.",
    "A teacher account already exists. Please sign in.": "يوجد حساب معلمة بالفعل. سجّلي الدخول من فضلك.",
    "Invalid login type.": "نوع تسجيل الدخول غير صحيح.",
    "Password must contain English letters.": "يجب أن تحتوي كلمة المرور على أحرف إنجليزية.",
    "Please enter your name (2-60 characters).": "أدخلي اسمكِ (من 2 إلى 60 خانة).",
    "Please sign in.": "سجّلي الدخول من فضلك.",
    "Student registration is closed. Ask your teacher for an account.": "التسجيل مغلق. اطلبي حسابًا من معلمتكِ.",
    "Account creation is closed. Ask your teacher to create an account for you.": "إنشاء الحسابات مغلق. اطلبي من معلمتكِ إنشاء حساب لكِ.",
    "Teacher permission required.": "هذا الإجراء يتطلب صلاحية المعلمة.",
    "Unknown setting.": "إعداد غير معروف.", "You can only view your own data.": "يمكنكِ عرض بياناتكِ أنتِ فقط.",
    "This mission is not available.": "هذه المهمة غير متاحة.", "This step does not exist.": "هذه الخطوة غير موجودة.",
    "Title must be 3-120 characters.": "يجب أن يكون العنوان من 3 إلى 120 خانة.",
    "Unknown resource type.": "نوع المرجع غير معروف.", "Unknown stage.": "مرحلة غير معروفة.",
    "Added by teacher": "أضافتها المعلمة", "Teacher-provided": "من المعلمة",
    "Official - Nasmo booklets": "رسمي - كتيّبات نسمو",
    "Official introduction to the Nasmo Informatics booklets.": "مقدمة رسمية لكتيّبات نسمو معلوماتيًا.",
    "Playlist of about 35 explanation videos for the Nasmo Olympiad kit (Informatics). Use it as a reference next to the lab missions.":
        "قائمة تشغيل بنحو 35 فيديو شرح لحقيبة أولمبياد نسمو (المعلوماتية). استخدميها مرجعًا بجانب مهمات المختبر.",
    "The visual training guide of the lab (opens inside the platform).": "الدليل التدريبي المرئي للمختبر (يُفتح داخل المنصة).",
    "Start your learning journey": "ابدئي رحلة تعلّمكِ", "Access dashboard and manage students": "ادخلي إلى لوحة المعلمة وأدّي الطالبات",
    "Open official topic ↗": "افتحي الموضوع الرسمي ↖", "Practised in the lab missions (no official page)": "يُتدرَّب عليه في مهمات المختبر (بلا صفحة رسمية)",
    "Mission complete!": "اكتملت المهمة!", "Mission complete! Replay it for more stars.": "اكتملت المهمة! أعيديها لتنالي نجومًا أكثر.",
    "Top rank reached. You are a legend!": "وصلتِ إلى أعلى رتبة. أنتِ أسطورة!",
    "You are a conqueror of this world.": "أنتِ فاتحة هذا العالم.",
    "Loot": "الغنائم", "Level": "المستوى", "In progress": "قيد التقدّم", "Correct!": "إجابة صحيحة!",
    "Continue": "تابعي", "Enter": "ادخلي", "Open": "افتحي", "Continue learning ▶": "تابعي التعلّم ◀",
    "No active quests in this world yet.": "لا توجد تحديات مفعّلة في هذا العالم بعد.",
    "No resources yet.": "لا توجد مراجع بعد.", "Continue ▶": "تابعي ◀", "Replay ↺": "إعادة ↺",
    "THINK · CODE · COMPETE": "فكّري · برمجي · نافسي",
    "You cleared every world. You are a Nasmo Legend!": "أنهيتِ كل العوالم. أنتِ أسطورة نسمو!",
    "You completed every mission. Well done!": "أكملتِ كل المهمات. أحسنتِ!",
    "Go to the unsolved step": "اذهبي إلى الخطوة غير المحلولة", "Review steps": "مراجعة الخطوات",
    "Password changed.": "تم تغيير كلمة المرور.",
    "Preview finished. Nothing was saved because you are signed in as a teacher.": "انتهت المعاينة. لم يُحفظ شيء لأنكِ مسجّلة كمعلمة.",
    "Some steps are not solved yet, so the mission is not complete. Go back and finish them.":
        "هناك خطوات لم تُحل بعد، فالمهمة غير مكتملة. ارجعي وأنهيها.",
    "The two new passwords do not match.": "كلمتا المرور الجديدتان غير متطابقتين.",
    "You already solved this step.": "لقد حللتِ هذه الخطوة من قبل.",
    "Your answer is correct, but it could not be saved": "إجابتكِ صحيحة لكن تعذّر حفظها",
    "Your explanation": "شرحكِ", "Your teacher revoked this certificate.": "ألغت معلمتكِ هذه الشهادة.",
    "Student Name": "اسم الطالبة", "Your certificate title": "عنوان شهادتكِ",
    "This is a preview. A real certificate is issued after you complete every mission of a stage.":
        "هذه معاينة فقط. تصدر الشهادة الحقيقية بعد إكمال كل مهمات مرحلة.",
    "Accepted answer(s):": "الإجابات المقبولة:", "Average score %": "متوسط الدرجات %", "Avg. score": "متوسط الدرجة",
    "Code the student wrote (Solve the Problem steps)": "الكود الذي كتبته الطالبة (خطوات حل المسألة)",
    "Created": "تاريخ الإنشاء", "Date": "التاريخ", "Demo students already exist.": "الطالبات التجريبيات موجودات بالفعل.",
    "Disabled": "معطّل", "Enable account": "تفعيل الحساب",
    "Free-text explanation, checked against key ideas.": "شرح كتابي حرّ، يُفحص مقابل الأفكار الأساسية.",
    "Hidden from students": "مخفية عن الطالبات", "Incorrect": "غير صحيحة", "Issued": "تاريخ الإصدار",
    "Latest answers": "أحدث الإجابات", "Mission Analysis": "تحليل المهمات",
    "Mission added. Students see it in its stage.": "تمت إضافة المهمة. ستراها الطالبات في مرحلتها.",
    "New temporary password (shown only now - give it to the student):": "كلمة المرور المؤقتة الجديدة (تظهر الآن فقط - أعطيها للطالبة):",
    "No student matches your search.": "لا توجد طالبة مطابقة لبحثكِ.", "Option": "الخيار",
    "Overview": "نظرة عامة", "Progress %": "التقدّم %", "Removed": "محذوفة", "Resource added.": "تمت إضافة المرجع.",
    "Restore certificate": "استعادة الشهادة", "Revoke certificate": "إلغاء الشهادة", "Revoked": "ملغاة",
    "Serial": "الرقم التسلسلي", "Settings saved.": "تم حفظ الإعدادات.", "Student deleted.": "تم حذف الطالبة.",
    "Student Summary": "ملخص الطالبة", "Teacher account created.": "تم إنشاء حساب المعلمة.",
    "The username does not match.": "اسم المستخدم غير مطابق.", "Total missions": "إجمالي المهمات", "Unknown": "غير معروف",
    "Valid": "سارية", "Please fill in the title, the question, at least two options, and make sure the correct option is not empty.":
        "املئي العنوان والسؤال وخيارين على الأقل، وتأكدي أن الخيار الصحيح ليس فارغًا.",
    "Latest answers ": "أحدث الإجابات", "Student Progress Report": "تقرير تقدّم الطالبة",
    "Review steps ": "مراجعة الخطوات", "Reset": "إعادة تعيين",
    "Removed demo students.": "تم حذف الطالبات التجريبيات.",
})

pat(r"Password must be at least (\d+) characters\.", lambda m: f"يجب ألا تقل كلمة المرور عن {m[1]} خانات.")
pat(r"New password must be at least (\d+) characters\.", lambda m: f"يجب ألا تقل كلمة المرور الجديدة عن {m[1]} خانات.")
pat(r"Password \(at least (\d+) characters\)", lambda m: f"كلمة المرور ({m[1]} خانات على الأقل)")
pat(r"Temporary password \(at least (\d+) characters\)", lambda m: f"كلمة مرور مؤقتة ({m[1]} خانات على الأقل)")
pat(r"Too many failed attempts\. Try again in (\d+) seconds\.", lambda m: f"محاولات فاشلة كثيرة. حاولي مرة أخرى بعد {m[1]} ثانية.")
pat(r"Password can only use English letters, digits and these symbols: (.+)",
    lambda m: f"يمكن أن تتكون كلمة المرور من أحرف إنجليزية وأرقام وهذه الرموز فقط: {m[1]}")
pat(r"Password must contain at least one symbol: (.+)", lambda m: f"يجب أن تحتوي كلمة المرور على رمز واحد على الأقل: {m[1]}")
pat(r"At least (\d+) characters, with English letters and at least one symbol\. Allowed symbols: (.+)",
    lambda m: f"{m[1]} خانات على الأقل، من أحرف إنجليزية ورمز واحد على الأقل. الرموز المسموحة: {m[2]}")
pat(r"Could not reach the database: (.+)", lambda m: f"تعذّر الوصول إلى قاعدة البيانات: {m[1]}")
pat(r"Could not open the database \((.+)\)\.", lambda m: f"تعذّر فتح قاعدة البيانات ({m[1]}).")
pat(r"Could not load your progress: (.+)", lambda m: f"تعذّر تحميل تقدّمكِ: {m[1]}")
pat(r"Could not load your trophies: (.+)", lambda m: f"تعذّر تحميل كؤوسكِ: {m[1]}")
pat(r"Could not load certificates: (.+)", lambda m: f"تعذّر تحميل الشهادات: {m[1]}")
pat(r"Could not load resources: (.+)", lambda m: f"تعذّر تحميل المراجع: {m[1]}")
pat(r"Could not check your answer: (.+)", lambda m: f"تعذّر فحص إجابتكِ: {m[1]}")
pat(r"Removed (\d+) demo students\.", lambda m: f"تم حذف {m[1]} طالبات تجريبيات.")
pat(r"Level (\d+)", lambda m: f"المستوى {m[1]}")
pat(r"The guide file is missing: (.+)", lambda m: f"ملف الدليل غير موجود: {m[1]}")
pat(r"Average score: (\d+)%", lambda m: f"متوسط الدرجات: {m[1]}%")
pat(r"(\d+) wrong tries", lambda m: f"{m[1]} محاولات خاطئة")
pat(r":orange\[(.+)\]", lambda m: ":orange[" + _t(m[1]) + "]")

# ------------------------------------------------------------------ forgotten passwords
add({
    "Forgot your password?": "نسيتِ كلمة المرور؟",
    "Write your username and send a request. Your teacher will give you a temporary password.":
        "اكتبي اسم المستخدم وأرسلي الطلب. ستعطيكِ معلمتكِ كلمة مرور مؤقتة.",
    "Your username": "اسم المستخدم الخاص بكِ", "Send request to my teacher": "إرسال الطلب إلى معلمتي",
    "Request sent. When your teacher gives you a temporary password, sign in with it and change it from Account Settings.":
        "تم إرسال الطلب. عندما تعطيكِ معلمتكِ كلمة مرور مؤقتة، سجّلي الدخول بها ثم غيّريها من إعدادات الحساب.",
    "Forgot your password or username?": "نسيتِ كلمة المرور أو اسم المستخدم؟",
    "Ask another teacher to reset your password: Settings, then Teachers, then Reset password.":
        "اطلبي من معلمة أخرى إعادة تعيين كلمة مرورك: الإعدادات ثم «Teachers» ثم «إعادة تعيين كلمة المرور».",
    "There is one teacher account, so you can recover it with the setup code. The code is in the file setup_code.txt inside the data folder of this computer, or it is the NASMO_SETUP_CODE value if you set one. After recovery the page shows your username.":
        "يوجد حساب معلمة واحد، لذلك يمكنكِ استرجاعه برمز الإعداد. الرمز في الملف setup_code.txt داخل مجلد البيانات في هذا الجهاز، أو هو قيمة NASMO_SETUP_CODE إن كنتِ قد حدّدتِها. بعد الاسترجاع ستظهر لكِ الصفحة اسم المستخدم.",
    "Repeat new password": "أعيدي كلمة المرور الجديدة", "Recover my account": "استرجاع حسابي",
    "Teachers": "المعلمات", "Password requests": "طلبات كلمة المرور", "Done": "تم",
    "Generate temporary password": "توليد كلمة مرور مؤقتة", "Dismiss request": "تجاهل الطلب",
    "Use Account Settings to change your own password.": "لتغيير كلمة مرورك أنتِ استخدمي إعدادات الحساب.",
    "Teacher not found.": "المعلمة غير موجودة.",
    "Recovery with the setup code works only when the lab has exactly one teacher account. Ask another teacher to reset your password from Settings.":
        "الاسترجاع برمز الإعداد يعمل فقط عندما يكون في المختبر حساب معلمة واحد. اطلبي من معلمة أخرى إعادة تعيين كلمة مرورك من الإعدادات.",
    "New temporary password (shown only now - give it to the teacher; she changes it in Account Settings):":
        "كلمة المرور المؤقتة الجديدة (تظهر الآن فقط - أعطيها للمعلمة لتغيّرها من إعدادات الحساب):",
    "Reset password": "إعادة تعيين كلمة المرور",
})
pat(r"New password \(at least (\d+) characters\)", lambda m: f"كلمة المرور الجديدة ({m[1]} خانات على الأقل)")
pat(r"Done\. Your username is: (.+)\. Sign in with your new password\.",
    lambda m: f"تم. اسم المستخدم الخاص بكِ هو: {m[1]}. سجّلي الدخول بكلمة مرورك الجديدة.")
pat(r"(\d+) student\(s\) asked for a new password\. Open Students to give each one a temporary password\.",
    lambda m: f"{m[1]} طالبة طلبت كلمة مرور جديدة. افتحي «الطالبات» لتعطي كل واحدة كلمة مرور مؤقتة.")
pat(r"Temporary password for (.*) \((.*)\) - shown only now\. Give it to her; she should change it from Account Settings:",
    lambda m: f"كلمة المرور المؤقتة لـ {m[1]} ({m[2]}) - تظهر الآن فقط. أعطيها للطالبة لتغيّرها من إعدادات الحساب:")
pat(r"(.+)  - you", lambda m: f"{m[1]}  - أنتِ")

add({
    "Please enter your username.": "اكتبي اسم المستخدم من فضلك.",
    "This username does not exist. Check it and try again.": "اسم المستخدم هذا غير موجود. تأكدي منه وحاولي مرة أخرى.",
    "This account is disabled. Ask your teacher.": "هذا الحساب معطّل. اسألي معلمتكِ.",
})


# ------------------------------------------------------------------ impact report page
add({
    "Impact Report": "تقرير الأثر",
    "How the lab is affecting your students: participation, scores, progress and a full analysis.":
        "كيف يؤثر المعمل في طالباتك: المشاركة والدرجات والتقدّم وتحليل كامل للموقف.",
    "Download report (Arabic)": "تنزيل التقرير (بالعربية)",
    "Download report (English)": "تنزيل التقرير (بالإنجليزية)",
    "Open the downloaded file in your browser and choose Print, then Save as PDF.":
        "افتحي الملف المُنزَّل في المتصفح ثم اختاري طباعة ثم «حفظ بصيغة PDF».",
})


# ------------------------------------------------------------------ discussion board
add({
    "Discussion Board": "لوح النقاش",
    "Ask your classmates, help each other, and learn together. Be kind and keep it about the lab.":
        "اسألي زميلاتك، وساعدن بعضكن، وتعلّمن معًا. كوني لطيفة واجعلي الحديث عن المعمل.",
    "Ask a question": "اطرحي سؤالًا", "Question title": "عنوان السؤال",
    "e.g. Why does my loop run forever?": "مثال: لماذا تعمل الحلقة عندي بلا نهاية؟",
    "Details (you can paste code between ``` lines)": "التفاصيل (يمكنك لصق الكود بين سطرين ```)",
    "Your answer (you can paste code between ``` lines)": "إجابتكِ (يمكنك لصق الكود بين سطرين ```)",
    "Post question": "نشر السؤال", "Post answer": "نشر الإجابة", "Search the board": "ابحثي في اللوح",
    "Search by a word in the title or details": "ابحثي بكلمة من العنوان أو التفاصيل",
    "No questions yet. Be the first to ask.": "لا توجد أسئلة بعد. كوني أول من تسأل.",
    "Nothing matches your search.": "لا شيء يطابق بحثكِ.",
    "Open discussion": "فتح النقاش", "Back to the board": "العودة إلى اللوح",
    "This question no longer exists.": "هذا السؤال لم يعد موجودًا.",
    "Answers": "الإجابات", "No answers yet. Can you help?": "لا توجد إجابات بعد. هل تستطيعين المساعدة؟",
    "This discussion is closed.": "هذا النقاش مغلق.",
    "Your question was posted.": "تم نشر سؤالكِ.", "Your answer was posted.": "تم نشر إجابتكِ.", "Deleted.": "تم الحذف.",
    "Helped me": "أفادتني", "Thanks sent": "تم إرسال الشكر", "Accept answer": "اعتماد الإجابة",
    "Remove accepted mark": "إزالة علامة الاعتماد", "Delete": "حذف", "Unpin": "إلغاء التثبيت", "Pin": "تثبيت",
    "Reopen discussion": "إعادة فتح النقاش", "Close discussion": "إغلاق النقاش",
    "Pinned": "مثبّت", "Answered": "تمت الإجابة", "Closed": "مغلق", "Accepted answer": "الإجابة المعتمدة",
    "replies": "ردود", "Teacher": "المعلمة",
    "Please sign in.": "سجّلي الدخول من فضلك.",
    "Please write the question title.": "اكتبي عنوان السؤال من فضلك.",
    "Please write the question details.": "اكتبي تفاصيل السؤال من فضلك.",
    "Please write the reply.": "اكتبي الرد من فضلك.",
    "This reply no longer exists.": "هذا الرد لم يعد موجودًا.", "This post no longer exists.": "هذا المنشور لم يعد موجودًا.",
    "You cannot thank your own post.": "لا يمكنكِ شكر منشوركِ.",
    "Only the person who asked (or the teacher) can accept an answer.": "صاحبة السؤال أو المعلمة فقط تستطيع اعتماد الإجابة.",
    "Unknown option.": "خيار غير معروف.", "You can delete only your own posts.": "يمكنكِ حذف منشوراتكِ فقط.",
    "Others already answered this question, so only the teacher can delete it.": "أجابت زميلات عن هذا السؤال، فالمعلمة وحدها تستطيع حذفه.",
})
pat(r"(\d+) new post\(s\) from students since your last visit\.", lambda m: f"{m[1]} منشور جديد من الطالبات منذ آخر زيارة لكِ.")
pat(r"(\d+) new post\(s\) on the Discussion Board\. Open it to read them\.", lambda m: f"{m[1]} منشور جديد في لوح النقاش. افتحيه لقراءتها.")
pat(r"The (question title|question details|reply) is too long \(maximum (\d+) characters\)\.",
    lambda m: f"{ {'question title':'عنوان السؤال','question details':'تفاصيل السؤال','reply':'الرد'}[m[1]] } أطول من المسموح (الحد الأقصى {m[2]} حرفًا).")
pat(r"You are posting very fast\. Please wait a few minutes \(maximum (\d+) posts in (\d+) minutes\)\.",
    lambda m: f"أنتِ تنشرين بسرعة كبيرة. انتظري بضع دقائق (الحد الأقصى {m[1]} منشورات كل {m[2]} دقائق).")
