"""Stages and topics of the lab.

Topic links point ONLY to official Nasmo booklet pages whose URLs were
checked (the Interactive Kit file and the booklet navigation). Topics with no
official page have url=None and are shown as internal topics - no link is
invented.
"""
from __future__ import annotations

BOOKLET = "https://nsmobooklets.mawhiba.sa/en/learn/"


def _u(path: str) -> str:
    return BOOKLET + path


STAGES: list[dict] = [
    {
        "id": "f", "num": 1, "title": "Fundamentals",
        "subtitle": "Build a Strong Foundation",
        "card_topics": "C++ Basics • Input/Output • Data Types • Control Statements • Functions",
        "desc": "The C++ essentials: program structure, types, input/output, "
                "decisions, loops, functions, arrays and vectors.",
        "goals": [
            "Read and write a complete C++ program with main().",
            "Choose the right type and operator for a calculation.",
            "Control the flow of a program with if, while and for.",
            "Split code into functions and understand where names are visible.",
            "Store sequences of values in arrays and vectors.",
        ],
        "topics": [
            ("Hello World!", "Your first C++ program.", _u("part-a/cpp/hello-world.html")),
            ("Structure of a Program", "Building blocks, comments and readability.", _u("part-a/cpp/structure-of-a-program.html")),
            ("Variables & Types", "Store and work with different kinds of data.", _u("part-a/cpp/variables-and-types.html")),
            ("Constants", "Values that should not change.", _u("part-a/cpp/constants.html")),
            ("Operators", "Build expressions and calculations.", _u("part-a/cpp/operators.html")),
            ("Input / Output", "Read input and produce output.", _u("part-a/cpp/input-output.html")),
            ("Statements & Control Flow", "Control the order in which code runs.", _u("part-a/cpp/statements-and-control-flow.html")),
            ("if", "Make decisions.", _u("part-a/cpp/if.html")),
            ("while", "Repeat while a condition is true.", _u("part-a/cpp/while.html")),
            ("for", "Repeat with a counter.", _u("part-a/cpp/for.html")),
            ("Functions", "Reusable blocks of logic.", _u("part-a/cpp/functions.html")),
            ("Name Visibility", "Understand where names can be used.", _u("part-a/cpp/name-visibility.html")),
            ("Arrays", "Fixed-size sequences of values.", _u("part-a/cpp/arrays.html")),
            ("Vectors", "Flexible sequences using std::vector.", _u("part-a/cpp/vectors.html")),
        ],
    },
    {
        "id": "s1", "num": 2, "title": "Stage 1", "subtitle": "Modular Algorithms",
        "card_topics": "Modular Arithmetic • Simulation • Case Work • Constructive • Greedy",
        "desc": "Five core problem-solving patterns that appear again and again.",
        "goals": [
            "Use % correctly, including negative numbers and fast exponentiation.",
            "Follow a process step by step in code (simulation).",
            "Split a problem into complete, non-overlapping cases.",
            "Build an object that satisfies given rules (constructive).",
            "Decide when a greedy choice is safe - and when it is not.",
        ],
        "topics": [
            ("Modular Arithmetics", "mod, modular rules, negatives, fast exponentiation and modular inverse.", _u("part-b/modular-arithmetics.html")),
            ("Simulation", "Follow a process exactly, step by step.", _u("part-b/simulation.html")),
            ("Case Work", "Split a problem into complete, non-overlapping cases.", _u("part-b/casework.html")),
            ("Constructive Algorithms", "Build an object that satisfies the required rules.", _u("part-b/constructive.html")),
            ("Greedy Algorithms", "Make a locally best choice and test when it remains globally valid.", _u("part-b/greedy.html")),
        ],
    },
    {
        "id": "s2", "num": 3, "title": "Stage 2", "subtitle": "Data Structures & Algorithms",
        "card_topics": "Sets • Maps • Time Complexity • Sorting • Binary Search",
        "desc": "Containers, bits, complexity, sorting and searching.",
        "goals": [
            "Use set and map to remove duplicates and count frequencies.",
            "Estimate how running time grows with input size.",
            "Sort data and use sorting as a tool.",
            "Write a correct binary search (and binary search on the answer).",
            "Work with bits and represent subsets as bitmasks.",
        ],
        "topics": [
            ("Sets", "Unique values, ordered sets and duplicate removal.", _u("part-c/cpp/sets.html")),
            ("Maps", "Key-value storage and frequency counting.", _u("part-c/cpp/maps.html")),
            ("Bitwise Operations", "Represent and manipulate information at the bit level.", _u("part-c/cpp/bitwise-operations.html")),
            ("Bit Manipulation Tricks", "Use bit-level patterns in algorithmic problems.", _u("part-c/bit-manipulation.html")),
            ("Time Complexity", "Reason about how runtime grows with input size.", _u("part-c/time-complexity.html")),
            ("Sorting", "Order data and use sorting as a problem-solving tool.", _u("part-c/sorting.html")),
            ("Binary Search", "Cut a sorted search space in half repeatedly.", _u("part-c/binary-search.html")),
            ("Generating Subsets Using Bitmasks", "Represent each subset as a bit pattern.", _u("part-c/generating-subsets-using-bitmasks.html")),
        ],
    },
    {
        "id": "s3", "num": 4, "title": "Stage 3", "subtitle": "Advanced Problem Solving",
        "card_topics": "Backtracking • Dynamic Programming • Number Theory • Primes",
        "desc": "Search, dynamic programming and number theory.",
        "goals": [
            "Explore all choices with backtracking and undo them correctly.",
            "Define a DP state and recurrence and fill the table.",
            "List divisors and test primes efficiently.",
            "Generate primes with the Sieve of Eratosthenes.",
            "Break a number into its prime factors.",
        ],
        "topics": [
            ("Backtracking", "Build choices step by step and undo them when needed.", _u("part-d/backtracking.html")),
            ("Dynamic Programming", "Store repeated subproblem results and reuse them.", _u("part-d/dynamic-programming.html")),
            ("Number Theory", "Use mathematical structure to simplify algorithms.", None),
            ("Divisors & Primes", "Work with factors, divisibility and prime structure.", None),
            ("Sieve of Eratosthenes", "Generate primes efficiently up to a limit.", None),
            ("Prime Factorization", "Break an integer into its prime factors.", None),
        ],
    },
    {
        "id": "s4", "num": 5, "title": "Stage 4", "subtitle": "Graphs & Advanced Structures",
        "card_topics": "Graphs • DFS • BFS • Trees • Segment Trees",
        "desc": "Graphs, trees and advanced data structures.",
        "goals": [
            "Represent a graph with adjacency lists.",
            "Traverse a graph with DFS and BFS and count components.",
            "Work with trees and dynamic programming on trees.",
            "Use sqrt decomposition and ordered sets for range/set queries.",
            "Answer range queries and updates with segment trees.",
        ],
        "topics": [
            ("Graphs", "Model relationships between objects and connections.", _u("part-e/graphs/intro.html")),
            ("Depth-First Search (DFS)", "Explore a graph deeply using recursive or stack-based traversal.", _u("part-e/graphs/dfs.html")),
            ("Connected Components", "Find groups of vertices connected to one another.", _u("part-e/graphs/components.html")),
            ("Breadth-First Search (BFS)", "Explore layer by layer and find shortest paths in unweighted graphs.", _u("part-e/graphs/bfs.html")),
            ("Trees", "Use graph structure with a unique path between nodes.", _u("part-e/trees/intro.html")),
            ("Dynamic Programming on Trees", "Combine dynamic programming with tree structure.", _u("part-e/trees/dp-on-trees.html")),
            ("Square Root Decomposition", "Split data into blocks to speed up range work.", _u("part-e/ds/sqrt-decomposition.html")),
            ("Ordered Sets", "Use ordered structures for dynamic set queries.", _u("part-e/ds/ordered-sets.html")),
            ("Segment Trees", "Answer range queries and updates efficiently.", _u("part-e/ds/segment-trees.html")),
        ],
    },
]

STAGE_BY_ID = {s["id"]: s for s in STAGES}
STAGE_IDS = [s["id"] for s in STAGES]

OFFICIAL_OVERVIEW = _u("overview/introduction.html")


def stage_label(stage: dict) -> str:
    """'Fundamentals' or 'Stage 1 - Modular Algorithms' style label."""
    if stage["id"] == "f":
        return stage["title"]
    return f'{stage["title"]} — {stage["subtitle"]}'
