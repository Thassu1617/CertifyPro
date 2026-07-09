from app import create_app
from database import db
from database.models import Course, Exam, Question
from datetime import datetime

COURSES = [
    {
        "code": "PY101",
        "name": "Python Basics",
        "desc": "Learn Python programming from scratch. Covers variables, data types, control flow, functions, object-oriented programming, file handling, and more. Perfect for beginners starting their coding journey.",
        "credits": 4,
        "exam_title": "Python Fundamentals Assessment",
        "questions": [
            {"q": "What is the correct file extension for Python files?", "a": ".pyth", "b": ".pt", "c": ".py", "d": ".p", "ans": "C"},
            {"q": "Which of the following is a valid variable name in Python?", "a": "2var", "b": "my-var", "c": "_myVar", "d": "my var", "ans": "C"},
            {"q": "What data type is the result of: type(3.14)?", "a": "int", "b": "float", "c": "double", "d": "decimal", "ans": "B"},
            {"q": "Which keyword is used to define a function in Python?", "a": "function", "b": "def", "c": "func", "d": "define", "ans": "B"},
            {"q": "What does len('Hello') return?", "a": "4", "b": "5", "c": "6", "d": "3", "ans": "B"},
            {"q": "Which of the following is a Python tuple?", "a": "[1,2,3]", "b": "(1,2,3)", "c": "{1,2,3}", "d": "{1:2,3:4}", "ans": "B"},
            {"q": "What will print(2 ** 3) output?", "a": "5", "b": "6", "c": "8", "d": "9", "ans": "C"},
            {"q": "Which loop is used to iterate over a sequence?", "a": "while", "b": "for", "c": "do-while", "d": "repeat", "ans": "B"},
            {"q": "What is the correct way to create a list in Python?", "a": "list = (1,2,3)", "b": "list = {1,2,3}", "c": "list = [1,2,3]", "d": "list = <1,2,3>", "ans": "C"},
            {"q": "Which statement is used to catch exceptions in Python?", "a": "catch", "b": "except", "c": "error", "d": "try...except", "ans": "D"},
            {"q": "What does the '==' operator do?", "a": "Assigns value", "b": "Compares equality", "c": "Checks identity", "d": "Calculates", "ans": "B"},
            {"q": "What is the output of print(type([]))?", "a": "<class 'tuple'>", "b": "<class 'list'>", "c": "<class 'dict'>", "d": "<class 'set'>", "ans": "B"},
            {"q": "Which method adds an element to a list?", "a": "push()", "b": "add()", "c": "append()", "d": "insert()", "ans": "C"},
            {"q": "What is the correct way to create a dictionary?", "a": "d = [1:2]", "b": "d = (1:2)", "c": "d = {'key': 'value'}", "d": "d = <key:value>", "ans": "C"},
            {"q": "Which function converts a string to an integer?", "a": "str()", "b": "float()", "c": "int()", "d": "bool()", "ans": "C"},
        ],
    },
    {
        "code": "ML101",
        "name": "Machine Learning Basics",
        "desc": "Introduction to Machine Learning concepts including supervised and unsupervised learning, regression, classification, clustering, model evaluation, and hands-on with popular ML algorithms.",
        "credits": 3,
        "exam_title": "Machine Learning Fundamentals Exam",
        "questions": [
            {"q": "What is Machine Learning?", "a": "Programming rules manually", "b": "Learning from data without explicit programming", "c": "Writing complex algorithms", "d": "Creating databases", "ans": "B"},
            {"q": "Which of these is a supervised learning algorithm?", "a": "K-Means", "b": "Linear Regression", "c": "PCA", "d": "DBSCAN", "ans": "B"},
            {"q": "What is overfitting?", "a": "Model too simple", "b": "Model learns noise", "c": "Model underfits data", "d": "Model is perfect", "ans": "B"},
            {"q": "What does SVM stand for?", "a": "Simple Vector Machine", "b": "Support Vector Machine", "c": "Supervised Virtual Machine", "d": "System Vector Model", "ans": "B"},
            {"q": "Which algorithm is used for classification?", "a": "Linear Regression", "b": "Logistic Regression", "c": "K-Means", "d": "PCA", "ans": "B"},
            {"q": "What is the purpose of train-test split?", "a": "Speed up training", "b": "Evaluate model performance", "c": "Reduce data size", "d": "Visualize data", "ans": "B"},
            {"q": "What does 'clustering' mean?", "a": "Sorting data", "b": "Grouping similar items", "c": "Predicting values", "d": "Reducing dimensions", "ans": "B"},
            {"q": "What is a confusion matrix used for?", "a": "Data visualization", "b": "Classification evaluation", "c": "Feature selection", "d": "Data cleaning", "ans": "B"},
            {"q": "What is the output of a regression model?", "a": "Classes", "b": "Continuous value", "c": "Categories", "d": "Clusters", "ans": "B"},
            {"q": "What does the term 'feature' refer to?", "a": "Model output", "b": "Input variable", "c": "Training data", "d": "Algorithm type", "ans": "B"},
            {"q": "Which library is commonly used for ML in Python?", "a": "Matplotlib", "b": "Scikit-learn", "c": "Flask", "d": "SQLAlchemy", "ans": "B"},
            {"q": "What is the bias-variance tradeoff?", "a": "Model size issue", "b": "Balance between underfitting and overfitting", "c": "Data quality issue", "d": "Training speed issue", "ans": "B"},
            {"q": "What type of learning uses labeled data?", "a": "Unsupervised", "b": "Supervised", "c": "Reinforcement", "d": "Semi-supervised", "ans": "B"},
            {"q": "What is the role of the learning rate?", "a": "Speed of data loading", "b": "Steps size in gradient descent", "c": "Accuracy threshold", "d": "Data split ratio", "ans": "B"},
            {"q": "What does PCA stand for?", "a": "Principal Component Analysis", "b": "Primary Class Algorithm", "c": "Process Control Analysis", "d": "Probability Calculation Array", "ans": "A"},
        ],
    },
    {
        "code": "AI101",
        "name": "Artificial Intelligence Basics",
        "desc": "Explore the world of Artificial Intelligence. Topics include intelligent agents, search algorithms, knowledge representation, natural language processing, computer vision, and AI ethics.",
        "credits": 3,
        "exam_title": "Artificial Intelligence Assessment",
        "questions": [
            {"q": "What is Artificial Intelligence?", "a": "Making machines think like humans", "b": "Storing data", "c": "Building websites", "d": "Creating databases", "ans": "A"},
            {"q": "Which is NOT a type of AI?", "a": "Narrow AI", "b": "General AI", "c": "Super AI", "d": "Virtual AI", "ans": "D"},
            {"q": "What is the Turing Test used for?", "a": "Testing code quality", "b": "Testing machine intelligence", "c": "Testing data accuracy", "d": "Testing network speed", "ans": "B"},
            {"q": "What is NLP?", "a": "Natural Programming Language", "b": "Natural Language Processing", "c": "Neural Learning Protocol", "d": "Network Logic Process", "ans": "B"},
            {"q": "Which search algorithm uses a queue?", "a": "DFS", "b": "BFS", "c": "A*", "d": "Hill Climbing", "ans": "B"},
            {"q": "What is an intelligent agent?", "a": "A bot that follows rules", "b": "An entity that perceives and acts", "c": "A database system", "d": "A web crawler", "ans": "B"},
            {"q": "What does 'heuristic' mean in AI?", "a": "Exact solution", "b": "Problem-solving approach", "c": "Database query", "d": "Random guess", "ans": "B"},
            {"q": "Which AI technique mimics neurons?", "a": "Decision Trees", "b": "Neural Networks", "c": "SVM", "d": "K-Means", "ans": "B"},
            {"q": "What is computer vision?", "a": "Making computers see", "b": "Making computers process images", "c": "Building monitors", "d": "Writing code", "ans": "B"},
            {"q": "What is reinforcement learning?", "a": "Learning with rewards", "b": "Learning from labeled data", "c": "Learning from clusters", "d": "Learning from rules", "ans": "A"},
            {"q": "What does a knowledge graph represent?", "a": "Code structure", "b": "Entities and their relationships", "c": "File directory", "d": "Network topology", "ans": "B"},
            {"q": "Which algorithm is used for pathfinding?", "a": "K-Means", "b": "A*", "c": "PCA", "d": "SVM", "ans": "B"},
            {"q": "What is the goal of AI ethics?", "a": "Speed improvement", "b": "Responsible AI development", "c": "Cost reduction", "d": "Feature addition", "ans": "B"},
            {"q": "What is a perceptron?", "a": "A type of sensor", "b": "A simple neural network", "c": "A database model", "d": "A search algorithm", "ans": "B"},
            {"q": "What does 'deep learning' use?", "a": "Simple linear models", "b": "Deep neural networks", "c": "Statistical tests", "d": "Rule-based systems", "ans": "B"},
        ],
    },
    {
        "code": "DB101",
        "name": "Database Management Systems",
        "desc": "Comprehensive introduction to databases. Learn about relational database design, SQL queries, normalization, indexing, transactions, ACID properties, and working with database systems.",
        "credits": 3,
        "exam_title": "Database Systems Exam",
        "questions": [
            {"q": "What does SQL stand for?", "a": "Simple Query Logic", "b": "Structured Query Language", "c": "System Query Language", "d": "Standard Query Logic", "ans": "B"},
            {"q": "Which command retrieves data from a table?", "a": "GET", "b": "SELECT", "c": "FETCH", "d": "EXTRACT", "ans": "B"},
            {"q": "What is a primary key?", "a": "A unique identifier for a record", "b": "A foreign reference", "c": "An index column", "d": "A default value", "ans": "A"},
            {"q": "What does JOIN do?", "a": "Combines rows from two tables", "b": "Deletes duplicate data", "c": "Creates a new table", "d": "Sorts the data", "ans": "A"},
            {"q": "What is normalization?", "a": "Increasing data size", "b": "Reducing redundancy", "c": "Encrypting data", "d": "Backing up data", "ans": "B"},
            {"q": "Which clause filters records?", "a": "SORT BY", "b": "WHERE", "c": "GROUP BY", "d": "ORDER BY", "ans": "B"},
            {"q": "What is a foreign key?", "a": "Links two tables", "b": "A unique key", "c": "An encrypted key", "d": "A backup key", "ans": "A"},
            {"q": "What does ACID stand for?", "a": "Atomicity, Consistency, Isolation, Durability", "b": "Accuracy, Consistency, Integrity, Data", "c": "Atomic, Consistent, Integrated, Durable", "d": "Access, Control, Isolation, Data", "ans": "A"},
            {"q": "Which SQL command adds data?", "a": "ADD", "b": "INSERT", "c": "CREATE", "d": "UPDATE", "ans": "B"},
            {"q": "What is an index used for?", "a": "Data encryption", "b": "Faster searching", "c": "Data deletion", "d": "Table creation", "ans": "B"},
            {"q": "What does GROUP BY do?", "a": "Groups rows with same values", "b": "Sorts the table", "c": "Filters records", "d": "Joins tables", "ans": "A"},
            {"q": "What is a transaction?", "a": "A single SQL query", "b": "A unit of work", "c": "A database backup", "d": "A table creation", "ans": "B"},
            {"q": "What is a view in SQL?", "a": "A stored query", "b": "A physical table", "c": "An index", "d": "A backup file", "ans": "A"},
            {"q": "Which keyword removes duplicate rows?", "a": "UNIQUE", "b": "DISTINCT", "c": "DIFFERENT", "d": "EXCLUDE", "ans": "B"},
            {"q": "What does DELETE command do?", "a": "Removes a table", "b": "Removes records", "c": "Removes database", "d": "Drops constraints", "ans": "B"},
        ],
    },
    {
        "code": "WEB101",
        "name": "Web Development Basics",
        "desc": "Build modern websites from scratch. Learn HTML5, CSS3, JavaScript, responsive design, front-end frameworks, and basic backend integration for complete web development.",
        "credits": 3,
        "exam_title": "Web Development Fundamentals Test",
        "questions": [
            {"q": "What does HTML stand for?", "a": "Hyper Text Markup Language", "b": "High Tech Modern Language", "c": "Hyper Transfer Markup Language", "d": "Home Tool Markup Language", "ans": "A"},
            {"q": "Which tag is used for the largest heading?", "a": "<h6>", "b": "<h1>", "c": "<heading>", "d": "<head>", "ans": "B"},
            {"q": "What does CSS stand for?", "a": "Computer Style Sheets", "b": "Cascading Style Sheets", "c": "Creative Style System", "d": "Code Style Sheets", "ans": "B"},
            {"q": "Which tag creates a hyperlink?", "a": "<link>", "b": "<a>", "c": "<href>", "d": "<url>", "ans": "B"},
            {"q": "What is the correct HTML for inserting an image?", "a": "<img src='image.jpg'>", "b": "<image src='image.jpg'>", "c": "<img href='image.jpg'>", "d": "<pic src='image.jpg'>", "ans": "A"},
            {"q": "Which CSS property changes text color?", "a": "font-color", "b": "text-color", "c": "color", "d": "text-style", "ans": "C"},
            {"q": "What does JavaScript add to a web page?", "a": "Styling", "b": "Structure", "c": "Interactivity", "d": "Database", "ans": "C"},
            {"q": "Which tag creates a paragraph?", "a": "<para>", "b": "<paragraph>", "c": "<p>", "d": "<text>", "ans": "C"},
            {"q": "What is a responsive design?", "a": "Fast loading design", "b": "Design that works on all devices", "c": "Colorful design", "d": "Animated design", "ans": "B"},
            {"q": "Which HTML tag is used for lists?", "a": "<list>", "b": "<ul> or <ol>", "c": "<li>", "d": "<item>", "ans": "B"},
            {"q": "What does the DOM stand for?", "a": "Document Object Model", "b": "Data Object Management", "c": "Document Orientation Mode", "d": "Display Object Module", "ans": "A"},
            {"q": "Which framework is used for CSS?", "a": "React", "b": "Bootstrap", "c": "Django", "d": "Flask", "ans": "B"},
            {"q": "What is the correct HTML for a form?", "a": "<form>", "b": "<input>", "c": "<field>", "d": "<formfield>", "ans": "A"},
            {"q": "How do you add a comment in HTML?", "a": "// comment", "b": "<!-- comment -->", "c": "/* comment */", "d": "# comment", "ans": "B"},
            {"q": "What does API stand for?", "a": "Application Programming Interface", "b": "Application Process Integration", "c": "Automated Program Interface", "d": "Application Protocol Interface", "ans": "A"},
        ],
    },
]


def seed():
    for c in COURSES:
        existing = Course.query.filter_by(course_code=c["code"]).first()
        if existing:
            continue

        course = Course(
            course_code=c["code"],
            course_name=c["name"],
            description=c["desc"],
            credits=c["credits"],
        )
        db.session.add(course)
        db.session.flush()

        exam = Exam(
            title=c["exam_title"],
            course_id=course.id,
            duration_minutes=30,
            total_questions=len(c["questions"]),
            passing_percentage=40,
            max_marks=len(c["questions"]),
            is_published=True,
        )
        db.session.add(exam)
        db.session.flush()

        for q_data in c["questions"]:
            q = Question(
                exam_id=exam.id,
                question_text=q_data["q"],
                option_a=q_data["a"],
                option_b=q_data["b"],
                option_c=q_data["c"],
                option_d=q_data["d"],
                correct_answer=q_data["ans"],
                marks=1,
            )
            db.session.add(q)

        print(f"Seeded: {c['code']} - {c['name']} ({len(c['questions'])} questions)")

    db.session.commit()
    print("Seeding complete!")


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed()