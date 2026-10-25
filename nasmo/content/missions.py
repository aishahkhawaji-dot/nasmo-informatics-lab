"""Built-in training missions (4 per stage, 2-3 steps each).

This is an internal training sequence made by the lab - it is NOT an official
division made by the Nasmo organisers.

Step types
  understand / bug / choice  -> multiple choice (`options`, `answer` = index)
  predict / complete         -> short text answer (`answer` = accepted list)
  solve                      -> final answer + the student's code (saved for
                                the teacher); completes only when the answer is
                                right AND some code was written
  explain                    -> free text checked against a concept rubric

Every `predict` step shows a complete program: tests compile and run it with
g++ and compare with the stored answer (tests/test_content.py).
`verify` holds a reference program for other steps for the same purpose.
"""
from __future__ import annotations

TYPE_LABELS = {
    "understand": "Understand the Code",
    "predict": "Predict the Output",
    "bug": "Find the Bug",
    "complete": "Complete the Code",
    "solve": "Solve the Problem",
    "choice": "Choose the Correct Answer",
    "explain": "Explain Your Reasoning",
}
TYPE_LABELS_AR = {
    "understand": "افهمي الكود",
    "predict": "توقّعي الناتج",
    "bug": "اكتشفي الخطأ",
    "complete": "أكملي الكود",
    "solve": "حلّي المسألة",
    "choice": "اختاري الإجابة الصحيحة",
    "explain": "اشرحي تفكيرك",
}
MCQ_TYPES = {"understand", "bug", "choice"}
TEXT_TYPES = {"predict", "complete", "solve"}


def mc(sid, type_, prompt, options, answer, explain_en, explain_ar, hint="", code=None, verify=None):
    return {"id": sid, "type": type_, "prompt": prompt, "code": code, "options": options,
            "answer": answer, "hint": hint, "explain_en": explain_en,
            "explain_ar": explain_ar, "verify": verify}


def txt(sid, type_, prompt, accept, explain_en, explain_ar, hint="", code=None,
        verify=None, match="words", min_code_chars=0, placeholder=""):
    return {"id": sid, "type": type_, "prompt": prompt, "code": code,
            "answer": list(accept), "match": match, "hint": hint,
            "explain_en": explain_en, "explain_ar": explain_ar, "verify": verify,
            "min_code_chars": min_code_chars, "placeholder": placeholder}


def ex(sid, prompt, rubric, explain_en, explain_ar, hint="", code=None):
    return {"id": sid, "type": "explain", "prompt": prompt, "code": code,
            "rubric": rubric, "hint": hint, "explain_en": explain_en,
            "explain_ar": explain_ar, "verify": None}


# =====================================================================
# FUNDAMENTALS
# =====================================================================
F1 = {
    "id": "f-1", "stage": "f", "title": "Hello, C++!",
    "summary": "Program structure, types and operators.",
    "topics": ["Hello World!", "Structure of a Program", "Variables & Types", "Constants"],
    "steps": [
        mc("a", "understand",
           "Which line is the entry point - where every C++ program starts running?",
           ["#include <iostream>", "using namespace std;", "int main() {", "return 0;"], 2,
           "Execution always begins at main(). The #include line only makes cout available.",
           "تبدأ كل برامج C++ بتنفيذ الدالة main()، أما سطر include فيجعل cout متاحًا فقط.",
           hint="Look for the function every program must have.",
           code='#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, Nasmo!" << endl;\n    return 0;\n}'),
        txt("b", "predict", "What does this program print?", ["3 1 3.5"],
            "Integer division 7 / 2 gives 3, 7 % 2 gives the remainder 1, and (double)7 / 2 is real division = 3.5.",
            "القسمة بين عددين صحيحين تعطي ناتجًا صحيحًا (3)، والباقي 1، وبعد تحويل أحدهما إلى double تصبح القسمة حقيقية 3.5.",
            hint="a / b with two ints drops the fraction.",
            code='#include <iostream>\nusing namespace std;\n\nint main() {\n    int a = 7, b = 2;\n    cout << a / b << " " << a % b << " " << (double)a / b << endl;\n    return 0;\n}',
            placeholder="e.g. 1 2 3"),
    ],
}

F2 = {
    "id": "f-2", "stage": "f", "title": "Input, Output & Operators",
    "summary": "Read values with cin and combine them with operators.",
    "topics": ["Operators", "Input / Output"],
    "steps": [
        mc("a", "bug", "This program does not compile. What is the correct fix?",
           ["Change `cin << a << b;` to `cin >> a >> b;`",
            "Add `return 1;` before the last brace",
            "Change `int` to `float`",
            "Replace `cout` with `print`"], 0,
           "cin extracts values with >> (into the variables). << is for cout (output).",
           "نستخدم >> مع cin لقراءة القيم، و << مع cout للطباعة.",
           hint="Which arrows point 'into' the variable?",
           code='#include <iostream>\nusing namespace std;\n\nint main() {\n    int a, b;\n    cin << a << b;\n    cout << a + b << endl;\n    return 0;\n}'),
        txt("b", "complete", "Fill the blank so the program prints 1 + 2 + ... + n.",
            ["i<=n", "n>=i", "i<n+1", "1+n>i"],
            "The loop must include i = n, so the condition is i <= n.",
            "الحلقة يجب أن تشمل i = n، لذلك الشرط هو i <= n.",
            hint="The last value added must be n itself.",
            code='#include <iostream>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    int sum = 0;\n    for (int i = 1; ______; i++) sum += i;\n    cout << sum << endl;\n    return 0;\n}',
            match="nospace", placeholder="the condition only",
            verify={"source": '#include <iostream>\nusing namespace std;\nint main(){int n;cin>>n;int sum=0;for(int i=1;i<=n;i++)sum+=i;cout<<sum<<endl;}',
                    "stdin": "5", "expect": "15"}),
    ],
}

