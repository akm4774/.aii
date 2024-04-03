from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from model3 import predict_top_unique_branches
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
    #submit()
    # Process form data
    full_name = request.form.get('Full_name')
    email = request.form.get('Email')
    whatsapp = request.form.get('WhatsApp_Number')
    per_12_input = request.form.get('per_12')
    percentage = float(per_12_input) if per_12_input is not None else 0
    stream = request.form.get('branch_12')
    #rank = int(request.form.get('jee_rank')) if request.form.get('jee_rank') else 0# type: ignore
    income = int(request.form.get('Family_income')) # type: ignore
    binterests = request.form.get('selected_interests')
    course = request.form.get('interests')
    jee_rank = request.form.get('jee_rank')
    neet_rank = request.form.get('neet_rank')
    clat_rank = request.form.get('clat_rank')
    cuet_rank = request.form.get('cuet_rank')

    # Find the first non-empty rank value among the four
    rank = next((rank for rank in [jee_rank, neet_rank, clat_rank, cuet_rank] if rank), None)

    # Convert the rank to an integer if it exists
    if rank:
        rank = int(rank)
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
            b1 = "Hons"
        elif course == "finance-accounting":
            b1 = "BCom(Hons)"
        elif course == "computer-application":
            b1 = "BCA"
        elif course == "agriculture":
            b1 = "BSC(Agri)"
        elif course == "medical/pharmacy":
            b1 = "B.PHARMA"
        # Add more cases as needed
    if b1 == 'Some of the provided interests are not appropriate for the selected stream.':
        b1 = "Error"
    session['b1'] = b1
    print(b1)
    return render_template('main.html', 
                           b1=b1, b2=b2, b3=b3,
                           full_name=full_name, 
                           email=email, 
                           whatsapp=whatsapp,   
                           percentage=percentage, 
                           interest=selected_interests,
                           stream = stream,
                           rank = rank, 
                           crs=course)
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

@app.route('/medical/pharmacy')
def medicalpharmacy_page():
    return render_template('course_interests/medical/pharmacy.html')
@app.route('/paramedical')
def paramedical_page():
    return render_template('course_interests/paramedical.html')

@app.route('/technology')
def technology_page():
    return render_template('course_interests/technology.html')

def submit():
    if request.method == 'POST':
        # Extract form data
        full_name = request.form['Full_name']
        email = request.form['Email']
        whatsApp_number = int(request.form['WhatsApp_Number'])
        Father_occupation = request.form['Father_Occupation']
        family_income = int(request.form['Family_income'])
        state = request.form['State']
        city = request.form['City']
        exam = request.form['Exam']
        if exam == 'JEE':
            marks = int(request.form['jee_rank'])
        elif exam == 'NEET':
            marks = int(request.form['neet_rank'])
        elif exam == 'CLAT':
            marks = int(request.form['clat_rank'])
        elif exam == 'CUET':
            marks = int(request.form['cuet_rank'])
        branch = request.form.get('branch_12') 
        per_12 = request.form.get('per_12', 0)
        try:
            per_12_int = int(per_12)
        except:
            per_12_int = 0
        interests = request.form.get('selected_interests')

        # Create a document to insert into MongoDB
        student_data = {
            'full_name': full_name,
            'email': email,
            'whatsApp_number': whatsApp_number,
            'father_occupation': Father_occupation,
            'family_income': family_income,
            'exam': exam,
            'rank':marks,
            'branch': branch,
            'per_12': per_12_int,
            'state': state,
            'city': city,
            'interests': interests
        }

        # Insert the document into MongoDB
        collection.insert_one(student_data)

        print('Form data submitted successfully!')

if __name__ == '__main__':
    app.run(debug=True)


