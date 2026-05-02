import streamlit as st
import os
import json
from datetime import date, timedelta
import openai
import shutil

# 디렉토리 설정
BASE_DIR = "data/users"
os.makedirs(BASE_DIR, exist_ok=True)

# 세션 상태 초기화
if "mode" not in st.session_state:
    st.session_state.mode = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "editing_profile" not in st.session_state:
    st.session_state.editing_profile = False

# 페이지 타이틀
st.title("🏋️ AI Personal Trainer")
st.subheader("👤 Choose user mode")

# 사용자 유형 선택
if st.session_state.mode is None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Use Existing User"):
            st.session_state.mode = "existing"
    with col2:
        if st.button("🆕 Start as New User"):
            st.session_state.mode = "new"

# 기존 유저 로그인
if st.session_state.mode == "existing":
    if st.button("🔙 Back", key="back_existing"):
        st.session_state.mode = None
        st.session_state.username = ""
        st.rerun()

    users = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    if users:
        c1, c2 = st.columns([3, 1])
        with c1:
            username = st.selectbox("Select your name", users)
        with c2:
            if st.button("🗑️ Delete User"):
                shutil.rmtree(os.path.join(BASE_DIR, username))
                st.success(f"User '{username}' deleted.")
                st.rerun()

        if st.button("✅ Login"):
            profile_path = os.path.join(BASE_DIR, username, "profile.json")
            if os.path.exists(profile_path):
                st.session_state.username = username
                st.session_state.mode = None
                st.rerun()
            else:
                st.error("❌ User not found.")
    else:
        st.warning("No registered users found.")

# 신규 유저 등록
if st.session_state.mode == "new":
    if st.button("🔙 Back", key="back_new"):
        st.session_state.mode = None
        st.rerun()

    username = st.text_input("Enter your name")
    age = st.number_input("Age", 10, 100, 25)
    gender = st.selectbox("Gender", ["male", "female", "other"])
    weight = st.slider("Weight (kg)", 30, 150, 65)
    body_fat = st.slider("Body Fat (%)", 5, 50, 25)
    muscle_mass = st.slider("Muscle Mass (kg)", 10, 50, 23)
    goal = st.selectbox("Fitness Goal", ["gain muscle", "lose fat", "maintain", "increase strength"])

    if st.button("✅ Register & Start") and username:
        user_dir = os.path.join(BASE_DIR, username)
        os.makedirs(user_dir, exist_ok=True)
        profile = {
            "name": username,
            "age": age,
            "gender": gender,
            "weight": weight,
            "body_fat": body_fat,
            "muscle_mass": muscle_mass,
            "goal": goal,
            "date_created": str(date.today())
        }
        with open(os.path.join(user_dir, "profile.json"), 'w') as f:
            json.dump(profile, f, indent=2)
        st.session_state.username = username
        st.rerun()