F3 = {
    "id": "f-3", "stage": "f", "title": "Decisions & Loops",
    "summary": "if, while, for, break and continue.",
    "topics": ["Statements & Control Flow", "if", "while", "for"],
    "steps": [
        txt("a", "predict", "What does this program print?", ["16"],
            "Even i are skipped (continue). Odd i are added until i = 9 > 7 triggers break: 1 + 3 + 5 + 7 = 16.",
            "الأعداد الزوجية تُتخطّى بـ continue، ونجمع الفردية 1+3+5+7=16 ثم يوقف break الحلقة عند 9.",
            hint="Trace i = 1..10 and write down total after each step.",
            code='#include <iostream>\nusing namespace std;\n\nint main() {\n    int total = 0;\n    for (int i = 1; i <= 10; i++) {\n        if (i % 2 == 0) continue;\n        if (i > 7) break;\n        total += i;\n    }\n    cout << total << endl;\n    return 0;\n}'),
        txt("b", "solve", "How many integers from 1 to 100 are divisible by 3 or by 5?", ["47"],
            "33 multiples of 3, 20 multiples of 5, minus 6 counted twice (multiples of 15): 33 + 20 - 6 = 47. A loop with `if (i % 3 == 0 || i % 5 == 0)` gives the same.",
            "33 من مضاعفات 3 و20 من مضاعفات 5 ونطرح 6 مضاعفات مشتركة (15): 33+20-6=47.",
            hint="Use || (or) - and do not count numbers like 15 twice.",
            min_code_chars=25, placeholder="the count",
            verify={"source": '#include <iostream>\nint main(){int c=0;for(int i=1;i<=100;i++)if(i%3==0||i%5==0)c++;std::cout<<c;}', "expect": "47"}),
    ],
}

F4 = {
    "id": "f-4", "stage": "f", "title": "Functions, Arrays & Vectors",
    "summary": "Name visibility, array bounds and std::vector.",
    "topics": ["Functions", "Name Visibility", "Arrays", "Vectors"],
    "steps": [
        txt("a", "predict", "What does this program print?", ["10 5"],
            "show() sees the global x (10). Inside main the local x (5) hides the global one.",
            "الدالة show() ترى المتغير العام x=10، بينما داخل main يُخفي المتغير المحلي x=5 المتغير العام.",
            hint="Which x can show() see?",
            code='#include <iostream>\nusing namespace std;\n\nint x = 10;\nvoid show() { cout << x << " "; }\n\nint main() {\n    int x = 5;\n    show();\n    cout << x << endl;\n    return 0;\n}'),
        mc("b", "bug", "The program should print the sum of the 5 elements but reads outside the array. What is the fix?",
           ["Change `i <= 5` to `i < 5`", "Change `int a[5]` to `int a[4]`",
            "Change `sum += a[i]` to `sum = a[i]`", "Start the loop at `i = 1`"], 0,
           "Valid indexes of a[5] are 0..4. With i <= 5 the loop reads a[5], which does not exist (undefined behaviour).",
           "الفهارس الصحيحة للمصفوفة ذات 5 عناصر هي 0..4، والشرط i <= 5 يقرأ عنصرًا غير موجود.",
           hint="How many elements does a[5] have, and what is the last index?",
           code='#include <iostream>\nusing namespace std;\n\nint main() {\n    int a[5] = {1, 2, 3, 4, 5};\n    int sum = 0;\n    for (int i = 0; i <= 5; i++) sum += a[i];\n    cout << sum << endl;\n    return 0;\n}'),
        mc("c", "choice", "Why is std::vector usually better than a plain array when the size is read from the input?",
           ["Its size can be chosen at run time and it can grow with push_back",
            "It runs the program faster than any array",
            "It never needs #include",
            "It automatically sorts its elements"], 0,
           "A vector manages its own memory: you can create it with any size at run time and add elements with push_back.",
           "المتجه vector يدير ذاكرته بنفسه: يمكن تحديد حجمه أثناء التشغيل وإضافة عناصر بـ push_back.",
           hint="Think about `int a[n]` when n is only known after reading input."),
    ],
}

