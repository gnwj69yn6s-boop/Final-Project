# 🧊 FridgeMate — 냉장고 AI 요리 코치

냉장고 사진을 찍으면 AI가 재료를 인식하고, 나의 알레르기·취향·조리 수준을 **기억**해
레시피 DB에서 **검색(RAG)** 한 맞춤 요리를 추천하는 AI Agent 서비스입니다.
부족한 재료는 장보기 목록에 저장하고, 주 1회 개인화 알림을 자동으로 보내줍니다.

> ⚠️ 본 서비스의 모든 답변은 AI가 생성한 콘텐츠입니다. 알레르기 정보는 직접 한 번 더 확인하세요.

## 🔗 링크
- 배포 URL: [배포 URL]
- 발표 자료: [docs/presentation.pdf]
- 시연 영상: [YouTube URL]

## 👥 팀원 및 역할
| 이름 | 역할 | 담당 업무 |
|------|------|-----------|
| 김민철 | PM / 기획 | 문제 정의, 기획서·명세서, 일정 관리, 사용자 테스트 총괄 |
| 한수민 | Backend / Agent | FastAPI, Agent 오케스트레이션, 도구 설계 |
| 석제훈 | AI / Data | RAG 파이프라인, 프롬프트 설계, 레시피 데이터 구축, 평가 |
| 서연철 | Frontend | 웹 UI, 카메라 업로드, 피드백 UI |
| 최진우 | Infra / Automation | Supabase, Render 배포, n8n 워크플로우, 모니터링 |

## 🧰 기술 스택
| 영역 | 기술 | 선정 이유 |
|---|---|---|
| LLM / Vision | Claude API | 이미지 입력, tool-use 통합 지원 |
| Embedding | Voyage AI | 한국어 지원, 간편한 API |
| Backend | FastAPI (Python) | 비동기, 자동 API 문서 |
| DB / Vector | Supabase (Postgres + pgvector) | 관계형과 벡터 검색 통합 |
| Frontend | HTML / CSS / JS | 단순 배포, 모바일 카메라 지원 |
| 자동화 | n8n | 노코드 스케줄링, 알림 |
| 배포 | Render | GitHub 연동 자동 배포 |

## 🤖 핵심 AI 활용
| 기술 요소 | 적용 |
|---|---|
| 멀티모달 | 냉장고 사진 → 재료 JSON (사용자 확인 단계 포함) |
| RAG | 레시피 임베딩 → pgvector 검색 → 검색 결과 기반 답변 |
| Long-term Memory | 알레르기·비선호·조리 수준을 저장, 매 대화에 자동 반영 |
| AI Agent | search_recipes / save_memory / add_to_shopping_list 도구 자율 호출 |
| 자동화 워크플로우 | n8n 주간 장보기 알림 (LLM 개인화 문구) |

상세 설계: [docs/03_ai_design.md](docs/03_ai_design.md)

## 🏗️ 시스템 아키텍처
[docs/02_requirements.md](docs/02_requirements.md)의 Mermaid 다이어그램 참조 (이미지 파일로도 export하여 첨부 권장)

## 🚀 실행 방법
### 요구사항
- Python 3.10+, Supabase 프로젝트, Anthropic / Voyage API 키

### 설치 및 실행
```bash
git clone https://github.com/[계정]/fridgemate.git
cd fridgemate
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # 키 입력
# Supabase SQL Editor에서 sql/schema.sql 실행 후
python -m scripts.ingest_recipes
uvicorn app.main:app --reload
# http://localhost:8000
```

### 배포 (Render)
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment 탭에 `.env.example`의 변수를 모두 등록

## 🔐 개인정보 및 AI 윤리
- 수집 항목: 닉네임, (선택) 이메일, 대화 내용 / 가입 시 동의 필수
- 냉장고 이미지는 **저장하지 않고** 분석 후 폐기
- 사용자가 직접 '내 기억 보기', '내 데이터 삭제' 가능
- 모든 AI 응답에 AI 생성 표시, 알레르기 강제 제외 규칙

## 📊 사용자 테스트 결과
[docs/04_user_test.md](docs/04_user_test.md) 참조
- 테스터: [N]명 / 과제 완료율 [ ]% / 만족도 [ ]/5
- 주요 피드백 → 반영
  - "[피드백]" → [개선 내용]

## 📁 문서
- [기획서](docs/01_project_plan.md) · [요구사항](docs/02_requirements.md) · [AI 설계](docs/03_ai_design.md) · [사용자 테스트](docs/04_user_test.md)

## 🧾 데이터 출처
- 레시피 데이터: [출처 및 라이선스 명시]
