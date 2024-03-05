from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from model2 import predict_top_unique_branches
from pymongo import MongoClient
from roadmaps import roadmaps
import numpy as np
app = Flask(__name__)
app.secret_key = 'secret_key'  # Set a secret key for session management
# mongo = PyMongo(app)
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client['college_recommendation_system']
collection = db['registered_data']


@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Process form data
    rank = int(request.form.get('jee_rank')) if request.form.get('jee_rank') else 0# type: ignore
    income = int(request.form.get('Family_income')) # type: ignore
    binterests = request.form.get('selected_interests')
    course = request.form.get('interests')
    print(binterests)
    selected_interests = binterests if binterests else ""
    print(selected_interests, rank, income, course)
     # Call get_recommendation function
    recommendations = predict_top_unique_branches(selected_interests, rank, course=course)
    recommendations = np.array(recommendations)
    recommendations = recommendations.tolist()
    print(recommendations)
    b1 = "None"
    if len(recommendations) == 3:
        b1, b2, b3 = recommendations
    elif len(recommendations) == 2:
        b1, b2 = recommendations
        b3 = "None"
    elif len(recommendations) == 1:
        b1 = recommendations[0]
        b2, b3 = "None", "None"
    else:
        b2, b3 = "None", "None"
    if b1 == "None":
        # Set default values based on the course
        if course == "technology":
            b1 = "Cyber Security"
        elif course == "administration":
            b1 = "Hons(Retail Mgmt & E Comm.)"
        elif course == "finance-accounting":
            b1 = "BCom(Hons)"
        elif course == "computer-application":
            b1 = "BCA"
        elif course == "agriculture":
            b1 = "BSC(Agri)"
        elif course == "pharmacology":
            b1 = "B.PHARMA"
        # Add more cases as needed
    
    session['b1'] = b1
    print(b1)
    return render_template('main.html', b1=b1, b2=b2.upper() if b2 else None, b3=b3.upper() if b3 else None, interest=selected_interests, crs=course)
 
@app.route('/roadmap')
def roadmap():
    # Retrieve 'b1' from the session
    b1 = session.get('b1', '')
    roadmap_data = roadmaps.get(b1, {})  # Get the roadmap data for the branch
    return render_template('roadmap.html', b1 = b1, roadmapData=roadmap_data, roadmaps = roadmaps)
# Call the function from model.py to predict top unique branches




#@app.route('/graph')
#def graph():
#    return render_template('graph.html') 

@app.route('/')
def index():
    return redirect(url_for('show_form'))


@app.route('/form', methods=['GET', 'POST'])
def show_form():
    if request.method == 'POST':
        # Process form submission here
        # For now, let's just print the form data
        print(request.form)
        return redirect(url_for('index'))
    return render_template('index.html')




@app.route('/display_content/<selected_branch>')
def display_content(selected_branch):
    return render_template('main.html', selected_branch=selected_branch)

@app.route('/output')
def output():
    return render_template('recommends/cs.html')

@app.route('/agriculture')
def agriculture_page():
    return render_template('course_interests/agriculture.html')

@app.route('/administration')
def administration_page():
    return render_template('course_interests/administration.html')

@app.route('/computer_app')
def computer_app_page():
    return render_template('course_interests/computer_app.html')

@app.route('/finance')
def finance_page():
    return render_template('course_interests/finance.html')

@app.route('/pharmacology')
def pharmacology_page():
    return render_template('course_interests/pharmacology.html')

@app.route('/technology')
def technology_page():
    return render_template('course_interests/technology.html')

if __name__ == '__main__':
    app.run(debug=True)


