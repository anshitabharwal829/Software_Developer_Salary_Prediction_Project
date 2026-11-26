# Software_Developer_Salary_Prediction_Project
Project Overview
The Software Developer Salary Prediction project aims to predict the salary of a software developer based on various factors such as years of experience, skills, education, location, and more. This project utilizes machine learning techniques to train a model capable of providing salary predictions for software developers, helping both candidates and employers make more informed decisions.
# Technologies Used
Python, Pandas, NumPy, scikit-learn, Streamlit and Plotly.

# Setup and Run
Requires Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

# Data
The model was trained on the Stack Overflow Developer Survey (2020), which is not included in this repository.
The Predict page works without it, using `saved_steps.pkl`. For the Explore page and the notebook,
download the survey from https://survey.stackoverflow.co/ and place `survey_results_public.csv` in the project folder.

# License
This project is licensed under the MIT License - see the LICENSE file for details.
