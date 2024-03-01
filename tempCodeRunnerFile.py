@app.route('/submit_form_alternate', methods=['POST'])
def submit_form_alternate():
    selected_interests = request.form.get('selected_interests')
    # Print the selected interests
    print("Selected interests:", selected_interests)
    return selected_interests