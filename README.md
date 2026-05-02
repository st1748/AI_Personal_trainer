# AI Personal Trainer

AI 기반으로 개인 맞춤 운동 루틴과 식단을 추천해주는 웹 애플리케이션입니다.  
사용자의 신체 정보와 목표를 입력하면, GPT를 활용하여 최적화된 운동 계획과 식단을 생성합니다.

---

## Features

- 사용자 정보 입력 (체중, 목표, 운동 수준 등)
- 맞춤형 운동 루틴 자동 생성
- 개인 맞춤 식단 추천
- 운동 기록 저장 및 관리
- 이전 운동 기록을 기반으로 루틴 개선

---

## 🛠 Tech Stack

- Frontend / UI: Streamlit  
- Backend: Python  
- AI: OpenAI API (GPT 기반)  
- Data Storage: Local file system (JSON)

---

## How to Run

### 1. 저장소 클론
git clone https://github.com/st1748/AI_Personal_trainer.git  
cd AI_Personal_trainer  

---

### 2. OpenAI API Key 설정
프로젝트 루트에 `.streamlit/secrets.toml` 파일을 생성하고 아래 내용을 입력하세요:

OPENAI_API_KEY = "your-api-key"

※ API 키는 반드시 본인의 키를 사용해야 하며, 코드에 직접 입력하지 마세요.

---

### 3. 필요한 라이브러리 설치
pip install -r requirements.txt

---

### 4. 실행
streamlit run HCIprojectrevised.py

---

## Project Structure

AI_Personal_trainer/  
├── HCIprojectrevised.py        (메인 애플리케이션)  
├── requirements.txt           (필요 라이브러리 목록)  
├── data/                      (사용자 데이터 및 기록 저장)  
├── .streamlit/  
│    └── secrets.toml          (API 키 - gitignore 처리됨)  
├── .gitignore  
└── README.md  

---

## Important Notes

- `.streamlit/secrets.toml` 파일은 GitHub에 업로드되지 않습니다.  
- API 키는 개인별로 발급받아 사용해야 합니다.  
- `data/` 폴더는 개인 데이터가 포함될 수 있으므로 필요 시 `.gitignore`에 추가하세요.

---


## Author

- https://github.com/st1748