# 메인 기능
if st.session_state.username:
    # 뒤로가기
    if st.button("🔙 Back", key="back_main"):
        st.session_state.mode = None
        st.session_state.username = ""
        st.rerun()

    # 파일 경로
    user_dir = os.path.join(BASE_DIR, st.session_state.username)
    profile_path = os.path.join(user_dir, "profile.json")
    routine_path = os.path.join(user_dir, "routine.json")
    log_path = os.path.join(user_dir, "log.json")

    # 프로필 로드
    with open(profile_path, 'r') as f:
        profile = json.load(f)

    # 루틴 & 기록 헤더
    st.header("📅 Routine & Workout Log")

    # 프로필 보기/편집
    with st.expander("🧾 View / Edit Profile Info"):
        if not st.session_state.editing_profile:
            st.json(profile)
            if st.button("✏️ Edit Profile"):
                st.session_state.editing_profile = True
                st.rerun()
        else:
            profile['age'] = st.number_input("Age", 10, 100, profile['age'])
            profile['gender'] = st.selectbox(
                "Gender",
                ["male", "female", "other"],
                index=["male", "female", "other"].index(profile['gender'])
            )
            profile['weight'] = st.slider("Weight (kg)", 30, 150, profile['weight'])
            profile['body_fat'] = st.slider("Body Fat (%)", 5, 50, profile['body_fat'])
            profile['muscle_mass'] = st.slider("Muscle Mass (kg)", 10, 50, profile['muscle_mass'])
            profile['goal'] = st.selectbox(
                "Fitness Goal",
                ["gain muscle", "lose fat", "maintain", "increase strength"],
                index=["gain muscle", "lose fat", "maintain", "increase strength"].index(profile['goal'])
            )
            if st.button("💾 Save Profile"):
                with open(profile_path, 'w') as f:
                    json.dump(profile, f, indent=2)
                st.session_state.editing_profile = False
                st.rerun()

    # GPT 루틴 생성
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    def summarize_logs(log_path):
        if not os.path.exists(log_path):
            return ""
        with open(log_path, "r") as f:
            records = [json.loads(line.strip()) for line in f if line.strip()]
        today = date.today()
        weekday = today.weekday()  # 월요일=0
        this_monday = today - timedelta(days=weekday)
        last_monday = this_monday - timedelta(days=7)
        last_week_records = [
            r for r in records
            if last_monday <= date.fromisoformat(r["date"]) < this_monday
        ]
        last_week_records.sort(key=lambda r: r["date"], reverse=True)
        summary_lines = []
        for r in last_week_records:
            line = f"{r['date']} ({r['day']}): " + "; ".join(
                f"{ex['exercise']} - {ex['performed_weight']}kg x {ex['performed_reps']} reps x {ex['performed_sets']} sets"
                for ex in r["performed"]
            )
            summary_lines.append(line)
        return "\n".join(summary_lines)

    def build_prompt():
        hist = summarize_logs(log_path)
        return f"""
You are a personal fitness coach.
I am a {profile['age']}-year-old {profile['gender']} with {profile['body_fat']}% body fat,
{profile['muscle_mass']}kg muscle mass, and {profile['weight']}kg weight.
My goal is to {profile['goal']}.
Here is a summary of my recent workouts:
{hist if hist else 'No prior records from last week.'}
Generate a weekly workout routine in JSON format:
{{"Monday":[{{"exercise":"string","weight":number,"reps":number,"sets":number}}],...}}
Return only valid JSON without explanations or markdown.
"""

    if st.button("🧠 Generate Routine"):
        with st.spinner("Generating routine..."):
            try:
                resp = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": build_prompt()}],
                    temperature=0.7,
                    max_tokens=1000
                )
                data = json.loads(resp.choices[0].message.content)
                with open(routine_path, 'w') as f:
                    json.dump(data, f, indent=2)
                st.success("✔️ Routine saved!")
            except Exception as e:
                st.error(f"JSON error: {e}")

    # 루틴 수행 기록
    if os.path.exists(routine_path):
        weekly = json.load(open(routine_path))
        day = st.selectbox("Select Day", list(weekly.keys()))
        st.subheader(f"{day} Performance")
        inputs = []
        for i, ex in enumerate(weekly[day]):
            st.markdown(f"**{ex['exercise']}** - {ex['weight']}kg x {ex['reps']} reps x {ex['sets']} sets")
            c1, c2, c3 = st.columns(3)
            w = c1.number_input("Weight", 0, key=f"w{i}")
            rps = c2.number_input("Reps", 0, key=f"r{i}")
            sets_ = c3.number_input("Sets", 0, key=f"s{i}")
            inputs.append({
                "exercise": ex['exercise'],
                "performed_weight": w,
                "performed_reps": rps,
                "performed_sets": sets_
            })
        if st.button("📋 Save Record"):
            rec = {
                "date": str(date.today()),
                "day": day,
                "user": profile,
                "routine": weekly[day],
                "performed": inputs
            }
            with open(log_path, 'a') as f:
                f.write(json.dumps(rec) + "\n")
            st.success("✅ Record saved!")

    # 기록 조회/삭제
    st.subheader("📊 View & Delete Workout History")
    if os.path.exists(log_path):
        recs = [json.loads(l) for l in open(log_path) if l.strip()]
        if recs:
            dates = sorted({r['date'] for r in recs}, reverse=True)
            sel = st.selectbox("Select Date", dates)
            r = next(x for x in recs if x['date'] == sel)
            st.markdown(f"**📅 {r['date']} / {r['day']}**")
            for e in r['performed']:
                st.write(f"- {e['exercise']} | {e['performed_weight']}kg x {e['performed_reps']} reps x {e['performed_sets']} sets")
            if st.button("🗑️ Delete This Record"):
                recs = [x for x in recs if x['date'] != sel]
                with open(log_path, 'w') as f:
                    for x in recs:
                        f.write(json.dumps(x) + "\n")
                st.success("✅ Deleted.")
                st.rerun()

    # 영양 계획 생성
    st.subheader("🍎 Nutrition Plan")
    with st.expander("Configure your meals & snacks"):
        col1, col2 = st.columns(2)
        meals_per_day = col1.number_input("Number of meals per day", 1, 6, 3)
        snacks_per_day = col2.number_input("Number of snacks per day", 0, 5, 2)

    def build_nutrition_prompt(profile, meals, snacks):
        return f"""
You are a professional nutritionist.
Client profile:
- Age: {profile['age']}
- Gender: {profile['gender']}
- Weight: {profile['weight']} kg
- Body Fat: {profile['body_fat']}%
- Muscle Mass: {profile['muscle_mass']} kg
- Goal: {profile['goal']}
Provide:
1. Daily recommended calorie intake (integer).
2. A balanced diet plan with exactly {meals} meals and {snacks} snacks per day.
Output only the JSON object without markdown or extra text.
"""

    if st.button("Generate Nutrition Plan"):
        with st.spinner("Generating nutrition plan..."):
            try:
                prompt = build_nutrition_prompt(profile, meals_per_day, snacks_per_day)
                resp = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
                nutrition_data = json.loads(resp.choices[0].message.content.strip())
                st.subheader("🍽️ Daily Calories")
                st.metric("Calories", nutrition_data.get("calories", 0))
                st.subheader("📋 Meal Plan")
                for key, meal in nutrition_data.get("meal_plan", {}).items():
                    st.markdown(f"**{key.title()}**: {meal.get('description')}")
                    macros = meal.get("macros", {})
                    st.write(f"- Calories: {macros.get('calories', 0)}")
                    st.write(f"- Carbs: {macros.get('carbs', '0g')}")
                    st.write(f"- Protein: {macros.get('protein', '0g')}")
                    st.write(f"- Fats: {macros.get('fats', '0g')}")
            except Exception as e:
                st.error(f"Nutrition generation error: {e}")
