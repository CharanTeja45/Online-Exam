import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
from pathlib import Path

DB = Path(__file__).with_name("online_exam.db")

st.set_page_config(page_title="Examlytics | Online Examination", page_icon="🎓", layout="wide")

def conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL, department TEXT, year TEXT
        );
        CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT NOT NULL,
            question TEXT NOT NULL, option_a TEXT NOT NULL, option_b TEXT NOT NULL,
            option_c TEXT NOT NULL, option_d TEXT NOT NULL, answer TEXT NOT NULL,
            marks INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS attempts(
            id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT NOT NULL,
            student_name TEXT NOT NULL, subject TEXT NOT NULL,
            score INTEGER NOT NULL, total INTEGER NOT NULL,
            percentage REAL NOT NULL, submitted_at TEXT NOT NULL
        );
        """)
        count = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count == 0:
            c.executemany("INSERT INTO students(roll_no,name,department,year) VALUES(?,?,?,?)", [
                ("DS001","Aarav Kumar","Data Science","III"),
                ("DS002","Priya Reddy","Data Science","III"),
                ("DS003","Rahul Sharma","CSE","III"),
                ("DS004","Sneha Patel","Data Science","II"),
                ("DS005","Arjun Rao","CSE","II"),
            ])
        qcount = c.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        if qcount == 0:
            sample = [
                ("Big Data","Which framework is used for distributed processing?","Hadoop","HTML","CSS","Figma","A",2),
                ("Big Data","HDFS stands for?","High Data File System","Hadoop Distributed File System","Hybrid Data Format System","High Distributed File Storage","B",2),
                ("Big Data","Which tool is commonly used for data analysis in Python?","Pandas","Photoshop","PowerPoint","Unity","A",2),
                ("Python","Which data type is immutable?","List","Dictionary","Set","Tuple","D",1),
                ("Python","Which keyword defines a function?","func","define","def","function","C",1),
                ("Database","Which SQL command retrieves records?","GET","SELECT","OPEN","FETCHALL","B",1),
            ]
            c.executemany("""INSERT INTO questions(subject,question,option_a,option_b,option_c,option_d,answer,marks)
                             VALUES(?,?,?,?,?,?,?,?)""", sample)

init_db()

def read_df(query, params=()):
    with conn() as c:
        return pd.read_sql_query(query, c, params=params)

def metric_card(label, value, note=""):
    st.metric(label, value, note)

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#0b1220 0%,#101b32 55%,#111827 100%); color:#eef2ff;}
[data-testid="stSidebar"] {background:#0a1020;}
.block-container {padding-top:1.5rem; max-width:1400px;}
.hero {padding:26px 30px;border:1px solid #263b5b;border-radius:20px;background:linear-gradient(110deg,#172b4d,#172036);margin-bottom:22px;}
.hero h1 {font-size:2.15rem;margin:0;color:#f8fafc;}
.hero p {color:#a9bdd8;margin:8px 0 0 0;}
div[data-testid="stMetric"] {background:#17243a;border:1px solid #2a3d59;padding:14px;border-radius:14px;}
.stButton>button {border-radius:10px;border:0;background:linear-gradient(90deg,#4f8cff,#7c5cff);color:white;font-weight:650;}
div[data-testid="stForm"] {background:#142138;padding:18px;border-radius:14px;border:1px solid #2a3d59;}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 🎓 Examlytics")
st.sidebar.caption("Online Examination & Big Data Analytics")
page = st.sidebar.radio("NAVIGATION", ["Dashboard","Take Examination","Question Bank","Students","Results & Analytics","Database Tools"])
st.sidebar.divider()
st.sidebar.caption("Demo project • SQLite database • CSV support")

st.markdown('<div class="hero"><h1>🎓 Examlytics</h1><p>Online Examination Management System with Performance Analytics</p></div>', unsafe_allow_html=True)

if page == "Dashboard":
    students = read_df("SELECT * FROM students")
    questions = read_df("SELECT * FROM questions")
    attempts = read_df("SELECT * FROM attempts")
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("Registered students",len(students))
    with c2: metric_card("Question bank",len(questions))
    with c3: metric_card("Examinations taken",len(attempts))
    with c4: metric_card("Average score",f"{attempts.percentage.mean():.1f}%" if len(attempts) else "—")
    st.subheader("Performance overview")
    if len(attempts):
        left,right = st.columns(2)
        with left:
            fig=px.histogram(attempts,x="percentage",nbins=10,title="Score distribution",template="plotly_dark",color_discrete_sequence=["#65a6ff"])
            st.plotly_chart(fig,use_container_width=True)
        with right:
            sub=attempts.groupby("subject",as_index=False).percentage.mean()
            fig=px.bar(sub,x="subject",y="percentage",title="Average score by subject",template="plotly_dark",color="percentage",color_continuous_scale="Blues")
            st.plotly_chart(fig,use_container_width=True)
        st.subheader("Recent examination activity")
        st.dataframe(attempts.sort_values("submitted_at",ascending=False).head(8),use_container_width=True,hide_index=True)
    else:
        st.info("No exam attempts yet. Go to Take Examination and submit a demo test to populate the analytics dashboard.")
    st.caption("Analytics are calculated from examination records stored in the SQLite database.")

elif page == "Take Examination":
    st.subheader("Start an examination")
    students=read_df("SELECT roll_no,name FROM students ORDER BY roll_no")
    subjects=read_df("SELECT DISTINCT subject FROM questions ORDER BY subject")
    if students.empty or subjects.empty:
        st.warning("Add students and questions before starting an exam.")
    else:
        student_map={f"{r.roll_no} — {r['name']}":(r.roll_no,r["name"]) for _,r in students.iterrows()}
        with st.form("exam_form"):
            student_label=st.selectbox("Student",list(student_map))
            subject=st.selectbox("Subject",subjects.subject.tolist())
            qs=read_df("SELECT * FROM questions WHERE subject=? ORDER BY id",(subject,))
            st.markdown(f"**{len(qs)} questions • {int(qs.marks.sum()) if len(qs) else 0} total marks**")
            answers={}
            for i,q in qs.iterrows():
                st.markdown(f"**Q{i+1}. {q.question}**")
                answers[str(q.id)]=st.radio("Choose an answer",["A","B","C","D"],key=f"q_{q.id}",horizontal=True,
                    format_func=lambda x: {"A":q.option_a,"B":q.option_b,"C":q.option_c,"D":q.option_d}[x])
            submitted=st.form_submit_button("Submit examination")
        if submitted:
            roll,name=student_map[student_label]
            score=0; total=0
            for _,q in qs.iterrows():
                total+=int(q.marks)
                if answers.get(str(q.id))==q.answer: score+=int(q.marks)
            pct=round(score/total*100,2) if total else 0
            with conn() as c:
                c.execute("""INSERT INTO attempts(roll_no,student_name,subject,score,total,percentage,submitted_at)
                              VALUES(?,?,?,?,?,?,?)""",(roll,name,subject,score,total,pct,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            st.success(f"Exam submitted! Score: {score}/{total} ({pct}%).")
            st.info("Your result has been saved to the examination database.")

elif page == "Question Bank":
    st.subheader("Question bank")
    with st.expander("➕ Add a question",expanded=True):
        with st.form("add_question"):
            subject=st.text_input("Subject", "Big Data")
            question=st.text_area("Question")
            a=st.text_input("Option A"); b=st.text_input("Option B")
            c=st.text_input("Option C"); d=st.text_input("Option D")
            answer=st.selectbox("Correct answer",["A","B","C","D"])
            marks=st.number_input("Marks",1,20,1)
            ok=st.form_submit_button("Save question")
        if ok:
            if all([subject.strip(),question.strip(),a.strip(),b.strip(),c.strip(),d.strip()]):
                with conn() as db:
                    db.execute("INSERT INTO questions(subject,question,option_a,option_b,option_c,option_d,answer,marks) VALUES(?,?,?,?,?,?,?,?)",
                               (subject,question,a,b,c,d,answer,int(marks)))
                st.success("Question added.")
                st.rerun()
            else: st.error("Please fill in every field.")
    qdf=read_df("SELECT id,subject,question,option_a,option_b,option_c,option_d,answer,marks FROM questions")
    st.dataframe(qdf,use_container_width=True,hide_index=True)
    if not qdf.empty:
        delete_id=st.number_input("Question ID to delete",min_value=1,step=1)
        if st.button("Delete selected question"):
            with conn() as db: db.execute("DELETE FROM questions WHERE id=?",(int(delete_id),))
            st.success("Deleted if that ID existed."); st.rerun()

elif page == "Students":
    st.subheader("Student records")
    with st.form("add_student"):
        col1,col2=st.columns(2)
        roll=col1.text_input("Roll number")
        name=col2.text_input("Student name")
        dept=col1.text_input("Department","Data Science")
        year=col2.selectbox("Year",["I","II","III","IV"])
        add=st.form_submit_button("Add student")
    if add:
        try:
            with conn() as db: db.execute("INSERT INTO students(roll_no,name,department,year) VALUES(?,?,?,?)",(roll.strip(),name.strip(),dept.strip(),year))
            st.success("Student added."); st.rerun()
        except Exception as e: st.error(f"Could not add student: {e}")
    sdf=read_df("SELECT * FROM students ORDER BY roll_no")
    st.dataframe(sdf,use_container_width=True,hide_index=True)
    upload=st.file_uploader("Import students from CSV",type=["csv"])
    if upload:
        try:
            df=pd.read_csv(upload)
            required={"roll_no","name","department","year"}
            if required.issubset(df.columns):
                with conn() as db:
                    df[list(required)].to_sql("students",db,if_exists="append",index=False)
                st.success(f"Imported {len(df)} rows."); st.rerun()
            else: st.error("CSV must contain: roll_no, name, department, year")
        except Exception as e: st.error(f"Import failed: {e}")

elif page == "Results & Analytics":
    st.subheader("Examination results")
    df=read_df("SELECT * FROM attempts ORDER BY submitted_at DESC")
    if df.empty: st.info("No results available yet. Submit an examination first.")
    else:
        f1,f2=st.columns(2)
        selected=f1.multiselect("Filter by subject",sorted(df.subject.unique()),default=sorted(df.subject.unique()))
        min_score=f2.slider("Minimum percentage",0,100,0)
        filtered=df[df.subject.isin(selected) & (df.percentage>=min_score)]
        a,b,c=st.columns(3)
        a.metric("Attempts",len(filtered))
        b.metric("Average",f"{filtered.percentage.mean():.1f}%" if len(filtered) else "—")
        c.metric("Pass rate (≥ 40%)",f"{(filtered.percentage.ge(40).mean()*100):.1f}%" if len(filtered) else "—")
        st.dataframe(filtered,use_container_width=True,hide_index=True)
        if len(filtered):
            fig=px.bar(filtered,x="student_name",y="percentage",color="subject",title="Student-wise performance",template="plotly_dark",hover_data=["roll_no","score","total"])
            st.plotly_chart(fig,use_container_width=True)
            st.download_button("⬇ Download filtered results CSV",filtered.to_csv(index=False).encode("utf-8"),"exam_results.csv","text/csv")

elif page == "Database Tools":
    st.subheader("Database & data import/export")
    st.write("The application stores students, questions and exam attempts in a local SQLite database (`online_exam.db`).")
    for table in ["students","questions","attempts"]:
        df=read_df(f"SELECT * FROM {table}")
        with st.expander(f"{table.title()} ({len(df)} records)"):
            st.dataframe(df,use_container_width=True,hide_index=True)
            st.download_button(f"Export {table}.csv",df.to_csv(index=False).encode("utf-8"),f"{table}.csv","text/csv",key=f"export_{table}")
    st.markdown("**Backup database**")
    if DB.exists():
        st.download_button("Download SQLite database",DB.read_bytes(),"online_exam.db","application/octet-stream")
    st.caption("For a fresh database, stop the app and delete online_exam.db. It will be recreated with sample records on next launch.")
