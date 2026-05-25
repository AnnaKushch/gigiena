import streamlit as st
import random
from docx import Document


FILE_PATH = "гигиена.docx"


def load_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text


def parse_tests(text):
    blocks = text.strip().split("\n\n")
    tests = []

    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue

        question = lines[0]
        options = []
        correct = None

        for line in lines[1:]:
            if line.startswith("*"):
                correct = line.replace("*", "").strip()
                options.append(correct)
            else:
                options.append(line)

        if question and options and correct:
            tests.append({
                "question": question,
                "options": options,
                "correct": correct
            })

    return tests


# ---------- LOAD DATA ----------
try:
    text = load_docx(FILE_PATH)
    tests = parse_tests(text)

    # ---------- STATE ----------
    if "i" not in st.session_state:
        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.tests = random.sample(tests, len(tests))
        st.session_state.answered = False
        st.session_state.last_answer = None
        st.session_state.is_correct = None

    current = st.session_state.tests[st.session_state.i]

    st.write(f"### {st.session_state.i + 1}. {current['question']}")

    # ---------- ANSWERING ----------
    if not st.session_state.answered:
        answer = st.radio("Выбери ответ", current["options"], key=f"q_{st.session_state.i}")

        if st.button("Ответить"):
            st.session_state.last_answer = answer
            st.session_state.is_correct = (answer == current["correct"])
            st.session_state.answered = True

            if st.session_state.is_correct:
                st.session_state.score += 1

            st.rerun()

    # ---------- SHOW RESULT ----------
else:

    correct = test["answer"]

    st.write("---")

    for opt in test["options"]:

        if opt == correct:
            st.markdown("🟢 " + opt)

        elif opt == st.session_state.selected:
            st.markdown("🔴 " + opt)

        else:
            st.markdown("⚪ " + opt)

    # ---------- SCORE ----------
    if not st.session_state.saved_answer:

        st.session_state.results.append({
            "question": test["question"],
            "selected": st.session_state.selected,
            "correct": correct,
            "is_correct": st.session_state.selected == correct
        })
    
        st.session_state.saved_answer = True
    
    if st.session_state.selected == correct:
        st.success("✅ Правильно")

        # защита от двойного подсчёта
        if not st.session_state.get("counted", False):
            st.session_state.score += 1
            st.session_state.counted = True

    else:
        st.error(f"❌ Неправильно. Правильный: {correct}")

    # ---------- NEXT ----------
    if st.button("Дальше ➡️"):

        st.session_state.i += 1
        st.session_state.checked = False
        st.session_state.selected = None
        st.session_state.counted = False
        st.session_state.saved_answer = False
            
        
    st.rerun()

except Exception as e:
    st.error(f"Ошибка загрузки файла: {e}")
