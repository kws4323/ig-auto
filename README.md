# 인스타그램 카드뉴스 자동 발행 (GitHub Actions)

컴퓨터를 켜두지 않아도, GitHub 서버에서 대신 실행되어 인스타그램에 캐러셀(여러 장) 게시물을 올려주는 자동화입니다.
(제가 지금 작업하는 클라우드 세션은 보안 정책상 인스타그램 API 도메인에 직접 접속할 수 없어서, GitHub Actions를 대신 사용합니다.)

## 1. GitHub 저장소 만들기

1. github.com에서 새 저장소(Repository)를 만듭니다. **Public**으로 만들어주세요 (이미지가 `raw.githubusercontent.com`을 통해 공개적으로 접근 가능해야 인스타그램 서버가 가져갈 수 있습니다. 민감한 내용은 없으니 공개해도 무방합니다).
2. 이 폴더(`ig-autopost`) 안의 파일들을 그 저장소에 그대로 올립니다 (`images/` 폴더, `post_instagram_carousel.py`, `requirements.txt`, `.github/workflows/post-instagram.yml` 전부 포함).

## 2. 저장소 Secrets 등록

저장소의 **Settings → Secrets and variables → Actions → New repository secret** 에서 2개를 등록합니다.

- `IG_ACCESS_TOKEN` : 인스타그램 Graph API 액세스 토큰 (IGAA로 시작하는 값)
- `IG_USER_ID` : 인스타그램 비즈니스/크리에이터 계정의 숫자 ID

### IG_USER_ID를 모르는 경우

본인 컴퓨터나 휴대폰 브라우저 주소창에 아래 주소를 입력해서 확인할 수 있습니다 (TOKEN 자리에 실제 토큰을 넣으세요):

```
https://graph.instagram.com/v21.0/me?fields=id,username&access_token=TOKEN
```

`{"id":"1789...", "username":"..."}` 형태로 응답이 오면 그 `id` 값이 `IG_USER_ID`입니다.

## 3. 실행 방법

- **수동 실행**: 저장소의 **Actions** 탭 → "인스타그램 카드뉴스 발행" 워크플로 선택 → **Run workflow** 클릭. 캡션을 바꾸고 싶으면 입력창에 적고 실행하면 됩니다.
- **매일 자동 실행**: `.github/workflows/post-instagram.yml` 파일 안의 `schedule` 부분 주석(`#`)을 해제하면 지정한 시각(cron, UTC 기준)에 컴퓨터 없이도 자동으로 발행됩니다.

## 4. 새로운 카드뉴스로 교체하려면

`images/card_1.png` ~ `card_9.png` 파일을 새 카드뉴스 이미지로 교체(같은 파일명 유지 또는 정렬 순서 유지)하고 저장소에 반영(commit)한 뒤, 워크플로를 다시 실행하면 됩니다.

## 참고

- 캐러셀은 최소 2장, 최대 10장까지 지원됩니다.
- 액세스 토큰은 만료될 수 있습니다 (기본 발급 토큰은 보통 짧고, 장기 토큰으로 교환 가능합니다 — 만료 시 재발급해서 Secret 값을 갱신해주세요).
- 토큰은 저장소 Secrets에만 저장하고, 코드나 커밋에는 절대 직접 적지 마세요.
