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

yesterday = datetime.utcnow() - timedelta(days=1)
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
    print("📄 수집된 논문 제목 목록:")
    for entry in feed.entries:
        title = entry.title.strip()
        print(f" - {title}")

    for entry in feed.entries:
        updated = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%SZ")
        if updated < yesterday:
            continue

        text = (entry.title + " " + entry.summary).lower()
        if contains_keyword(text, KEYWORDS_2D):
            print(f"👉 [2D 매칭됨] {entry.title.strip()}")
            msg_2d.append(f"🔹 **{entry.title.strip()}**\n{entry.link}")
        if contains_keyword(text, KEYWORDS_3D):
            print(f"👉 [3D 매칭됨] {entry.title.strip()}")
            msg_3d.append(f"🔸 **{entry.title.strip()}**\n{entry.link}")

    if msg_2d:
        send_to_discord(WEBHOOK_2D, "**📡 오늘의 2D 생성 논문 (arXiv)**\n\n" + "\n\n".join(msg_2d[:5]))
    if msg_3d:
        send_to_discord(WEBHOOK_3D, "**🧱 오늘의 3D 생성 논문 (arXiv)**\n\n" + "\n\n".join(msg_3d[:5]))

filter_and_post()
