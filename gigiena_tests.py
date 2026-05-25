import streamlit as st
import random
from docx import Document

FILE_PATH = "гигиена.docx"
BATCH_SIZE = 20


# ---------- LOAD DOC ----------
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
            random.shuffle(options)  # 🔥 ВОТ ГЛАВНОЕ

            tests.append({
                "question": question,
                "options": options,
                "correct": correct
            })

    return tests


# ===================== FINAL SCREEN =====================
if st.session_state.get("finished", False):

    st.title("📊 Результат теста")

    st.write(f"**Баллы:** {st.session_state.score} / {BATCH_SIZE}")

    st.write("---")

    for r in st.session_state.all_results:

        st.write(f"### {r['question']}")

        for opt in r["options"]:
            if opt == r["correct"]:
                st.markdown("🟢 " + opt)
            elif opt == r["selected"]:
                st.markdown("🔴 " + opt)
            else:
                st.markdown("⚪ " + opt)

        if r["is_correct"]:
            st.success("Правильно")
        else:
            st.error(f"Правильный ответ: {r['correct']}")

        st.write("---")

    if st.button("🔄 Новый тест"):
        for key in ["i", "score", "checked", "selected", "finished", "all_results"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.stop()


# ===================== MAIN =====================
try:
    text = load_docx(FILE_PATH)
    tests = parse_tests(text)

    if not tests:
        st.error("В файле нет тестов")
        st.stop()

    # ===================== HOME PAGE =====================
    if "started" not in st.session_state:
        st.session_state.started = False

    if not st.session_state.started:

        st.title("📚 Тренажёр по биологии")
        st.write("Выбери режим теста:")

        mode = st.radio(
            "Режим",
            ["🔀 Случайный (20 вопросов)", "📖 По порядку (все вопросы)"]
        )

        if st.button("▶ Начать"):
            st.session_state.started = True
            st.session_state.mode = mode
            st.session_state.i = 0
            st.session_state.score = 0
            st.session_state.checked = False
            st.session_state.selected = None
            st.session_state.all_results = []

            # --------- СЛУЧАЙНЫЙ ----------
            if mode == "🔀 Случайный (20 вопросов)":
                st.session_state.tests_pool = random.sample(tests, len(tests))
                st.session_state.batch = st.session_state.tests_pool[:20]

            # --------- ПО ПОРЯДКУ ----------
            else:
                st.session_state.tests_pool = tests.copy()
                st.session_state.batch = tests  # ВСЕ ВОПРОСЫ

            st.rerun()

        st.stop()

    # ===================== CURRENT QUESTION =====================
    current = st.session_state.batch[st.session_state.i]

    if st.session_state.mode == "📖 По порядку (все вопросы)":

        st.write("---")
    
        cols = st.columns(min(20, len(st.session_state.batch)))
    
        for idx in range(len(st.session_state.batch)):

            with cols[idx % len(cols)]:

                label = str(idx + 1)

                if idx < len(st.session_state.all_results):
                    if st.session_state.all_results[idx]["is_correct"]:
                        label = "🟢 " + label
                    else:
                        label = "🔴 " + label
                else:
                    label = "⚪ " + label

                if st.button(label, key=f"nav_{idx}"):
    
                    st.session_state.i = idx
                    st.session_state.checked = False
                    st.session_state.selected = None
    
                    st.rerun()

    st.write(f"### Вопрос {st.session_state.i + 1} / {len(st.session_state.batch)}")
    st.write(current["question"])

    # ---------- ANSWER ----------
    if not st.session_state.checked:

        st.session_state.selected = st.radio(
            "Выбери ответ",
            current["options"],
            key=f"q_{st.session_state.i}"
        )

        if st.button("Ответить"):
            st.session_state.checked = True

            is_correct = st.session_state.selected == current["correct"]

            if is_correct:
                st.session_state.score += 1

            st.session_state.all_results.append({
                "question": current["question"],
                "options": current["options"],
                "selected": st.session_state.selected,
                "correct": current["correct"],
                "is_correct": is_correct
            })

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

        if st.button("Далее ➡️"):
            st.session_state.i += 1
            st.session_state.checked = False
            st.session_state.selected = None

            if st.session_state.i >= len(st.session_state.batch):
                st.session_state.finished = True
                st.rerun()

            st.rerun()

except Exception as e:
    st.error(f"Ошибка: {e}")
    
    # ---------- ANSWER ----------
    if not st.session_state.checked:
        st.session_state.selected = st.radio(
            "Выбери ответ",
            current["options"],
            key=f"q_{st.session_state.i}"
        )

        if st.button("Ответить"):
            st.session_state.checked = True

            is_correct = st.session_state.selected == current["correct"]

            if is_correct:
                st.session_state.score += 1

            st.session_state.all_results.append({
                "question": current["question"],
                "options": current["options"],
                "selected": st.session_state.selected,
                "correct": current["correct"],
                "is_correct": is_correct
            })

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

        # ---------- NEXT ----------
        if st.button("Далее ➡️"):
            st.session_state.i += 1
            st.session_state.checked = False
            st.session_state.selected = None

            if st.session_state.i >= BATCH_SIZE:
                st.session_state.finished = True
                st.rerun()

            st.rerun()

except Exception as e:
    st.error(f"Ошибка: {e}")
