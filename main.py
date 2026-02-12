#!/usr/bin/env python3
"""
Simple Mapillary image downloader.

Requirements:
    pip install requests
"""

import os
import sys
import requests
import time

# ----------------------------------------------------------------------
# USER SETTINGS –‑ edit these ------------------------------------------------
MAPILLARY_TOKEN = "****"   # <-- replace with yours
RADIUS_M      = 10        # search radius in metres (max 100 m for free tier)
OUTPUT_DIR    = "./mapillary_images"
a = 19.415758, -99.141010
b = 19.416421, -99.140908
# ----------------------------------------------------------------------


def ensure_dir(path: str) -> None:
    """Create output directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def search_image(lat: float, lon: float, radius: int = 50) -> dict | None:
    """
    Query the Mapillary Images endpoint for photos near (lat, lon).

    Returns the JSON dict of the first image found, or None if none.
    """
    url = "https://graph.mapillary.com/images"
    params = {
        "access_token": MAPILLARY_TOKEN,
        "fields": "id,captured_at,thumb_original_url",
        "bbox": f"{lon-radius/111320},{lat-radius/110540},{lon+radius/111320},{lat+radius/110540}",
        "limit": 1,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("data"):
        print(len(data["data"]), 'images found')
        return data["data"][0]   # first (and only) image in the result set
    return None


def download_image(image_meta: dict, out_dir: str) -> str:
    """
    Download the original image using the thumbnail URL (which redirects
    to the full‑resolution file). Returns the local file path.
    """
    img_id = image_meta["id"]
    thumb_url = image_meta["thumb_original_url"]

    # The thumbnail URL redirects to the original image; follow it.
    resp = requests.get(thumb_url, stream=True, timeout=15)
    resp.raise_for_status()

    ext = os.path.splitext(resp.url)[1] or ".jpg"
    out_path = os.path.join(out_dir, f"{img_id}{ext}")

    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return out_path


def main(LATITUDE, LONGITUDE) -> None:
    ensure_dir(OUTPUT_DIR)

    print(f"🔎 Searching for images within {RADIUS_M} m of ({LATITUDE}, {LONGITUDE}) …")
    img = search_image(LATITUDE, LONGITUDE, RADIUS_M)

    if not img:
        print("❌ No images found in the specified area.")
        return None        
        # sys.exit(1)

    print(f"📷 Found image ID {img['id']} captured at {img['captured_at']}")
    saved_path = download_image(img, OUTPUT_DIR)
    print(f"✅ Image saved to: {saved_path}")


if __name__ == "__main__":
    for i in range(-10,10):
        alt = a[0]*(i/6) + b[0]*(1-i/6)
        lon = a[1]*(i/6) + b[1]*(1-i/6)
        main(alt, lon)
        time.sleep(5)
        print(i, 'done!')  # be nice to the API