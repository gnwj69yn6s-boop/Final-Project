# n8n 주간 알림 워크플로우

[Schedule Trigger] 매주 일요일 18:00 (Asia/Seoul)
   ↓
[HTTP Request] GET https://[배포 URL]/api/internal/digests
   Header: x-api-key = {{INTERNAL_API_KEY}}  (n8n Credentials에 저장)
   ↓
[Split Out] digests 배열 분리
   ↓
[Send Email (또는 Discord Webhook)]
   To: {{$json.email}}  /  Subject: "🧊 이번 주 장보기 알림"  /  Body: {{$json.message}}

노드 구성을 캡처해 docs/에 첨부하고, 워크플로우 JSON을 Export하여 n8n/ 폴더에 커밋합니다.
