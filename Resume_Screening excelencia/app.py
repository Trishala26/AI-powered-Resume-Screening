from flask import Flask, request, render_template, redirect, url_for
import os
import PyPDF2
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r'C:\Users\trilo\OneDrive\Desktop\Trishala\Resume_screening\uploads'

# Load your dataset
df = pd.read_csv(r'C:\Users\trilo\OneDrive\Desktop\Trishala\Resume_screening\cgpa_above_7_with_domain.csv')

@app.route('/')
def upload_form():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    if not files or all(file.filename == '' for file in files):
        return redirect(request.url)
    
    filepaths = []
    for file in files:
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            filepaths.append(filepath)
    
    # Join file paths with commas
    filepaths_str = ','.join(filepaths)
    
    return redirect(url_for('extract_and_compare', filepaths=filepaths_str))

@app.route('/extract_and_compare')
def extract_and_compare():
    filepaths_str = request.args.get('filepaths')
    if not filepaths_str:
        return "Filepaths are missing", 400

    # Split file paths back into a list
    filepaths = filepaths_str.split(',')

    results = []

    for filepath in filepaths:
        extracted_info = extract_information(filepath)
        score = compare_and_predict(extracted_info)
        score = min(score, 100)
        filename = os.path.basename(filepath)
        results.append({'filename': filename, 'score': score})

    return render_template('predict.html', results=results)

def extract_text_from_pdf(filepath):
    text = ""
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def extract_information(filepath):
    text = extract_text_from_pdf(filepath)
    skills_keywords = ['Python', 'Java', 'SQL', 'C++', 'Machine Learning', 'HTML/CSS', 'C', 'Angular', 'Javascript', 'Node.js', 'Sklearn', 'NLP', 'OpenCV']
    achievements_keywords = ['Award', 'Certified', 'Achieved', 'Led', 'Managed', 'Hackathon', 'Coding']
    projects_keywords = ['RESTful API', 'e-commerce', 'Customer Churn', 'Disease', 'Renewable energy', 'Chatbot', 'Crime', 'Tic Tac Toe', 'Portfolio']

    skills = [keyword for keyword in skills_keywords if keyword.lower() in text.lower()]
    achievements = [sentence.strip() for sentence in text.split('.') if any(keyword.lower() in sentence.lower() for keyword in achievements_keywords)]
    projects = [sentence.strip() for sentence in text.split('.') if any(keyword.lower() in sentence.lower() for keyword in projects_keywords)]

    extracted_info = {
        'text': text,
        'skills': skills,
        'achievements': achievements,
        'projects': projects
    }

    return extracted_info

def count_matching_keywords(text, keywords):
    return sum(keyword.lower() in text.lower() for keyword in keywords)

def compare_and_predict(extracted_info):
    skills_weight = 0.5
    achievements_weight = 0.2
    projects_weight = 0.6

    skills_match_count = count_matching_keywords(extracted_info['text'], extracted_info.get('skills', []))
    achievements_match_count = count_matching_keywords(extracted_info['text'], extracted_info.get('achievements', []))
    projects_match_count = count_matching_keywords(extracted_info['text'], extracted_info.get('projects', []))

    weighted_skills_match = skills_match_count * skills_weight
    weighted_achievements_match = achievements_match_count * achievements_weight
    weighted_projects_match = projects_match_count * projects_weight

    total_weighted_matches = weighted_skills_match + weighted_achievements_match + weighted_projects_match
    score = total_weighted_matches * 10

    return score

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == "__main__":
    app.run(debug=True)