# =====================================================================
# STAGE 1 - MODULAR ALGORITHMS
# =====================================================================
S1_1 = {
    "id": "s1-1", "stage": "s1", "title": "Modular Arithmetic",
    "summary": "Negative remainders and fast exponentiation.",
    "topics": ["Modular Arithmetics"],
    "steps": [
        txt("a", "predict", "What does this program print?", ["-1 2"],
            "In C++ the remainder takes the sign of the left operand: -7 % 3 = -1. Adding m and taking % m again gives the non-negative remainder 2.",
            "إشارة الباقي في C++ تتبع المقسوم: -7 % 3 = -1، ولتحويله إلى باقٍ غير سالب نضيف m ونأخذ % m مرة أخرى فنحصل على 2.",
            hint="C++ keeps the sign of the first operand.",
            code='#include <iostream>\nusing namespace std;\n\nint main() {\n    int a = -7, m = 3;\n    cout << a % m << " " << ((a % m) + m) % m << endl;\n    return 0;\n}'),
        txt("b", "complete", "Fill the blank: when the lowest bit of e is 1, multiply the result by b (mod m).",
            ["res*b%m", "b*res%m", "(res*b)%m", "(b*res)%m", "res*b%m;", "res=res*b%m"],
            "If e is odd, the current power of b contributes to the answer: res = res * b % m.",
            "عندما يكون e فرديًا يدخل b الحالي في الناتج: res = res * b % m.",
            hint="Do not forget the % m.",
            code='long long power(long long b, long long e, long long m) {\n    long long res = 1;\n    b %= m;\n    while (e > 0) {\n        if (e & 1) res = ______;\n        b = b * b % m;\n        e >>= 1;\n    }\n    return res;\n}',
            match="nospace", placeholder="the expression",
            verify={"source": '#include <iostream>\nlong long power(long long b,long long e,long long m){long long res=1;b%=m;while(e>0){if(e&1)res=res*b%m;b=b*b%m;e>>=1;}return res;}\nint main(){std::cout<<power(3,20,7);}', "expect": "2"}),
    ],
}

S1_2 = {
    "id": "s1-2", "stage": "s1", "title": "Simulation",
    "summary": "Follow a process exactly, step by step.",
    "topics": ["Simulation"],
    "steps": [
        txt("a", "predict", "What does this program print? (5 lamps start OFF; round k toggles every k-th lamp.)", ["10010"],
            "A lamp is toggled once for every divisor of its number. It ends ON only if it has an odd number of divisors, i.e. perfect squares: lamps 1 and 4.",
            "كل مصباح يُبدَّل بعدد قواسم رقمه، ويبقى مضاءً إذا كان عدد القواسم فرديًا (المربعات الكاملة): المصباحان 1 و4.",
            hint="Count how many rounds touch each lamp.",
            code='#include <iostream>\nusing namespace std;\n\nint main() {\n    bool on[6] = {};\n    for (int k = 1; k <= 5; k++)\n        for (int i = k; i <= 5; i += k)\n            on[i] = !on[i];\n    for (int i = 1; i <= 5; i++) cout << on[i];\n    cout << endl;\n    return 0;\n}'),
        txt("b", "solve",
            "People 1..7 stand in a queue (1 at the front). Repeat: the front person leaves, then the new front person moves to the back. Who is the last person left?",
            ["6"],
            "Queue: 1 2 3 4 5 6 7 -> (1 leaves, 2 to back) 3 4 5 6 7 2 -> 5 6 7 2 4 -> 7 2 4 6 -> 4 6 2 -> 2 6 -> 6.",
            "نحاكي العملية خطوة بخطوة بقائمة انتظار (queue): تنتهي بالشخص رقم 6.",
            hint="Use a queue: pop the front, then pop again and push to the back.",
            min_code_chars=40, placeholder="the person's number",
            verify={"source": '#include <bits/stdc++.h>\nint main(){std::queue<int>q;for(int i=1;i<=7;i++)q.push(i);while(q.size()>1){q.pop();int x=q.front();q.pop();q.push(x);}std::cout<<q.front();}', "expect": "6"}),
    ],
}

S1_3 = {
    "id": "s1-3", "stage": "s1", "title": "Case Work",
    "summary": "Complete, non-overlapping cases.",
    "topics": ["Case Work"],
    "steps": [
        mc("a", "choice", "To classify a triangle by its sides, which set of cases is complete and does NOT overlap?",
           ["All three equal / exactly two equal / all different",
            "All three equal / at least two equal / all different",
            "a == b / b == c",
            "Acute / obtuse"], 0,
           "'At least two equal' also contains the all-equal triangle, so those cases overlap. 'Exactly two equal' keeps the cases separate and covers everything.",
           "عبارة «اثنان على الأقل متساويان» تشمل أيضًا المثلث متساوي الأضلاع فتتداخل الحالات؛ أما «اثنان بالضبط» فتجعل الحالات منفصلة وكاملة.",
           hint="Can one triangle fall in two cases at once?"),
        mc("b", "bug", "isLeap(2024) returns false although 2024 is a leap year. Which version is correct?",
           ["return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;",
            "return y % 4 == 0 || y % 400 == 0;",
            "return y % 100 == 0 && y % 400 == 0;",
            "return y % 4 != 0 || y % 100 == 0;"], 0,
           "A leap year is divisible by 4 but not by 100, unless it is divisible by 400. The bug was y % 100 == 0 instead of != 0.",
           "السنة الكبيسة تقبل القسمة على 4 ولا تقبلها على 100، إلا إذا قبلت القسمة على 400. الخطأ كان في استخدام == بدل != مع 100.",
           hint="Check 1900 (not leap) and 2000 (leap) too.",
           code='bool isLeap(int y) {\n    return y % 4 == 0 && y % 100 == 0 || y % 400 == 0;\n}'),
    ],
}

