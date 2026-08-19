#!/usr/bin/env python3
"""Download photos from an instagram-profile-scraper JSON export.

Reads the scrape JSON (see dataset_instagram-profile-scraper_*.json) and
downloads: the HD profile picture (logo) and every post's image / video-poster
frame into an assets/photos/ folder. Sidecar child images are included.

Usage:
    python download_instagram_photos.py <profile.json> [--out assets] [--logo-out assets/logo.jpg]
"""
import argparse
import json
import os
import sys
import urllib.request

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Referer": "https://www.instagram.com/",
}


def looks_like(data: bytes, dest: str) -> bool:
    """Does the body actually carry the format the filename promises?

    A CDN that 404s often answers with a perfectly large HTML error page.
    Trusting the byte count alone once saved a 35KB "not found" page as both
    a .jpg and an .mp4, and the site shipped it for nine commits.
    """
    ext = os.path.splitext(dest)[1].lower()
    if ext in (".jpg", ".jpeg"):
        return data[:3] == b"\xff\xd8\xff"
    if ext == ".png":
        return data[:8] == b"\x89PNG\r\n\x1a\n"
    if ext == ".mp4":
        return data[4:8] == b"ftyp"
    return True


def download(url: str, dest: str) -> bool:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"  skip (exists): {dest}")
        return True
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            status = getattr(r, "status", 200)
            ctype = r.headers.get("Content-Type", "")
            data = r.read()
        if status != 200:
            print(f"  FAIL (HTTP {status}): {dest}")
            return False
        if len(data) < 1000:
            print(f"  FAIL (tiny body {len(data)}B): {dest}")
            return False
        if not looks_like(data, dest):
            print(f"  FAIL (el cuerpo no es {os.path.splitext(dest)[1]}, "
                  f"Content-Type: {ctype or '?'}): {dest}")
            return False
        with open(dest, "wb") as f:
            f.write(data)
        print(f"  ok {len(data)//1024}KB: {dest}")
        return True
    except Exception as e:
        print(f"  FAIL {type(e).__name__}: {dest} ({e})")
        return False


def run(profile_path: str, out_dir: str = "assets/photos",
        logo_out: str = None, vid_dir: str = "assets/videos"):
    data = json.load(open(profile_path))
    # profile may be a bare dict or a one-element list
    prof = data[0] if isinstance(data, list) else data

    if logo_out and prof.get("profilePicUrlHD"):
        download(prof["profilePicUrlHD"], logo_out)

    posts = prof.get("latestPosts", [])
    for i, post in enumerate(posts):
        disp = post.get("displayUrl")
        if disp:
            download(disp, os.path.join(out_dir, f"post{i:02d}.jpg"))
        for j, child in enumerate(post.get("images") or []):
            download(child, os.path.join(out_dir, f"post{i:02d}_child{j}.jpg"))
        vid = post.get("videoUrl")
        if vid:
            download(vid, os.path.join(vid_dir, f"post{i:02d}.mp4"))

    print("\nDone.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("profile_json")
    ap.add_argument("--out", default="assets/photos")
    ap.add_argument("--logo-out", default="assets/logo.jpg")
    ap.add_argument("--videos-out", default="assets/videos")
    args = ap.parse_args()
    if not os.path.exists(args.profile_json):
        print(f"JSON not found: {args.profile_json}", file=sys.stderr)
        sys.exit(1)
    run(args.profile_json, args.out, args.logo_out, args.videos_out)


if __name__ == "__main__":
    main()