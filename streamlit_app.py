
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

# Load data and model
df = pd.read_csv("Student_Performance_Standard6to12_Final.csv")
model = joblib.load("student_performance_simple.pkl")

st.title("📊 Enhanced Student Performance Dashboard")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    classes = ['All'] + sorted(df['Class'].unique())
    regions = ['All'] + sorted(df['Region'].unique())
    sections = ['All'] + sorted(df['Section'].unique())
    selected_class = st.selectbox("Select Class", classes)
    selected_region = st.selectbox("Select Region", regions)
    selected_section = st.selectbox("Select Section", sections)
    chart_type = st.selectbox("Select Chart Type", [
        "Performance Label Distribution",
        "Score Trend by Student",
        "Average Score by Class",
        "Attendance vs Exam Score",
        "Growth vs Decline"
    ])

# Apply filters
filtered_df = df.copy()
if selected_class != 'All':
    filtered_df = filtered_df[filtered_df['Class'] == selected_class]
if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
if selected_section != 'All':
    filtered_df = filtered_df[filtered_df['Section'] == selected_section]

# KPIs
st.subheader("Key Performance Indicators")
st.metric("Average Previous Score", round(filtered_df['Previous_Score'].mean(), 2))
st.metric("Average Exam Score", round(filtered_df['Exam_Score'].mean(), 2))
st.metric("Average Attendance Rate", round(filtered_df['Attendance_Rate'].mean(), 2))

# Predictive insights
st.subheader("Predicted Performance Labels")
predicted_labels = model.predict(filtered_df[['Previous_Score', 'Exam_Score', 'Attendance_Rate']])
filtered_df['Predicted_Label'] = predicted_labels

# Chart rendering
if chart_type == "Performance Label Distribution":
    label_counts = filtered_df['Performance_Label'].value_counts().reset_index()
    label_counts.columns = ['Performance_Label', 'Count']
    fig = px.pie(label_counts, names='Performance_Label', values='Count')
elif chart_type == "Score Trend by Student":
    fig = px.line(filtered_df, x='Student_Unique_ID', y=['Previous_Score', 'Exam_Score'])
elif chart_type == "Average Score by Class":
    avg_score_by_class = filtered_df.groupby('Class')['Exam_Score'].mean().reset_index()
    fig = px.bar(avg_score_by_class, x='Class', y='Exam_Score')
elif chart_type == "Attendance vs Exam Score":
    fig = px.scatter(filtered_df, x='Attendance_Rate', y='Exam_Score', color='Performance_Label')
elif chart_type == "Growth vs Decline":
    filtered_df['Score_Change'] = filtered_df['Exam_Score'] - filtered_df['Previous_Score']
    fig = px.bar(filtered_df, x='Student_Unique_ID', y='Score_Change',
                 color=filtered_df['Score_Change'] > 0, color_discrete_map={True: 'green', False: 'red'})

st.plotly_chart(fig)

# Top 10 Students by Score Improvement
st.subheader("Top 10 Students by Score Improvement")
filtered_df['Score_Change'] = filtered_df['Exam_Score'] - filtered_df['Previous_Score']
top_improved = filtered_df.sort_values('Score_Change', ascending=False).head(10)
st.dataframe(top_improved[['Student_Unique_ID','Previous_Score','Exam_Score','Score_Change']])

# Summary metrics
st.subheader("Summary Metrics")
st.write(filtered_df['Performance_Label'].value_counts())
st.write(filtered_df['Predicted_Label'].value_counts())

# Full student records
st.subheader("Filtered Student Records")
st.dataframe(filtered_df)

# Download button
csv_data = filtered_df.to_csv(index=False)
st.download_button(
    label="Download Filtered Data",
    data=csv_data,
    file_name="filtered_students.csv",
    mime="text/csv"
)
