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


# ---------- UI ----------
st.title("Тренажер по гигиене")

try:
    text = load_docx(FILE_PATH)
    tests = parse_tests(text)

    st.success(f"Загружено вопросов: {len(tests)}")

    if "i" not in st.session_state:
        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.tests = random.sample(tests, len(tests))

    current = st.session_state.tests[st.session_state.i]

    st.write(f"### {st.session_state.i + 1}. {current['question']}")

    answer = st.radio("Выбери ответ", current["options"], key=st.session_state.i)

    if st.button("Ответить"):
        if answer == current["correct"]:
            st.success("Правильно ✅")
            st.session_state.score += 1
        else:
            st.error(f"Неправильно ❌ Правильный ответ: {current['correct']}")

        st.session_state.i += 1

        if st.session_state.i >= len(st.session_state.tests):
            st.write(f"### Тест завершен: {st.session_state.score}/{len(st.session_state.tests)}")
            st.stop()

        st.rerun()

except Exception as e:
    st.error(f"Ошибка загрузки файла: {e}")
