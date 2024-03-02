import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib

# Function to load the data
def load_data(file_path):
    return pd.read_csv(file_path)

# Function to preprocess course names
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
            return "B.PHARMA"
        case _:
            return course

# Function to preprocess interests
def preprocess_interests(interests):
    if pd.isna(interests):
        return ["Your selected interests are not appropriate."]
    elif not interests.strip():  # Empty string
        return ["You did not provide any interests."]
    return interests.lower().split(', ')

# Function to train the model
def train_model(data):
    tfidf_vectorizer = TfidfVectorizer()
    X_tfidf = tfidf_vectorizer.fit_transform(data['Interest'])
    model = RandomForestClassifier(n_estimators=100, random_state=34)
    model.fit(X_tfidf, data["Branch"])
    return model, tfidf_vectorizer

# Function to preprocess user input
def preprocess_user_input(user_interest, user_rank, course):
    user_interest = preprocess_interests(user_interest)
    course = preprocess_course(course)
    return user_interest, user_rank, course

# Function to predict top unique branches
def predict_top_unique_branches(user_interest, user_rank=None, course=None):
    top_n=3
    # Preprocess user input
    user_interest, user_rank, course = preprocess_user_input(user_interest, user_rank, course)

    # Check if any interest entry is NULL or empty
    if "Your selected interests are not appropriate." in user_interest:
        return user_interest
    elif "You did not provide any interests." in user_interest:
        return user_interest

    # Load the data
    data = load_data("static/btech.csv")

    # Filter data based on the provided course
    if course is not None:
        filtered_data = data[data['Course'] == course].copy()
    else:
        filtered_data = data.copy()  # Use the entire dataset if no course specified

    # Check if the user's interest is within the range of interests present in the dataset
    dataset_interests = filtered_data['Interest'].str.lower().str.split(',').explode().unique()
    user_interests = set(user_interest)
    if not user_interests.issubset(dataset_interests):
        return []

    if user_rank is not None:
        # Filter data based on rank
        filtered_data = filtered_data[pd.to_numeric(filtered_data['Closing Rank'], errors='coerce') >= user_rank]

    if filtered_data.empty:
        return []

    # Train the model based on filtered data
    model, tfidf_vectorizer = train_model(filtered_data)

    # Save the trained model
    #save_model(model, "rf_model.pkl")

    # Predict branch based on interests only
    user_input_tfidf = tfidf_vectorizer.transform([' '.join(user_interest)])
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
    if 'CSE' in top_unique_branches and user_rank is not None:
        if user_rank > 80000:
            top_unique_branches = [branch for branch in top_unique_branches if branch != 'CSE'] + ['CSE']

    return top_unique_branches

# Function to save the trained model
def save_model(model, filename):
    try:
        joblib.dump(model, filename)
        print("Model saved successfully as", filename)
    except Exception as e:
        print("Error occurred while saving the model:", str(e))

# Function to load the saved model
def load_model(filename):
    try:
        loaded_model = joblib.load(filename)
        print("Model loaded successfully from", filename)
        return loaded_model
    except Exception as e:
        print("Error occurred while loading the model:", str(e))
        return None