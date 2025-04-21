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

# 날짜 범위 설정
today = datetime.utcnow()
today_weekday = today.weekday()  # 0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일

if today_weekday in [5, 6, 0]:  # 토, 일, 월요일
    # 지난 금요일 찾기
    days_since_friday = (today_weekday + 2) % 7  # 토:0, 일:1, 월:2
    target_date = today - timedelta(days=days_since_friday)
else:  # 화, 수, 목, 금요일
    # 어제 찾기
    target_date = today - timedelta(days=1)

# 타겟 날짜의 00:00:00 ~ 23:59:59 설정
start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
end_date = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

feed = feedparser.parse(ARXIV_URL)

def send_to_discord(webhook_url, content):
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
    weekday_names = ['월', '화', '수', '목', '금', '토', '일']
    print(f"\n🗓️ 오늘: {today.strftime('%Y-%m-%d')} ({weekday_names[today_weekday]})")
    print(f"📅 타겟 날짜: {target_date.strftime('%Y-%m-%d')} ({weekday_names[target_date.weekday()]})")
    print(f"⏰ 수집 범위: {start_date.strftime('%Y-%m-%d %H:%M')} ~ {end_date.strftime('%Y-%m-%d %H:%M')}")
    
    print("\n📄 수집된 논문 제목 및 날짜 목록:")
    
    for i, entry in enumerate(feed.entries):
        title = entry.title.strip()
        updated = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%SZ")
        
        # 날짜 정보 출력
        print(f" {i+1}. [{updated.strftime('%Y-%m-%d %H:%M')}] {title}")
        
        # 타겟 날짜 범위에 포함되는지 확인
        if start_date <= updated <= end_date:
            print(f"   ✅ PASS: 타겟 날짜 범위 내 ({start_date} <= {updated} <= {end_date})")
            
            text = (entry.title + " " + entry.summary).lower()
            
            # 키워드 매칭 디버깅
            if contains_keyword(text, KEYWORDS_2D):
                print(f"   👉 [2D 매칭됨] {entry.title.strip()}")
                msg_2d.append(f"🔹 **{entry.title.strip()}**\n{entry.link}")
            
            if contains_keyword(text, KEYWORDS_3D):
                print(f"   👉 [3D 매칭됨] {entry.title.strip()}")
                msg_3d.append(f"🔸 **{entry.title.strip()}**\n{entry.link}")
        else:
            print(f"   ⏭️ SKIP: 타겟 날짜 범위 밖 (not in {start_date} ~ {end_date})")

    print(f"\n📊 필터링 결과:")
    print(f"- 2D 논문: {len(msg_2d)}개")
    print(f"- 3D 논문: {len(msg_3d)}개")

    target_date_str = target_date.strftime('%Y-%m-%d')
    
    if msg_2d:
        send_to_discord(WEBHOOK_2D, f"**📡 {target_date_str} 2D 생성 논문 (arXiv)**\n\n" + "\n\n".join(msg_2d[:5]))
    else:
        print("❌ 2D 논문이 없어 Discord 전송을 생략합니다.")
    
    if msg_3d:
        send_to_discord(WEBHOOK_3D, f"**🧱 {target_date_str} 3D 생성 논문 (arXiv)**\n\n" + "\n\n".join(msg_3d[:5]))
    else:
        print("❌ 3D 논문이 없어 Discord 전송을 생략합니다.")

filter_and_post()
