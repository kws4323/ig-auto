#!/usr/bin/env python3
"""
인스타그램 캐러셀(여러 장) 게시물 자동 업로드 스크립트.

Instagram Graph API (Instagram Login 방식, graph.instagram.com 호스트) 사용.
GitHub Actions 등 컴퓨터가 꺼져 있어도 동작하는 환경에서 실행하도록 설계됨.

필요 환경변수:
  IG_ACCESS_TOKEN   - 인스타그램 Graph API 액세스 토큰 (IGAA로 시작)
  IG_USER_ID        - 인스타그램 비즈니스/크리에이터 계정 ID (숫자)
  IMAGE_URLS        - 콤마(,)로 구분된, 공개적으로 접근 가능한 이미지 URL 목록 (2~10장)
  CAPTION           - (선택) 게시물 캡션. 없으면 기본 문구 사용.

사용 예:
  IG_ACCESS_TOKEN=... IG_USER_ID=... \
  IMAGE_URLS="https://.../card_1.png,https://.../card_2.png" \
  CAPTION="오늘의 국장 브리핑" \
  python3 post_instagram_carousel.py
"""

import os
import sys
import time
import requests

GRAPH_API_VERSION = "v21.0"
GRAPH_HOST = "https://graph.instagram.com"

DEFAULT_CAPTION = "오늘의 국장 브리핑 📈\n\n매일 국내 증시 마감 브리핑을 카드뉴스로 전해드려요.\n\n#주식 #국장 #코스피 #코스닥 #주식한량 #오늘의증시"


def die(msg: str) -> None:
    print(f"[오류] {msg}", file=sys.stderr)
    sys.exit(1)


def api_post(path: str, params: dict) -> dict:
    url = f"{GRAPH_HOST}/{GRAPH_API_VERSION}/{path}"
    resp = requests.post(url, data=params, timeout=60)
    data = resp.json()
    if resp.status_code >= 400 or "error" in data:
        die(f"Graph API 요청 실패 ({path}): {data}")
    return data


def api_get(path: str, params: dict) -> dict:
    url = f"{GRAPH_HOST}/{GRAPH_API_VERSION}/{path}"
    resp = requests.get(url, params=params, timeout=60)
    data = resp.json()
    if resp.status_code >= 400 or "error" in data:
        die(f"Graph API 요청 실패 ({path}): {data}")
    return data


def wait_until_finished(container_id: str, token: str, timeout_sec: int = 120) -> None:
    """미디어 컨테이너가 FINISHED 상태가 될 때까지 대기."""
    start = time.time()
    while time.time() - start < timeout_sec:
        data = api_get(container_id, {"fields": "status_code", "access_token": token})
        status = data.get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            die(f"미디어 컨테이너 처리 실패: {container_id}")
        time.sleep(3)
    die(f"미디어 컨테이너 처리 시간 초과: {container_id}")


def main() -> None:
    token = os.environ.get("IG_ACCESS_TOKEN")
    ig_user_id = os.environ.get("IG_USER_ID")
    image_urls_raw = os.environ.get("IMAGE_URLS")
    caption = os.environ.get("CAPTION", DEFAULT_CAPTION)

    if not token:
        die("환경변수 IG_ACCESS_TOKEN이 설정되지 않았습니다.")
    if not ig_user_id:
        die("환경변수 IG_USER_ID가 설정되지 않았습니다.")
    if not image_urls_raw:
        die("환경변수 IMAGE_URLS가 설정되지 않았습니다. (콤마로 구분된 공개 이미지 URL 목록)")

    image_urls = [u.strip() for u in image_urls_raw.split(",") if u.strip()]
    if not (2 <= len(image_urls) <= 10):
        die(f"캐러셀은 2~10장이어야 합니다. 현재 {len(image_urls)}장.")

    print(f"[1/3] 이미지 {len(image_urls)}장에 대한 미디어 컨테이너 생성 중...")
    child_ids = []
    for i, url in enumerate(image_urls, start=1):
        data = api_post(
            f"{ig_user_id}/media",
            {"image_url": url, "is_carousel_item": "true", "access_token": token},
        )
        container_id = data["id"]
        print(f"  - ({i}/{len(image_urls)}) 컨테이너 생성됨: {container_id}")
        wait_until_finished(container_id, token)
        child_ids.append(container_id)

    print("[2/3] 캐러셀 컨테이너 생성 중...")
    carousel_data = api_post(
        f"{ig_user_id}/media",
        {
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption,
            "access_token": token,
        },
    )
    carousel_id = carousel_data["id"]
    wait_until_finished(carousel_id, token)
    print(f"  - 캐러셀 컨테이너 준비 완료: {carousel_id}")

    print("[3/3] 게시물 발행 중...")
    publish_data = api_post(
        f"{ig_user_id}/media_publish",
        {"creation_id": carousel_id, "access_token": token},
    )
    print(f"완료! 게시된 미디어 ID: {publish_data['id']}")


if __name__ == "__main__":
    main()
