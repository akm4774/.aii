import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load the data
def load_data(file_path):
    return pd.read_csv(file_path)

# Preprocess course names
def preprocess_course(course):
    course_mapping = {
        "technology": "BTech",
        "administration": "BBA",
        "finance-accounting": "BCom",
        "computer-application": "BCA",
        "agriculture": "BSC(Agriculture)",
        "medical/pharmacy": "MEDICAL",
        "paramedical": "PARAMEDICAL"
    }
    return course_mapping.get(course.lower(), course)

# Preprocess user interests
def preprocess_interests(interests):
    if pd.isna(interests):
        return ["Your selected interests are not appropriate."]
    elif not interests.strip():
        return ["You did not provide any interests."]
    return interests.lower().split(', ')

# Train the model
def train_model(data):
    tfidf_vectorizer = TfidfVectorizer()
    X_tfidf = tfidf_vectorizer.fit_transform(data['Interest'])
    model = RandomForestClassifier(n_estimators=100, random_state=34)
    model.fit(X_tfidf, data["Branch"])
    return model, tfidf_vectorizer

# Predict top unique branches
def predict_top_unique_branches(user_interest, user_rank=None, top_n=3, course=None):
    user_interests = preprocess_interests(user_interest)
    course = preprocess_course(course)
    if course.lower() not in ['medical/pharmacy', 'technology']:
        user_rank = None

    data = load_data("static/data-final.csv")
    filtered_data = data if course is None else data[data['Course'].str.lower() == course.lower()]

    dataset_interests = set(filtered_data['Interest'].str.lower().str.split(',').explode().unique())
    if not set(user_interests).issubset(dataset_interests):
        return "User interests are not compatible with available data."

    if user_rank is not None:
        filtered_data = filtered_data[pd.to_numeric(filtered_data['Closing Rank'], errors='coerce') >= user_rank]

    if filtered_data.empty:
        return "No branches available based on provided criteria."

    model, tfidf_vectorizer = train_model(filtered_data)
    save_model(model, "rf_model.pkl")

    user_input_tfidf = tfidf_vectorizer.transform([' '.join(user_interests)])
    branch_probs = model.predict_proba(user_input_tfidf)
    branch_names = model.classes_
    branch_probabilities = branch_probs[0]

    result_df = pd.DataFrame({'Branch': branch_names, 'Probability': branch_probabilities})
    result_df = result_df.sort_values(by='Probability', ascending=False)

    top_unique_branches = result_df['Branch'].unique()[:top_n]

    if 'Computer Science and Engineering (CSE)' in top_unique_branches and user_rank is not None and user_rank > 80000:
      top_unique_branches = [branch for branch in top_unique_branches if branch != 'Computer Science and Engineering (CSE)'] + ['Computer Science and Engineering (CSE)']


    if len(top_unique_branches) == 0:
        return "No top branches found for the given criteria."

    return top_unique_branches

# Save the trained model
def save_model(model, filename):
    try:
        joblib.dump(model, filename)
        print("Model saved successfully as", filename)
    except Exception as e:
        print("Error occurred while saving the model:", str(e))