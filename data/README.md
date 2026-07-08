# data — 공용 데이터

챗봇/웹/텔레그램/rei_core가 공유하는 REI 산정 입력값과 결과.

## 파일

- `active_ingredients.json` — 활성성분별 AOEL, 급성독성 카테고리
- `dt50.json` — 활성성분 × 작물별 DT50(반감기, days). PPDB 범위 교차검증됨
- `rei_results.json` — 산정된 최종 REI (웹/봇/챗봇이 표시). 값은 파이프라인 확정 후 채움
- `products.json` — 등록 제품(PSIS) → 활성성분 매핑, 작업별 REI 연장

## 출처

- AOEL: EFSA OpenFoodTox 3.0 (fluxametamide는 한국 ADI 0.0085)
- DT50: 회귀식/원자료, PPDB(Lewis & Tzilivakis 2017) 범위 내 검증
- DFR₀: boscalid는 토마토(칸투스)만 완전 회귀식 확보 — 오이·딸기 일반식 대체 필요
- TC: 오이 한국 측정치 ~6,020 cm²/hr (Choi 2023). EU EFSA(2014) 5,800과 근접, US EPA 기본 1,100이 이상치

## 위치 (중요)

- **최종 REI = `rei_results.json`** (EFSA 2022 Guidance 직접 산정, `rawdata/*.csv` 기반). 서비스가 실제로 읽는 값.
- `dt50.json` = **참고용 유지**. Method B(EPA기본REI×DT50)는 접었지만 발표 근거·재검토용으로 남김. 버리지 않음.
- `products.json` = 예전 성분 기준 예시 → 신규 6종 기준으로 갱신 예정.
