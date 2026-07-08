# knowledge — RAG 지식 문서

챗봇이 인덱싱할 원본 문서를 여기에 넣는다 (`.md` 권장).

## 넣을 것

- REI 산정 방법론 (Method B, 박연기 2021 수식, EPA WPS/PRN 95-3 요약)
- 딸기 농약 로테이션 규칙 — 작용기작 그룹(FRAC/IRAC) 교차 저항성 관리
- 대표 3종(azoxystrobin/abamectin/boscalid) 특성·작업별 REI 연장
- 제품 라벨 재출입 주의사항 (PSIS)

인덱스 갱신: `python -c "from app.rag import build_index; build_index()"`