S1_4 = {
    "id": "s1-4", "stage": "s1", "title": "Constructive & Greedy",
    "summary": "Build an answer, and know when greedy fails.",
    "topics": ["Constructive Algorithms", "Greedy Algorithms"],
    "steps": [
        mc("a", "choice", "Construct 5 DIFFERENT integers whose sum is 0 using the idea 'pair x with -x'. Which array works?",
           ["-2 -1 0 1 2", "1 2 3 4 5", "-1 -1 0 1 1", "0 0 0 0 0"], 0,
           "Pairs (-2,2) and (-1,1) cancel, and 0 fills the odd slot. The other arrays are not zero-sum or repeat values.",
           "الأزواج (-2,2) و(-1,1) تلغي بعضها، والصفر يكمل العدد الفردي. بقية المصفوفات إما مجموعها لا يساوي صفرًا أو فيها تكرار.",
           hint="Distinct means no repeated value."),
        txt("b", "solve", "Coins: 1, 5, 10, 25 cents. What is the fewest number of coins to pay exactly 63 cents?", ["6"],
            "Greedy works for this coin system: 25 + 25 + 10 + 1 + 1 + 1 = 63 -> 6 coins.",
            "في هذا النظام من العملات يصلح الاختيار الجشع: 25+25+10+1+1+1 = 63 أي 6 عملات.",
            hint="Take the biggest coin that still fits, repeatedly.",
            min_code_chars=30, placeholder="number of coins",
            verify={"source": '#include <iostream>\nint main(){int a=63,c=0;int v[]={25,10,5,1};for(int x:v){c+=a/x;a%=x;}std::cout<<c;}', "expect": "6"}),
        ex("c", "For coins {1, 3, 4} and amount 6, explain why always taking the largest coin first is NOT optimal.",
           {"min_words": 8,
            "groups": [[r"3\s*\+\s*3", r"two coins", r"\b2 coins", r"2\s*coin"],
                       [r"4\s*\+\s*1\s*\+\s*1", r"three coins", r"\b3 coins", r"3\s*coin", r"largest", r"biggest"]],
            "need": 2},
           "Greedy picks 4 + 1 + 1 = three coins, but 3 + 3 uses only two coins. A locally best choice is not always globally best.",
           "الاختيار الجشع يأخذ 4+1+1 أي ثلاث عملات، بينما 3+3 تحتاج عملتين فقط؛ أفضل خيار محلي ليس دائمًا الأفضل عامًا.",
           hint="Compare what greedy gives with another way to make 6."),
    ],
}

# =====================================================================
# STAGE 2 - DATA STRUCTURES & ALGORITHMS
# =====================================================================
S2_1 = {
    "id": "s2-1", "stage": "s2", "title": "Sets & Maps",
    "summary": "Remove duplicates and count frequencies.",
    "topics": ["Sets", "Maps"],
    "steps": [
        txt("a", "predict", "What does this program print?", ["4: 1 2 3 4", "4:1 2 3 4"],
            "A set stores each value once and keeps them sorted: {1, 2, 3, 4} - size 4.",
            "المجموعة set تخزّن كل قيمة مرة واحدة وبترتيب تصاعدي: {1,2,3,4} وحجمها 4.",
            hint="Duplicates are ignored and the order is sorted.",
            code='#include <iostream>\n#include <set>\nusing namespace std;\n\nint main() {\n    set<int> s;\n    int a[] = {4, 1, 3, 4, 1, 2};\n    for (int x : a) s.insert(x);\n    cout << s.size() << ":";\n    for (int x : s) cout << " " << x;\n    cout << endl;\n    return 0;\n}',
            placeholder="exact output"),
        txt("b", "complete", "Fill the blank to count how many times each value appears.",
            ["freq[x]++", "++freq[x]", "freq[x]+=1", "freq[x]=freq[x]+1", "freq[x]++;"],
            "A map creates a missing key with value 0, so freq[x]++ counts occurrences.",
            "الخريطة map تنشئ المفتاح المفقود بقيمة 0، لذلك freq[x]++ تعدّ مرات الظهور.",
            hint="Increase the counter stored at key x.",
            code='map<int, int> freq;\nfor (int x : a) ______;',
            match="nospace", placeholder="the statement",
            verify={"source": '#include <bits/stdc++.h>\nusing namespace std;\nint main(){int a[]={1,2,2,3,3,3};map<int,int> freq;for(int x:a) freq[x]++;cout<<freq[3];}', "expect": "3"}),
    ],
}

S2_2 = {
    "id": "s2-2", "stage": "s2", "title": "Complexity & Sorting",
    "summary": "Estimate running time and sort with a comparator.",
    "topics": ["Time Complexity", "Sorting"],
    "steps": [
        mc("a", "choice", "How many times is work() called, in Big-O terms?",
           ["O(n)", "O(n log n)", "O(n^2)", "O(2^n)"], 2,
           "The inner loop runs n, n-1, ..., 1 times: about n(n+1)/2 calls, which is O(n^2).",
           "الحلقة الداخلية تعمل n ثم n-1 ... حتى 1 مرة أي نحو n(n+1)/2، وهذا O(n²).",
           hint="Add up how many times the inner loop runs for each i.",
           code='for (int i = 0; i < n; i++)\n    for (int j = i; j < n; j++)\n        work();'),
        txt("b", "predict", "What does this program print?", ["9 7 5 2 1"],
            "greater<int>() makes sort order the numbers from largest to smallest.",
            "المقارن greater<int>() يجعل sort يرتّب الأعداد تنازليًا.",
            hint="Which direction does greater<int> sort?",
            code='#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    vector<int> v = {5, 2, 9, 1, 7};\n    sort(v.begin(), v.end(), greater<int>());\n    for (int x : v) cout << x << " ";\n    cout << endl;\n    return 0;\n}'),
    ],
}

