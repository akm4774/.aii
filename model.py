import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load the data and train the model
data = pd.read_csv("static/Btechnew 2.csv")
tfidf_vectorizer = TfidfVectorizer()
X_tfidf = tfidf_vectorizer.fit_transform(data['Interest'])
X = data[["Interest", "Institute Name", "Course"]]
y = data["Branch"]
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_tfidf, y)
data['Closing Rank'] = pd.to_numeric(data['Closing Rank'], errors='coerce')

def preprocess_course(course):
    match course.lower():
        case "technology":
            return "BTech"
        case "administration":
            return "BBA"
        case "finance and accounting":
            return "BCom"
        case "computer application":
            return "BCA"
        case "agriculture":
            return "BSC(Agriculture)"
        case "pharmacology":
            return "B.Pharma"
        case _:
            return course

def predict_top_unique_branches(user_interest, user_rank=None, course=None):
    top_n = 3
    
    # Preprocess the course input
    if course is not None:
        course = preprocess_course(course)

    # Filter data based on the provided course
    if course is not None:
        filtered_data = data[data['Course'] == course].copy()
    else:
        filtered_data = data.copy()  # Use the entire dataset if no course specified

    if user_rank is not None:
        # Filter data based on rank and percentage if provided
        filtered_data['Closing Rank'] = pd.to_numeric(filtered_data['Closing Rank'], errors='coerce')
        filtered_data = filtered_data[filtered_data['Closing Rank'] >= user_rank]

    if filtered_data.empty:
        # If no branches are found after filtering, return an empty list
        return []

    # Transform user input using the existing tfidf_vectorizer
    user_input_tfidf = tfidf_vectorizer.transform([user_interest])
    # Predict branch probabilities using the trained model
    branch_probs = model.predict_proba(user_input_tfidf)

    # Get branch names and corresponding probabilities
    branch_names = model.classes_
    branch_probabilities = branch_probs[0]

    # Create a DataFrame for easy sorting
    result_df = pd.DataFrame({'Branch': branch_names, 'Probability': branch_probabilities})

    # Sort by probabilities in descending order
    result_df = result_df.sort_values(by='Probability', ascending=False)

    # Get top N unique branches
    top_unique_branches = result_df['Branch'].unique()[:top_n]

    # Move 'CSE' to the last position if present
    if 'CSE' in top_unique_branches:
        top_unique_branches = [branch for branch in top_unique_branches if branch != 'CSE'] + ['CSE']

    return top_unique_branches

# Function to save the trained model
def save_model(model, filename):
    try:
        joblib.dump(model, filename)
        print("Model saved successfully as", filename)
    except Exception as e:
        print("Error occurred while saving the model:", str(e))

# Save the trained model
save_model(model, "rf_model.pkl")

# Function to load the saved model
def load_model(filename):
    try:
        loaded_model = joblib.load(filename)
        print("Model loaded successfully from", filename)
        return loaded_model
    except Exception as e:
        print("Error occurred while loading the model:", str(e))
        return None

# Load the saved model
loaded_model = load_model("rf_model.pkl")

# Function to get recommendation based on user input
def get_recommendation(user_interest, user_rank, course):
    print(user_interest, user_rank)
    top_unique_branches = predict_top_unique_branches(user_interest, user_rank, course)
    return top_unique_branches
