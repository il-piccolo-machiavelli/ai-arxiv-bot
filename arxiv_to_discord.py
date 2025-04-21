import feedparser
import requests
import os
from datetime import datetime, timedelta

ARXIV_URL = (
    "http://export.arxiv.org/api/query?search_query="
    "(cat:cs.CV+OR+cat:cs.GR+OR+cat:eess.IV)"
    "&sortBy=submittedDate&max_results=60"
)

KEYWORDS_2D = [
    "text-to-image", "image-to-image", "diffusion", "latent diffusion",
    "gan", "vae", "autoregressive", "normalizing flow", "energy-based"
]

KEYWORDS_3D = [
    "text-to-3d", "image-to-3d", "3d reconstruction", "point cloud", "mesh",
    "polygon mesh", "solid", "solid modeling", "nerf", "3dgs", "sdf", "stylesdf",
    "deepcad", "3d-gpt", "csg", "csgnet", "occupancy network",
    "latent point diffusion model", "meshgpt", "point-e", "get3d", "atlasnet", "cad agent"
]

WEBHOOK_2D = os.environ["WEBHOOK_2D"]
WEBHOOK_3D = os.environ["WEBHOOK_3D"]

# 주말과 평일을 고려한 날짜 기준 설정
today_weekday = datetime.utcnow().weekday()
if today_weekday == 0:  # 월요일
    days_ago = 3  # 금요일 논문까지 포함
elif today_weekday == 1:  # 화요일
    days_ago = 4  # 금요일 논문까지 포함
else:
    days_ago = 1  # 어제 논문만

date_threshold = datetime.utcnow() - timedelta(days=days_ago)
feed = feedparser.parse(ARXIV_URL)

def send_to_discord(webhook_url, content):
    requests.post(webhook_url, json={"content": content})
    response = requests.post(webhook_url, json={"content": content})
    print(f"📤 Discord 전송 응답: {response.status_code}")
    if response.status_code != 204:
        print(f"❗ 응답 본문: {response.text}")

def contains_keyword(text, keywords):
    clean_text = text.replace("-", "").replace("\n", "").replace(" ", "")
    return any(kw.replace(" ", "") in clean_text for kw in keywords)

print(f"🧪 Webhook 2D 존재 여부: {'WEBHOOK_2D' in os.environ}")
print(f"📡 Webhook 2D 길이: {len(os.environ.get('WEBHOOK_2D', ''))}")

def filter_and_post():
    msg_2d, msg_3d = [], []

    print(f"✅ arXiv에서 받은 논문 수: {len(feed.entries)}개")
    
    # 날짜 비교 정보 출력
    print(f"\n🗓️ 기준 날짜 (UTC): {date_threshold}")
    print(f"🕒 현재 시간 (UTC): {datetime.utcnow()}")
    print(f"📅 요일 기준: {['월', '화', '수', '목', '금', '토', '일'][today_weekday]}요일, {days_ago}일 전 논문까지 포함")
    
    print("\n📄 수집된 논문 제목 및 날짜 목록:")
    
    for i, entry in enumerate(feed.entries):
        title = entry.title.strip()
        updated = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%SZ")
        
        # 날짜 정보 출력
        print(f" {i+1}. [{updated.strftime('%Y-%m-%d %H:%M')}] {title}")
        
        if updated < date_threshold:
            print(f"   ⏭️ SKIP: 날짜가 기준보다 이전임 ({updated} < {date_threshold})")
            continue
        else:
            print(f"   ✅ PASS: 날짜 조건 통과 ({updated} >= {date_threshold})")

        text = (entry.title + " " + entry.summary).lower()
        
        # 키워드 매칭 디버깅
        if contains_keyword(text, KEYWORDS_2D):
            print(f"   👉 [2D 매칭됨] {entry.title.strip()}")
            msg_2d.append(f"🔹 **{entry.title.strip()}**\n{entry.link}")
        
        if contains_keyword(text, KEYWORDS_3D):
            print(f"   👉 [3D 매칭됨] {entry.title.strip()}")
            msg_3d.append(f"🔸 **{entry.title.strip()}**\n{entry.link}")

    print(f"\n📊 필터링 결과:")
    print(f"- 2D 논문: {len(msg_2d)}개")
    print(f"- 3D 논문: {len(msg_3d)}개")

    if msg_2d:
        send_to_discord(WEBHOOK_2D, "**📡 오늘의 2D 생성 논문 (arXiv)**\n\n" + "\n\n".join(msg_2d[:5]))
    else:
        print("❌ 2D 논문이 없어 Discord 전송을 생략합니다.")
    
    if msg_3d:
        send_to_discord(WEBHOOK_3D, "**🧱 오늘의 3D 생성 논문 (arXiv)**\n\n" + "\n\n".join(msg_3d[:5]))
    else:
        print("❌ 3D 논문이 없어 Discord 전송을 생략합니다.")

filter_and_post()
