import streamlit as st
import matplotlib.pyplot as plt
import speech_recognition as sr
import streamlit_calendar as st_calendar
from openai import OpenAI
from datetime import date
import json
import openai


st.set_page_config(layout="wide")
tab1, tab2, tab3=st.tabs(['오늘의 숙제', '체크리스트', '성취도'])

hw = {'수학':[['교재 문제 풀이','6.7'],['에라토스테네스의체 알고리즘 구현','8.4']]}

client = OpenAI(api_key="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")

def gpt(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 과목/숙제/마감기한만 JSON으로 출력하는 비서다. 다른 말 금지."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content


def load_tasks():
    try:
        with open("schedule.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        out = []
        for t in raw:
            y, m, d = map(int, t["date"].split("-"))
            out.append({
                "id": int(t["id"]),
                "subject": t["subject"],
                "hw": t["hw"],
                "date": date(y, m, d),
                "done": bool(t["done"]),
            })
        return out
    except Exception:
        return []
    

def save_tasks(tasks):
    data=[
        {
            "id": t["id"],
            "subject": t["subject"],
            "hw": t["hw"],
            "date": t["date"].strftime("%Y-%m-%d"),
            "done": t["done"],    
        }for t in tasks
    ]
    with open('schedule.json', "w", encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)



if "tasks" not in st.session_state:
    st.session_state.tasks=load_tasks()
if "id_seq" not in st.session_state:
    st.session_state.id_seq=(max([t["id"] for t in st.session_state.tasks], default=0) + 1)

def next_id():
    nid = st.session_state.id_seq
    st.session_state.id_seq += 1
    return nid

def add_task(subject, work, due):
    st.session_state.tasks.append({
        "id": next_id(),
        "subject": subject,
        "hw": work,
        "date": due,
        "done": False
    })
    save_tasks(st.session_state.tasks)
    
def remove_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]
    save_tasks(st.session_state.tasks)
    st.rerun()
    
    
def get_events():
    events = []
    today = date.today()
    for t in st.session_state.tasks:
        due_str = t["date"].strftime("%Y-%m-%d")
        if t["date"] < today:
            color = "#e74c3c" 
        elif t["done"]:
            color = "#27ae60"   
        elif t["date"] == today:
            color = "#f39c12"  
        else:
            color = "#2980b9" 

        title = f"{t['subject']} · {t['hw']}"
        events.append({
            "id": str(t["id"]),
            "title": title,
            "start": due_str,     
            "end": due_str,
            "allDay": True,
            "color": color
        })
    return events
with tab1:
    col1, col2, col3=st.columns([0.9,0.1,1.1])
    with col1:
        st.header("오늘의 숙제")
        
        title=st.columns([1,4,2,2,1,1])
        title[0].write("과목")
        title[1].write("숙제")
        title[2].write("마감기한")
        title[3].write("")
        title[4].write("상태")
        title[5].write("삭제")
        if not st.session_state.tasks:
            st.write("숙제가 없습니다")
        else:
            for t in st.session_state.tasks:
                cols = st.columns([1,4,2,2,1,1])
                cols[0].write(t["subject"])
                cols[1].write(t["hw"])
                cols[2].write(t["date"])
                check = cols[3].checkbox("",value=t["done"],key=f"{t["id"]}_check")
                finish=''
                if check:
                    finish='완료'
                    t["done"]=True
                    
                else:
                    finish='미완료'
                    t["done"]=False
                cols[4].write(finish)
                if cols[5].button('❌',key=f"{t["id"]}_delete"):
                    remove_task(t["id"])
            save_tasks(st.session_state.tasks)  


    with col2:
        pass

    
    with col3:
        st_calendar.calendar(events=get_events(),key="caledar")



with tab2:
    st.header('숙제 체크리스트')
    SUBJECT=''
    HOMEWORK=''
    DATE=date.today()
    if st.button("음성으로 입력하기"):
        st.button("지우기", type="primary")
        st.write("숙제를 말해주세요: ")
        r = sr.Recognizer()
        r.pause_threshold = 1            
        r.non_speaking_duration = 0.5    
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source,phrase_time_limit=10)
        try:
            
            record_text = r.recognize_google(audio, language='ko')
            st.write(record_text)
            result=gpt(record_text)
            SUBJECT='핳'
            HOMEWORK='하ㅗㅓ호ㅓㅏㅗㅎ'
            DATE=date.today()
            
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            
    st.subheader("과목")
    subject = st.text_input("",value=SUBJECT, key=f"subject")
    st.subheader("숙제")
    hw = st.text_input("",value=HOMEWORK, key=f"hw")
    st.subheader("마감일")
    date = st.date_input("",value=DATE, key=f"date")
    if st.button('등록'):
        add_task(subject, hw, date)
        st.rerun()
                    
                            
        
    
        
    # 구글 웹 음성 API로 인식하기 (하루에 제한 50회)
        


with tab3:
    st.header('성취도')
    
    st.subheader('오늘')
    labels = ['수학', '과학', '영어']
    sizes = [30, 45, 25]

    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal') 

    st.pyplot(fig)
    st.subheader('주간')
    labels = ['수학', '과학', '영어']
    sizes = [20, 15, 65]

    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal') 

    st.pyplot(fig)
    st.subheader('월간')
    labels = ['수학', '과학', '영어']
    sizes = [35, 15, 55]


    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal') 


