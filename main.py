import streamlit as st
from streamlit_chat import message
import streamlit_modal as modal
import json
from model.elastic_setting import *

from model.inference import load_model, run_mrc

model, tokenizer = load_model()


st.title("뭐든 내게 물어봐!(MNM)")
st.image("https://t1.daumcdn.net/cfile/tistory/99D595365C348A850A")

if "input" not in st.session_state:
    st.session_state["input"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []
if "user_ids" not in st.session_state:
    st.session_state["user_ids"] = []

# 회의록 입력
with st.sidebar:
    st.title('사용자 ID를 입력해주세요!')
    user = st.text_input("사용자 ID", placeholder="User_1", key="user", disabled=False)
    st.title('회의록을 입력해주세요!')
    st.session_state['uploaded_files'] = st.file_uploader('정해진 형식의 회의록을 올려주세요!(json)', accept_multiple_files=True, disabled= (False if user else True))
    print(st.session_state['uploaded_files'])
    minutes_list =[files.name.split(".")[0] for files in st.session_state['uploaded_files']] # 모든 회의록 파일명
    options = list(range(len(minutes_list)))

    selected_minutes = st.selectbox(f'회의록 목록(개수: {len(minutes_list)}): ', options, 
                                    format_func = lambda x: minutes_list[x])
    submit_minute = st.button(label="회의록 보기", disabled=(False if st.session_state['uploaded_files'] else True)) 
    if submit_minute:
        modal.open()

# TODO: 사용자별 index 생성
    # TODO: modal쪽에서 사용자 id/이름을 받아오기
# TODO: txt 로드해서 index에 삽입 - txt 1개/ 여러개 모두 가능하도록
# TODO: 생성된 인덱스로 검색 (es_index)

if modal.is_open():
    with modal.container():
        # print(st.session_state['uploaded_files'][selected_minutes].read().decode('utf-8'))
        # st_json = json.dumps(st.session_state['uploaded_files'][selected_minutes].read().decode('utf-8')) # 파일 형식에 따라서 주기
        data = st.session_state['uploaded_files'][selected_minutes].read().decode('utf-8')
        st.title(minutes_list[selected_minutes])
        st.write(data)

es, es_index = es_setting(index_name="사용자별 id")

# 입력 
with st.form(key="my_form", clear_on_submit=True):
    col1, col2 = st.columns([8, 1])
    with col1:
        if len(st.session_state['uploaded_files']) != 0:
            st.text_input(
                "궁금한 건 뭐든지 물어봐 (물론 회의록 내에서)",
                placeholder="2015년 2차 본회의는 언제야?",
                key="input", disabled=False,
            )
        else: 
            st.text_input(
                "궁금한 건 뭐든지 물어봐 (물론 회의록 내에서)",
                placeholder="회의록을 먼저 올려주세요!!!",
                key="input", disabled=True
            )
    with col2:
        st.write("&#9660;&#9660;&#9660;")
        submit = st.form_submit_button(label="Ask")

# 제출 시 모델 사용
if submit:
    msg = (st.session_state["input"], True)
    st.session_state.messages.append(msg)
    for msg in st.session_state.messages:
        message(msg[0], is_user=msg[1])
    with st.spinner("두뇌 풀가동!"):
        result = run_mrc(None, None, None, None, tokenizer, model, msg[0], es_index) # 인덱스 name 을 변수로 준다거나 
    msg = (result, False)
    st.session_state.messages.append(msg)
    message(msg[0], is_user=msg[1])