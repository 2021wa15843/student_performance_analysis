
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(layout="wide")

df = pd.read_csv("Student_Performance_Standard6to12_Final.csv")

st.title("📊 Student Performance Dashboard")

with st.sidebar:
    st.header("Filters")
    classes = ['All'] + sorted(df['Class'].unique())
    regions = ['All'] + sorted(df['Region'].unique())
    sections = ['All'] + sorted(df['Section'].unique())
    # schools = ['All'] + sorted(df['School_Name'].unique())

    selected_class = st.selectbox("Select Class", classes)
    selected_region = st.selectbox("Select Region", regions)
    selected_section = st.selectbox("Select Section", sections)
    # selected_school = st.selectbox("Select School", schools)

    chart_type = st.selectbox("Select Chart Type", [
        "Performance Label Distribution",
        "Score Trend by Student",
        "Average Score by Class",
        "Attendance vs Exam Score",
        "Growth vs Decline"
    ])

filtered_df = df.copy()
if selected_class != 'All':
    filtered_df = filtered_df[filtered_df['Class'] == selected_class]
if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
if selected_section != 'All':
    filtered_df = filtered_df[filtered_df['Section'] == selected_section]
# if selected_school != 'All':
    # filtered_df = filtered_df[filtered_df['School_Name'] == selected_school]

st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3)
col1.metric("Avg Previous Score", round(filtered_df['Previous_Score'].mean(), 2))
col2.metric("Avg Exam Score", round(filtered_df['Exam_Score'].mean(), 2))
col3.metric("Avg Attendance Rate", round(filtered_df['Attendance_Rate'].mean(), 2))

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

st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 10 Students by Score Improvement")
filtered_df['Score_Change'] = filtered_df['Exam_Score'] - filtered_df['Previous_Score']
top_improved = filtered_df.sort_values('Score_Change', ascending=False).head(10)
st.dataframe(top_improved[['Student_Unique_ID','Previous_Score','Exam_Score','Score_Change']])

st.subheader("Filtered Student Records")
st.dataframe(filtered_df)

csv_data = filtered_df.to_csv(index=False)
st.download_button(
    label="Download Filtered Data",
    data=csv_data,
    file_name="filtered_students.csv",
    mime="text/csv"
)

# Notify staff via Google Sheets + Email Display
st.subheader("Notify Staff")
staff_email = "lavanya.ramamoorthy30@gamil.com"
st.info(f"Notification will be sent to: {staff_email}")

if st.button("Notify Staff"):
    try:
        # Google Sheets logic (optional)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)

        sheet = client.open("Student Performance Alerts").sheet1
        sheet.append_row(["Total Students", len(filtered_df)])
        sheet.append_row(["Avg Exam Score", round(filtered_df['Exam_Score'].mean(), 2)])
        sheet.append_row(["Avg Attendance", round(filtered_df['Attendance_Rate'].mean(), 2)])
        sheet.append_row(["Class", selected_class, "Region", selected_region, "Section", selected_section, "School", selected_school])

        st.success(f"Notification logged for {staff_email}")
    except Exception as e:
        st.error(f"Failed to update Google Sheet: {e}")
