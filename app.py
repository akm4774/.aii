from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from model3 import predict_top_unique_branches
from pymongo import MongoClient
from roadmaps import roadmaps
from content import branchContent
from insights import insights

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
    income = request.form.get('Family_income') # type: ignore
    binterests = request.form.get('selected_interests')
    course = request.form.get('interests')
    jee_rank = request.form.get('jee_rank')
    neet_rank = request.form.get('neet_rank')
    lnct_cet_rank = request.form.get('lnct-cet')
    clat_rank = request.form.get('clat_rank')
    cuet_rank = request.form.get('cuet_rank')

    # Find the first non-empty rank value among the four
    rank = next((rank for rank in [jee_rank, neet_rank, lnct_cet_rank, clat_rank, cuet_rank] if rank), None)

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
    # Retrieve branch content and image from branchContent dictionary
    branch_data = branchContent.get(b1)
    if branch_data:
        branch_content = branch_data.get('content', "Content not available for the top recommended branch.")
        branch_image = branch_data.get('image')
    else:
        branch_content = "Content not available for the top recommended branch."
        branch_image = None
    if b1 in insights:
        insight = insights[b1]["insight"]
        graph = insights[b1]["graph"]
    else:
        insight = ""
        graph = ""
    # Store branch data in session
    session['b1_data'] = get_branch_data(b1)
    
    session['form_data'] = {
    'full_name': full_name,
    'email': email,
    'whatsapp': whatsapp,
    'percentage': percentage,
    'interest': selected_interests,
    'stream': stream,
    'rank': rank,
    'crs': course
}

    if b2:
        session['b2'] = b2
    if b3:
        session['b3'] = b3
    # Replace \n with <br> tags in branch_content
    insight = insight.replace('\n', '<br>')

    return render_template('main.html', 
                           b1=b1, b2=b2, b3=b3,
                           full_name=full_name, 
                           email=email, 
                           whatsapp=whatsapp,   
                           percentage=percentage, 
                           interest=selected_interests,
                           stream = stream,
                           rank = rank, 
                           crs=course,
                           branch_content=branch_content,
                           branch_image=branch_image,
                           insight=insight,
                           graph=graph)
@app.route('/roadmap/<branch>')
def roadmap(branch):
    # Retrieve 'b1' from the session
    roadmap_data = roadmaps.get(branch, {})  # Get the roadmap data for the branch
    return render_template('roadmap.html', b1 = branch, roadmapData=roadmap_data, roadmaps = roadmaps)
# Call the function from model.py to predict top unique branches
@app.route('/b2')
def branch_b2():
    
    b2 = session.get('b2', '')
    b1 = session.get('b1', '')
    b3 = session.get('b3', '')
    form_data = session.get('form_data', {})
    branch_data = get_branch_data(b2)
    if branch_data:
        branch_content, branch_image, insight, graph = branch_data
        insight = insight.replace('\n', '<br>')
        return render_template('main.html', 
                               b1=b2, b2=b1, b3=b3, 
                               branch_content=branch_content, 
                               branch_image=branch_image, 
                               insight=insight, 
                               graph=graph,
                               full_name=form_data.get('full_name', ''),
                               email=form_data.get('email', ''),
                               whatsapp=form_data.get('whatsapp', ''),
                               percentage=form_data.get('percentage', 0),
                               interest=form_data.get('interest', ''),
                               stream=form_data.get('stream', ''),
                               rank=form_data.get('rank', 0),
                               crs=form_data.get('crs', ''))
    else:
        # Handle case when data is not available
        return "Data not available for branch b2"

@app.route('/b3')
def branch_b3():
    
    b3 = session.get('b3', '')
    b2 = session.get('b2', '')
    b1 = session.get('b1', '')
    branch_data = get_branch_data(b3)
    form_data = session.get('form_data', {})
    if branch_data:
        branch_content, branch_image, insight, graph = branch_data
        insight = insight.replace('\n', '<br>')
        return render_template('main.html', 
                               b1=b3, b2=b2, b3=b1, 
                               branch_content=branch_content, 
                               branch_image=branch_image, 
                               insight=insight, 
                               graph=graph,
                               full_name=form_data.get('full_name', ''),
                               email=form_data.get('email', ''),
                               whatsapp=form_data.get('whatsapp', ''),
                               percentage=form_data.get('percentage', 0),
                               interest=form_data.get('interest', ''),
                               stream=form_data.get('stream', ''),
                               rank=form_data.get('rank', 0),
                               crs=form_data.get('crs', ''))
    else:
        # Handle case when data is not available
        return "Data not available for branch b3"


def get_branch_data(branch):
    branch_data = branchContent.get(branch)
    if branch_data:
        branch_content = branch_data.get("content", "Content not available for this branch.")
        branch_image = branch_data.get('image')
    else:
        branch_content = "Content not available."
        branch_image = None

    insight = insights.get(branch, {}).get("insight", "")
    graph = insights.get(branch, {}).get("graph", "")

    return branch_content, branch_image, insight, graph




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
        elif exam == 'LNCT_CET':
            marks = int(request.form['lnct-cet'])
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


