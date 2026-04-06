import re

# ── Knowledge base: keyword patterns → answers ────────────────────────────────
KNOWLEDGE_BASE = [
    # Machine Learning / AI
    (r"machine learning", "Machine learning is a branch of AI where systems learn from data to make predictions or decisions without being explicitly programmed. It includes supervised, unsupervised, and reinforcement learning."),
    (r"deep learning", "Deep learning is a subset of machine learning that uses neural networks with many layers to learn complex patterns from large amounts of data. It powers image recognition, speech recognition, and NLP."),
    (r"artificial intelligence|what is ai\b", "Artificial Intelligence (AI) is the simulation of human intelligence in machines. It includes areas like machine learning, natural language processing, computer vision, and robotics."),
    (r"neural network", "A neural network is a computational model inspired by the human brain. It consists of layers of interconnected nodes (neurons) that process data and learn patterns through training."),
    (r"natural language processing|nlp", "Natural Language Processing (NLP) is a field of AI that enables computers to understand, interpret, and generate human language. It powers chatbots, translation, sentiment analysis, and more."),
    (r"supervised learning", "Supervised learning is a type of ML where the model is trained on labeled data — each input has a known output. Examples include classification and regression tasks."),
    (r"unsupervised learning", "Unsupervised learning finds hidden patterns in data without labeled outputs. Common techniques include clustering (K-Means) and dimensionality reduction (PCA)."),
    (r"overfitting", "Overfitting occurs when a model learns the training data too well, including noise, and performs poorly on new data. It can be prevented using regularization, dropout, or more training data."),
    (r"tfidf|tf-idf|term frequency", "TF-IDF stands for Term Frequency–Inverse Document Frequency. It measures how important a word is in a document relative to a collection. Words common everywhere (like 'the') get low scores; rare but relevant words get high scores."),
    (r"logistic regression", "Logistic Regression is a classification algorithm that predicts the probability of a binary outcome. Despite its name, it's used for classification, not regression. It uses a sigmoid function to output values between 0 and 1."),
    (r"random forest", "Random Forest is an ensemble learning method that builds multiple decision trees and merges their results. It reduces overfitting and improves accuracy compared to a single decision tree."),
    (r"decision tree", "A decision tree is a flowchart-like model where each node represents a feature, each branch a decision rule, and each leaf a prediction. It's easy to interpret but prone to overfitting."),
    (r"confusion matrix", "A confusion matrix is a table used to evaluate a classification model. It shows True Positives, True Negatives, False Positives, and False Negatives, helping calculate accuracy, precision, recall, and F1-score."),
    (r"precision|recall|f1", "Precision = TP/(TP+FP) — how many predicted positives are actually positive. Recall = TP/(TP+FN) — how many actual positives were found. F1-score is the harmonic mean of both, balancing precision and recall."),
    (r"accuracy", "Accuracy is the ratio of correctly predicted instances to total instances. It's a good metric when classes are balanced, but misleading when they're imbalanced."),

    # Programming
    (r"install python|how.*python.*install", "To install Python: visit python.org, download the latest version, run the installer, and check 'Add Python to PATH'. Verify with `python --version` in your terminal."),
    (r"what is python", "Python is a high-level, interpreted programming language known for its simple syntax and readability. It's widely used in web development, data science, AI, automation, and scripting."),
    (r"what is java\b", "Java is a high-level, object-oriented programming language designed to be platform-independent ('write once, run anywhere'). It's widely used in enterprise applications, Android development, and backend systems."),
    (r"what is javascript", "JavaScript is a lightweight, interpreted programming language primarily used to make web pages interactive. It runs in the browser and also on servers via Node.js."),
    (r"what is git", "Git is a distributed version control system that tracks changes in source code. It allows multiple developers to collaborate, manage branches, and maintain a history of all changes."),
    (r"what is github", "GitHub is a cloud-based platform for hosting Git repositories. It enables collaboration, code review, issue tracking, and CI/CD workflows for software projects."),
    (r"what is an api", "An API (Application Programming Interface) is a set of rules that allows different software applications to communicate with each other. It defines how requests and responses should be structured."),
    (r"what is a database", "A database is an organized collection of structured data stored electronically. Common types include relational databases (MySQL, PostgreSQL) and NoSQL databases (MongoDB, Redis)."),
    (r"what is sql", "SQL (Structured Query Language) is a language used to manage and query relational databases. It supports operations like SELECT, INSERT, UPDATE, DELETE, and JOIN."),
    (r"what is object oriented|oop", "Object-Oriented Programming (OOP) is a programming paradigm based on objects that contain data (attributes) and behavior (methods). Key principles are Encapsulation, Inheritance, Polymorphism, and Abstraction."),

    # Science
    (r"photosynthesis", "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to produce glucose and oxygen. The equation is: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂."),
    (r"gravity", "Gravity is a fundamental force of attraction between objects with mass. On Earth, it gives objects weight and causes them to fall. Newton described it as F = Gm₁m₂/r², while Einstein described it as the curvature of spacetime."),
    (r"evolution", "Evolution is the process of change in all forms of life over generations. Charles Darwin's theory of natural selection explains how organisms with favorable traits survive and reproduce more successfully."),
    (r"dna", "DNA (Deoxyribonucleic Acid) is the molecule that carries genetic information in living organisms. It's a double helix made of nucleotide base pairs (A-T and G-C) that encode instructions for building proteins."),
    (r"black hole", "A black hole is a region in space where gravity is so strong that nothing — not even light — can escape. They form when massive stars collapse. The boundary is called the event horizon."),
    (r"climate change|global warming", "Climate change refers to long-term shifts in global temperatures and weather patterns. Since the industrial revolution, human activities (burning fossil fuels, deforestation) have been the main driver, increasing greenhouse gases."),

    # History / General Knowledge
    (r"who invented the telephone", "The telephone was invented by Alexander Graham Bell, who received the first patent for it in 1876. He made the first successful telephone call to his assistant Thomas Watson."),
    (r"who invented electricity|benjamin franklin|thomas edison", "Electricity was not invented but discovered and harnessed. Benjamin Franklin demonstrated lightning is electrical (1752). Thomas Edison developed the first practical incandescent light bulb (1879) and built the first power grid."),
    (r"who invented the internet", "The internet evolved from ARPANET, a US military project in the 1960s. Tim Berners-Lee invented the World Wide Web in 1989, which made the internet accessible to the public."),
    (r"world war 2|world war ii|ww2", "World War II (1939–1945) was a global conflict involving most of the world's nations. It was triggered by Nazi Germany's invasion of Poland. It ended with Germany's surrender in May 1945 and Japan's in September 1945 after atomic bombs were dropped on Hiroshima and Nagasaki."),
    (r"independence.*india|india.*independence", "India gained independence from British rule on August 15, 1947. The independence movement was led by figures like Mahatma Gandhi, Jawaharlal Nehru, and Subhas Chandra Bose."),

    # Health & Fitness
    (r"benefits.*exercise|exercise.*benefits|why.*exercise", "Regular exercise improves cardiovascular health, strengthens muscles and bones, boosts mental health by releasing endorphins, helps maintain healthy weight, improves sleep quality, and reduces the risk of chronic diseases like diabetes and heart disease."),
    (r"benefits.*meditation|why.*meditat", "Meditation reduces stress and anxiety, improves focus and concentration, promotes emotional health, enhances self-awareness, can reduce age-related memory loss, and helps control pain."),
    (r"healthy diet|what.*eat.*healthy|nutrition", "A healthy diet includes plenty of fruits and vegetables, whole grains, lean proteins, healthy fats (like nuts and olive oil), and adequate water. It limits processed foods, added sugars, and excess salt."),

    # Math
    (r"pythagorean theorem|pythagoras", "The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides: a² + b² = c². It was formulated by the Greek mathematician Pythagoras."),
    (r"what is calculus", "Calculus is a branch of mathematics dealing with rates of change (differentiation) and accumulation of quantities (integration). It was independently developed by Isaac Newton and Gottfried Wilhelm Leibniz in the 17th century."),
    (r"what is probability", "Probability is the measure of how likely an event is to occur, expressed as a number between 0 (impossible) and 1 (certain). P(event) = favorable outcomes / total outcomes."),

    # Task confirmations
    (r"book|reserve|schedule", "Got it! To complete this booking, you'll typically need to: 1) Choose your preferred date and time, 2) Select the location or platform, 3) Confirm your details and receive a confirmation number."),
    (r"send|email|message", "To send this: 1) Open your email/messaging app, 2) Compose your message with the correct recipient, 3) Attach any required files, 4) Hit Send. Make sure to double-check the recipient before sending!"),
    (r"delete|remove", "To delete this safely: 1) Make sure you have a backup if needed, 2) Select the item, 3) Confirm deletion. Note: deleted items may be recoverable from Trash/Recycle Bin temporarily."),
    (r"order|buy|purchase", "To place this order: 1) Add the item to your cart, 2) Enter your delivery address, 3) Choose a payment method, 4) Review and confirm. You'll receive an order confirmation via email."),
    (r"fix|debug|solve", "To fix this issue: 1) Identify the root cause by checking error logs, 2) Search for the error message online, 3) Apply the fix in a test environment first, 4) Verify the fix works, then deploy."),
]

def get_answer(question: str) -> str:
    q = question.lower().strip()
    for pattern, answer in KNOWLEDGE_BASE:
        if re.search(pattern, q):
            return answer
    # Generic fallback
    return (
        "That's a great question! Based on the context, I'd suggest looking this up on a reliable source "
        "like Wikipedia, Khan Academy, or official documentation for the most accurate and detailed answer. "
        "My knowledge base covers common topics in AI/ML, programming, science, history, and general knowledge."
    )