S2_3 = {
    "id": "s2-3", "stage": "s2", "title": "Binary Search",
    "summary": "Halve the search space - and avoid the infinite loop.",
    "topics": ["Binary Search"],
    "steps": [
        mc("a", "bug", "This loop never ends for some inputs. What is the fix?",
           ["Change `lo = mid;` to `lo = mid + 1;`", "Change `hi = mid;` to `hi = mid - 1;`",
            "Change `lo < hi` to `lo <= hi`", "Compute `mid = (lo + hi) * 2;`"], 0,
           "When hi = lo + 1 and a[lo] < x, mid equals lo, so lo = mid never moves. Using lo = mid + 1 always shrinks the range.",
           "عندما يكون hi = lo + 1 ويكون a[lo] < x فإن mid = lo فلا يتحرك lo أبدًا. استخدام lo = mid + 1 يضمن تقلّص المدى دائمًا.",
           hint="Try lo = 3, hi = 4 and a[3] < x.",
           code='int lo = 0, hi = n - 1;      // find first index with a[i] >= x\nwhile (lo < hi) {\n    int mid = (lo + hi) / 2;\n    if (a[mid] < x) lo = mid;\n    else hi = mid;\n}'),
        txt("b", "solve", "Binary search on the answer: what is the smallest integer k such that k * k >= 1000?", ["32"],
            "31 * 31 = 961 < 1000 and 32 * 32 = 1024 >= 1000, so k = 32. Binary search finds it in about log2(1000) steps.",
            "31×31=961 أقل من 1000 و32×32=1024 أكبر منه، إذن k=32. البحث الثنائي يجدها في نحو log2(1000) خطوة.",
            hint="The condition k*k >= 1000 is false for small k and true for large k.",
            min_code_chars=30, placeholder="k",
            verify={"source": '#include <iostream>\nint main(){long long lo=0,hi=1000;while(lo<hi){long long m=(lo+hi)/2;if(m*m>=1000)hi=m;else lo=m+1;}std::cout<<lo;}', "expect": "32"}),
    ],
}

S2_4 = {
    "id": "s2-4", "stage": "s2", "title": "Bits & Subsets",
    "summary": "Bitwise operators and bitmask subsets.",
    "topics": ["Bitwise Operations", "Bit Manipulation Tricks", "Generating Subsets Using Bitmasks"],
    "steps": [
        txt("a", "predict", "What does this program print?", ["1 7 6 16 6"],
            "5 = 101, 3 = 011: AND = 001 = 1, OR = 111 = 7, XOR = 110 = 6; 1 << 4 = 16; 13 >> 1 = 6.",
            "5 = 101 و3 = 011: AND = 1، OR = 7، XOR = 6؛ والإزاحة 1<<4 = 16؛ و13>>1 = 6.",
            hint="Write 5 and 3 in binary first.",
            code='#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << (5 & 3) << " " << (5 | 3) << " " << (5 ^ 3) << " "\n         << (1 << 4) << " " << (13 >> 1) << endl;\n    return 0;\n}'),
        txt("b", "solve", "For n = 4 items, each subset is a mask from 0 to 15. How many masks have exactly 2 bits set?", ["6"],
            "That is choosing 2 of 4 items: C(4,2) = 6 (0011, 0101, 0110, 1001, 1010, 1100).",
            "هذا اختيار عنصرين من أربعة: C(4,2) = 6 (0011, 0101, 0110, 1001, 1010, 1100).",
            hint="Loop over all masks and count bits with __builtin_popcount.",
            min_code_chars=30, placeholder="the count",
            verify={"source": '#include <iostream>\nint main(){int c=0;for(int m=0;m<16;m++)if(__builtin_popcount(m)==2)c++;std::cout<<c;}', "expect": "6"}),
        mc("c", "choice", "Which expression tests whether item i (0-based) is inside the subset represented by `mask`?",
           ["mask & (1 << i)", "mask | (1 << i)", "mask ^ i", "(mask >> i) == 0"], 0,
           "1 << i has only bit i set. AND-ing keeps that bit: the result is non-zero exactly when item i is in the subset.",
           "العدد 1 << i فيه البت i فقط، وعملية AND تُبقي هذا البت: النتيجة غير صفرية فقط إذا كان العنصر i ضمن المجموعة.",
           hint="You need an operation that keeps only bit i."),
    ],
}

# =====================================================================
# STAGE 3 - ADVANCED PROBLEM SOLVING
# =====================================================================
S3_1 = {
    "id": "s3-1", "stage": "s3", "title": "Backtracking",
    "summary": "Try a choice, explore, undo it.",
    "topics": ["Backtracking"],
    "steps": [
        txt("a", "predict", "What does this program print?", ["00 01 10 11"],
            "gen tries '0' first and then '1' at each position, so strings of length 2 appear in this order.",
            "الدالة gen تجرّب '0' ثم '1' في كل موضع، فتظهر السلاسل بطول 2 بهذا الترتيب.",
            hint="Draw the recursion tree: first digit 0 -> second digit 0, 1; then first digit 1 ...",
            code='#include <bits/stdc++.h>\nusing namespace std;\n\nvoid gen(string cur, int n) {\n    if ((int)cur.size() == n) { cout << cur << " "; return; }\n    gen(cur + "0", n);\n    gen(cur + "1", n);\n}\n\nint main() {\n    gen("", 2);\n    cout << endl;\n}'),
        mc("b", "understand", "What is the purpose of the line `used[i] = false;` after the recursive call?",
           ["Undo the choice so other branches can use element i again",
            "Mark that element i was used",
            "Stop the recursion early",
            "Free the memory of element i"], 0,
           "Backtracking = choose, explore, un-choose. Resetting used[i] restores the state for the next choice in the loop.",
           "الرجوع للخلف = اختيار ثم استكشاف ثم تراجع. إعادة used[i] إلى false تعيد الحالة كما كانت لتجربة الاختيار التالي.",
           hint="What would happen to the next iteration if used[i] stayed true?",
           code='void permute(vector<int>& cur) {\n    if ((int)cur.size() == n) { print(cur); return; }\n    for (int i = 0; i < n; i++) {\n        if (used[i]) continue;\n        used[i] = true;\n        cur.push_back(i);\n        permute(cur);\n        cur.pop_back();\n        used[i] = false;   // <- this line\n    }\n}'),
    ],
}

S3_2 = {
    "id": "s3-2", "stage": "s3", "title": "Dynamic Programming",
    "summary": "Store sub-results and reuse them.",
    "topics": ["Dynamic Programming"],
    "steps": [
        txt("a", "complete", "dp[i] = number of ways to climb i stairs taking 1 or 2 steps at a time. Fill the blank.",
            ["dp[i-1]+dp[i-2]", "dp[i-2]+dp[i-1]", "dp[i-1]+dp[i-2];", "dp[i-2]+dp[i-1];"],
            "The last move was either 1 step (from stair i-1) or 2 steps (from stair i-2), so the ways add up.",
            "آخر حركة إما خطوة واحدة (من الدرجة i-1) أو خطوتان (من i-2)، فنجمع الطرق.",
            hint="Think about the very last move.",
            code='dp[0] = 1; dp[1] = 1;\nfor (int i = 2; i <= n; i++)\n    dp[i] = ______;',
            match="nospace", placeholder="the expression",
            verify={"source": '#include <iostream>\nint main(){int n=10;long long dp[20];dp[0]=1;dp[1]=1;for(int i=2;i<=n;i++)dp[i]=dp[i-1]+dp[i-2];std::cout<<dp[n];}', "expect": "89"}),
        txt("b", "solve", "In how many different ways can you climb 10 stairs taking 1 or 2 steps at a time?", ["89"],
            "dp = 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89 -> dp[10] = 89.",
            "تتابع الطرق: 1، 1، 2، 3، 5، 8، 13، 21، 34، 55، 89 فيكون dp[10] = 89.",
            hint="Use the recurrence from the previous step.",
            min_code_chars=30, placeholder="number of ways",
            verify={"source": '#include <iostream>\nint main(){long long a=1,b=1;for(int i=2;i<=10;i++){long long c=a+b;a=b;b=c;}std::cout<<b;}', "expect": "89"}),
    ],
}

S3_3 = {
    "id": "s3-3", "stage": "s3", "title": "Divisors & Number Theory",
    "summary": "Divisors come in pairs.",
    "topics": ["Number Theory", "Divisors & Primes"],
    "steps": [
        txt("a", "predict", "What does this program print?", ["9"],
            "36 has divisors 1, 2, 3, 4, 6, 9, 12, 18, 36 = 9. The pair (6, 6) is counted once because i == n / i.",
            "للعدد 36 تسعة قواسم: 1,2,3,4,6,9,12,18,36. الزوج (6,6) يُعدّ مرة واحدة لأن i == n/i.",
            hint="List the divisor pairs (i, 36 / i).",
            code='#include <iostream>\nusing namespace std;\n\nint main() {\n    int n = 36, cnt = 0;\n    for (int i = 1; (long long)i * i <= n; i++) {\n        if (n % i == 0) {\n            cnt++;\n            if (i != n / i) cnt++;\n        }\n    }\n    cout << cnt << endl;\n}'),
        mc("b", "choice", "Why is it enough to loop i only up to sqrt(n) when listing the divisors of n?",
           ["Divisors come in pairs (i, n / i) and one of each pair is <= sqrt(n)",
            "Numbers above sqrt(n) are always prime",
            "The computer cannot loop past sqrt(n)",
            "Because n must be a perfect square"], 0,
           "If i divides n then n / i divides n too, and min(i, n/i) <= sqrt(n). So the loop finds every pair in O(sqrt(n)).",
           "إذا قسم i العدد n فإن n/i يقسمه أيضًا، وأحدهما لا يتجاوز sqrt(n). لذلك تجد الحلقة كل الأزواج في O(√n).",
           hint="Pair every divisor d with n / d."),
    ],
}

