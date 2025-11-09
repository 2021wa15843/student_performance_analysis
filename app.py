from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import joblib
import plotly.express as px
import os

app = Flask(__name__)

# Load data and model
df = pd.read_csv("Student_Performance_Standard6to12_Final.csv")
model = joblib.load("student_performance_simple.pkl")

chart_types = [
    "Performance Label Distribution",
    "Score Trend by Student",
    "Average Score by Class",
    "Attendance vs Exam Score",
    "Growth vs Decline"
]

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    # Get filter values
    selected_class = request.form.get('Class', 'All')
    selected_region = request.form.get('Region', 'All')
    selected_section = request.form.get('Section', 'All')
    selected_chart = request.form.get('Chart', chart_types[0])

    # Apply filters
    filtered_df = df.copy()
    if selected_class != 'All':
        filtered_df = filtered_df[filtered_df['Class'] == selected_class]
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    if selected_section != 'All':
        filtered_df = filtered_df[filtered_df['Section'] == selected_section]

    # KPIs
    avg_scores = {
        'Average Previous Score': round(filtered_df['Previous_Score'].mean(), 2),
        'Average Exam Score': round(filtered_df['Exam_Score'].mean(), 2),
        'Average Attendance Rate': round(filtered_df['Attendance_Rate'].mean(), 2)
    }

    # Chart generation
    if selected_chart == "Performance Label Distribution":
        label_counts = filtered_df['Performance_Label'].value_counts().reset_index()
        label_counts.columns = ['Performance_Label', 'Count']
        fig = px.pie(label_counts, names='Performance_Label', values='Count', title='Distribution of Performance Labels')
    elif selected_chart == "Score Trend by Student":
        fig = px.line(filtered_df, x='Student_Unique_ID', y=['Previous_Score', 'Exam_Score'], title='Exam Score vs Previous Score by Student')
    elif selected_chart == "Average Score by Class":
        avg_score_by_class = filtered_df.groupby('Class')['Exam_Score'].mean().reset_index()
        fig = px.bar(avg_score_by_class, x='Class', y='Exam_Score', title='Average Exam Score by Class')
    elif selected_chart == "Attendance vs Exam Score":
        fig = px.scatter(filtered_df, x='Attendance_Rate', y='Exam_Score', color='Performance_Label', title='Attendance Rate vs Exam Score')
    elif selected_chart == "Growth vs Decline":
        filtered_df['Score_Change'] = filtered_df['Exam_Score'] - filtered_df['Previous_Score']
        fig = px.bar(filtered_df, x='Student_Unique_ID', y='Score_Change', title='Growth vs Decline',
                     color=filtered_df['Score_Change'] > 0, color_discrete_map={True: 'green', False: 'red'})

    chart_html = fig.to_html(full_html=False)

    # Dropdown options
    classes = ['All'] + sorted(df['Class'].unique())
    regions = ['All'] + sorted(df['Region'].unique())
    sections = ['All'] + sorted(df['Section'].unique())
    students = filtered_df.to_dict(orient='records')

    return render_template("dashboard.html", classes=classes, regions=regions, sections=sections,
                           selected_class=selected_class, selected_region=selected_region,
                           selected_section=selected_section, avg_scores=avg_scores,
                           students=students, chart_types=chart_types,
                           selected_chart=selected_chart, chart_html=chart_html)

@app.route('/filter_by_label', methods=['POST'])
def filter_by_label():
    label = request.json.get('label')
    filtered_df = df[df['Performance_Label'] == label]
    return jsonify(filtered_df.to_dict(orient='records'))

@app.route('/filter_by_class', methods=['POST'])
def filter_by_class():
    cls = request.json.get('class')
    filtered_df = df[df['Class'] == cls]
    return jsonify(filtered_df.to_dict(orient='records'))

@app.route('/filter_by_student', methods=['POST'])
def filter_by_student():
    student_id = request.json.get('student_id')
    filtered_df = df[df['Student_Unique_ID'] == student_id]
    return jsonify(filtered_df.to_dict(orient='records'))

@app.route('/export_csv', methods=['POST'])
def export_csv():
    filtered_df = df.copy()
    filtered_df.to_csv("static/charts/filtered_students.csv", index=False)
    return send_file("static/charts/filtered_students.csv", as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
