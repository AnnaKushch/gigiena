import streamlit as st
import random
from docx import Document


FILE_PATH = "гигиена.docx"


def load_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


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


# ===================== MAIN =====================

try:
    text = load_docx(FILE_PATH)
    tests = parse_tests(text)

    if not tests:
        st.error("Нет тестов в файле")
        st.stop()

    # ---------- STATE ----------
    if "i" not in st.session_state:
        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.tests = random.sample(tests, len(tests))
        st.session_state.selected = None
        st.session_state.checked = False

    current = st.session_state.tests[st.session_state.i]

    st.write(f"### {st.session_state.i + 1}. {current['question']}")

    # ---------- ANSWER ----------
    if not st.session_state.checked:
        st.session_state.selected = st.radio(
            "Выбери ответ",
            current["options"],
            key=f"q_{st.session_state.i}"
        )

        if st.button("Ответить"):
            st.session_state.checked = True

            if st.session_state.selected == current["correct"]:
                st.session_state.score += 1

            st.rerun()

    # ---------- RESULT ----------
    else:
        correct = current["correct"]

        st.write("---")

        for opt in current["options"]:
            if opt == correct:
                st.markdown("🟢 " + opt)
            elif opt == st.session_state.selected:
                st.markdown("🔴 " + opt)
            else:
                st.markdown("⚪ " + opt)

        if st.session_state.selected == correct:
            st.success("✅ Правильно")
        else:
            st.error(f"❌ Неправильно. Правильный: {correct}")

        if st.button("Дальше ➡️"):
            st.session_state.i += 1
            st.session_state.checked = False
            st.session_state.selected = None

            if st.session_state.i >= len(st.session_state.tests):
                st.write(f"### Тест завершен: {st.session_state.score}/{len(st.session_state.tests)}")
                st.stop()

            st.rerun()

except Exception as e:
    st.error(f"Ошибка загрузки файла: {e}")