S3_4 = {
    "id": "s3-4", "stage": "s3", "title": "Sieve & Prime Factorization",
    "summary": "Generate primes fast and factor numbers.",
    "topics": ["Sieve of Eratosthenes", "Prime Factorization"],
    "steps": [
        txt("a", "predict", "What does this program print?", ["10"],
            "The sieve crosses out multiples of each prime. The primes up to 30 are 2, 3, 5, 7, 11, 13, 17, 19, 23, 29 - ten of them.",
            "المنخل يشطب مضاعفات كل عدد أولي. الأعداد الأولية حتى 30 هي 2,3,5,7,11,13,17,19,23,29 أي عشرة.",
            hint="List the primes up to 30.",
            code='#include <iostream>\nusing namespace std;\n\nint main() {\n    const int N = 30;\n    bool composite[N + 1] = {};\n    int count = 0;\n    for (int i = 2; i <= N; i++) {\n        if (composite[i]) continue;\n        count++;\n        for (int j = i * i; j <= N; j += i) composite[j] = true;\n    }\n    cout << count << endl;\n}'),
        txt("b", "solve", "How many positive divisors does 360 have? (Hint: 360 = 2^3 x 3^2 x 5.)", ["24"],
            "With 360 = 2^3 * 3^2 * 5^1 the number of divisors is (3+1)(2+1)(1+1) = 24.",
            "360 = 2³ × 3² × 5، وعدد القواسم = (3+1)(2+1)(1+1) = 24.",
            hint="Add 1 to each exponent and multiply.",
            min_code_chars=30, placeholder="number of divisors",
            verify={"source": '#include <iostream>\nint main(){int n=360,c=0;for(int i=1;i<=n;i++)if(n%i==0)c++;std::cout<<c;}', "expect": "24"}),
    ],
}

# =====================================================================
# STAGE 4 - GRAPHS & ADVANCED STRUCTURES
# =====================================================================
S4_1 = {
    "id": "s4-1", "stage": "s4", "title": "Graph Basics",
    "summary": "Adjacency lists and degrees.",
    "topics": ["Graphs"],
    "steps": [
        mc("a", "choice", "A graph has 5 vertices and 6 undirected edges stored as adjacency lists. How many entries are there in total across all the lists?",
           ["12", "6", "11", "30"], 0,
           "Each undirected edge (u, v) is stored twice: v in u's list and u in v's list. So 2 x 6 = 12 (the sum of degrees).",
           "كل ضلع غير موجّه (u,v) يُخزَّن مرتين، فيكون المجموع 2×6 = 12 وهو مجموع الدرجات.",
           hint="How many times does one edge appear?"),
        txt("b", "predict", "What does this program print?", ["3 2 2 1"],
            "Vertex 1 has edges to 2, 3, 4 (degree 3); vertices 2 and 3 have degree 2; vertex 4 has degree 1.",
            "الرأس 1 مرتبط بـ 2 و3 و4 (درجته 3)، والرأسان 2 و3 درجة كل منهما 2، والرأس 4 درجته 1.",
            hint="Each edge adds 1 to the degree of both its ends.",
            code='#include <iostream>\nusing namespace std;\n\nint main() {\n    int n = 4;\n    int edges[][2] = {{1, 2}, {1, 3}, {1, 4}, {2, 3}};\n    int deg[5] = {};\n    for (auto& e : edges) { deg[e[0]]++; deg[e[1]]++; }\n    for (int v = 1; v <= n; v++) cout << deg[v] << " ";\n    cout << endl;\n}'),
    ],
}

S4_2 = {
    "id": "s4-2", "stage": "s4", "title": "DFS & Connected Components",
    "summary": "Explore deeply; count the groups.",
    "topics": ["Depth-First Search (DFS)", "Connected Components"],
    "steps": [
        txt("a", "predict", "What does this program print?", ["1 2 4 5 3"],
            "DFS goes as deep as possible first: 1 -> 2 -> 4 -> 5, then backtracks to 1 and visits 3.",
            "يتعمق DFS قدر الإمكان: 1 ثم 2 ثم 4 ثم 5، ثم يرجع إلى 1 ويزور 3.",
            hint="Follow the first unvisited neighbour each time.",
            code='#include <bits/stdc++.h>\nusing namespace std;\n\nvector<int> adj[6];\nbool vis[6];\n\nvoid dfs(int u) {\n    vis[u] = true;\n    cout << u << " ";\n    for (int v : adj[u])\n        if (!vis[v]) dfs(v);\n}\n\nint main() {\n    int e[][2] = {{1, 2}, {1, 3}, {2, 4}, {4, 5}};\n    for (auto& x : e) { adj[x[0]].push_back(x[1]); adj[x[1]].push_back(x[0]); }\n    dfs(1);\n    cout << endl;\n}'),
        txt("b", "solve", "A graph has 9 vertices and the edges 1-2, 2-3, 4-5, 6-7, 7-8, 6-8. How many connected components does it have?", ["4"],
            "Components: {1,2,3}, {4,5}, {6,7,8} and the isolated vertex {9} -> 4.",
            "المركّبات: {1,2,3} و{4,5} و{6,7,8} والرأس المنفرد {9} فيكون العدد 4.",
            hint="Do not forget vertices that have no edges.",
            min_code_chars=40, placeholder="number of components",
            verify={"source": '#include <bits/stdc++.h>\nusing namespace std;\nvector<int> g[10];bool v[10];void d(int u){v[u]=1;for(int w:g[u])if(!v[w])d(w);}\nint main(){int e[][2]={{1,2},{2,3},{4,5},{6,7},{7,8},{6,8}};for(auto&x:e){g[x[0]].push_back(x[1]);g[x[1]].push_back(x[0]);}int c=0;for(int i=1;i<=9;i++)if(!v[i]){c++;d(i);}cout<<c;}', "expect": "4"}),
    ],
}

