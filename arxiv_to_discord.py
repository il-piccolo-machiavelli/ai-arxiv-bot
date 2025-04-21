import feedparser
import requests
import os
from datetime import datetime, timedelta

# 카테고리 설정
ARXIV_URL = (
    "http://export.arxiv.org/api/query?search_query="
    "(cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.GR+OR+cat:cs.CL+OR+cat:stat.ML+OR+cat:eess.IV)"
    "&sortBy=submittedDate&max_results=30"
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

def filter_and_post():
    msg_2d, msg_3d = [], []
    for entry in feed.entries:
        updated = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%SZ")
        if updated < yesterday:
            continue
        text = (entry.title + " " + entry.summary).lower()
        url = entry.link

        if any(kw in text for kw in KEYWORDS_2D):
            msg_2d.append(f"🔹 **{entry.title.strip()}**\n{url}")
        if any(kw in text for kw in KEYWORDS_3D):
            msg_3d.append(f"🔸 **{entry.title.strip()}**\n{url}")

    if msg_2d:
        send_to_discord(WEBHOOK_2D, "**📡 오늘의 2D 생성 논문 (arXiv)**\n\n" + "\n\n".join(msg_2d[:5]))
    if msg_3d:
        send_to_discord(WEBHOOK_3D, "**🧱 오늘의 3D 생성 논문 (arXiv)**\n\n" + "\n\n".join(msg_3d[:5]))

filter_and_post()