S4_3 = {
    "id": "s4-3", "stage": "s4", "title": "BFS & Trees",
    "summary": "Shortest paths in unweighted graphs; tree facts.",
    "topics": ["Breadth-First Search (BFS)", "Trees"],
    "steps": [
        txt("a", "solve", "Unweighted graph with edges 1-2, 1-3, 2-4, 3-4, 4-5, 5-6. What is the fewest number of edges on a path from 1 to 6?", ["4"],
            "BFS levels from 1: {1} -> {2,3} -> {4} -> {5} -> {6}. Vertex 6 is on level 4.",
            "مستويات BFS من الرأس 1: {1} ثم {2,3} ثم {4} ثم {5} ثم {6}، فالرأس 6 في المستوى 4.",
            hint="Run BFS and count levels.",
            min_code_chars=40, placeholder="number of edges",
            verify={"source": '#include <bits/stdc++.h>\nusing namespace std;\nvector<int> g[7];int main(){int e[][2]={{1,2},{1,3},{2,4},{3,4},{4,5},{5,6}};for(auto&x:e){g[x[0]].push_back(x[1]);g[x[1]].push_back(x[0]);}vector<int> d(7,-1);queue<int>q;d[1]=0;q.push(1);while(!q.empty()){int u=q.front();q.pop();for(int v:g[u])if(d[v]<0){d[v]=d[u]+1;q.push(v);}}cout<<d[6];}', "expect": "4"}),
        mc("b", "bug", "On a graph that contains a cycle this BFS never stops. What is missing?",
           ["Check/mark whether v was already reached before pushing it",
            "Replace the queue with a stack",
            "Start from vertex 0 instead of s",
            "Use `dist[u] - 1` instead of `dist[u] + 1`"], 0,
           "Without a visited check, vertices on a cycle are pushed again and again. Set dist[v] only when it is still unreached (for example dist[v] == -1).",
           "بدون التحقق من الزيارة تُدفع رؤوس الدورة إلى الطابور مرارًا. يجب تعيين dist[v] فقط إذا لم نصل إليه من قبل (مثلًا dist[v] == -1).",
           hint="What stops you from visiting the same vertex twice?",
           code='dist[s] = 0;\nq.push(s);\nwhile (!q.empty()) {\n    int u = q.front(); q.pop();\n    for (int v : adj[u]) {\n        dist[v] = dist[u] + 1;\n        q.push(v);\n    }\n}'),
        mc("c", "choice", "A tree with n vertices has exactly how many edges?",
           ["n - 1", "n", "n + 1", "2n"], 0,
           "A tree is connected and has no cycles: every vertex except the root hangs on exactly one parent edge, giving n - 1 edges.",
           "الشجرة متصلة وبلا دورات؛ كل رأس عدا الجذر له ضلع واحد إلى أبيه، فيكون عدد الأضلاع n - 1.",
           hint="Count one edge for every non-root vertex."),
    ],
}

S4_4 = {
    "id": "s4-4", "stage": "s4", "title": "Advanced Structures",
    "summary": "Segment trees, ordered sets and sqrt decomposition.",
    "topics": ["Square Root Decomposition", "Ordered Sets", "Segment Trees"],
    "steps": [
        mc("a", "choice", "A segment tree over n elements answers a range-sum query and a point update in:",
           ["O(log n) each", "O(n) each", "O(1) each", "O(n^2) each"], 0,
           "The tree has height about log2(n), and a query or update touches a constant number of nodes per level.",
           "ارتفاع الشجرة نحو log2(n) والاستعلام أو التحديث يمرّ على عدد ثابت من العقد في كل مستوى.",
           hint="Think about the height of the tree."),
        mc("b", "understand", "What does `*s.lower_bound(25)` print for this set?",
           ["30", "20", "25", "40"], 0,
           "lower_bound returns an iterator to the first element that is NOT smaller than 25 - that is 30.",
           "الدالة lower_bound تعيد أول عنصر ليس أصغر من 25، وهو 30.",
           hint="25 is not in the set: which is the next larger value?",
           code='#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    set<int> s = {10, 20, 30, 40};\n    cout << *s.lower_bound(25) << endl;\n}',
           verify={"source": '#include <bits/stdc++.h>\nusing namespace std;\nint main(){set<int> s={10,20,30,40};cout<<*s.lower_bound(25);}', "expect": "30"}),
        ex("c", "Explain why splitting an array of n elements into blocks of about sqrt(n) elements makes a range-sum query take about O(sqrt(n)) time.",
           {"min_words": 12,
            "groups": [[r"block"],
                       [r"sqrt|square root|√"],
                       [r"partial|at most two|two blocks|whole blocks|full blocks|complete blocks|precomputed|stored sum"]],
            "need": 2},
           "A query covers whole blocks (each answered in O(1) from a stored sum - at most about sqrt(n) of them) plus at most two partial blocks (at most about 2*sqrt(n) single elements).",
           "الاستعلام يغطي كتلًا كاملة (لكل منها مجموع مخزّن بزمن O(1) وعددها نحو √n) وكتلتين جزئيتين على الأكثر (نحو 2√n عنصرًا مفردًا).",
           hint="Count whole blocks and leftover elements separately."),
    ],
}

MISSIONS: list[dict] = [F1, F2, F3, F4, S1_1, S1_2, S1_3, S1_4,
                        S2_1, S2_2, S2_3, S2_4, S3_1, S3_2, S3_3, S3_4,
                        S4_1, S4_2, S4_3, S4_4]
MISSION_BY_ID = {m["id"]: m for m in MISSIONS}
