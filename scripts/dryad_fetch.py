#!/usr/bin/env python3
"""Download files from datadryad.org, solving the Anubis PoW challenge.

Usage: dryad_fetch.py <file_id_or_url> <output_path>
"""
import re, json, urllib.parse, hashlib, time, sys, urllib.request, http.cookiejar

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
BASE = "https://datadryad.org"


def make_opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", UA)]
    return op


def fetch_html(op, url):
    for attempt in range(6):
        try:
            r = op.open(url, timeout=60)
            return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 403 and attempt < 5:
                time.sleep(2 * (attempt + 1))
                continue
            raise


def get(op, url):
    raw = fetch_html(op, url)
    try:
        txt = raw.decode()
    except UnicodeDecodeError:
        return raw
    if "anubis_challenge" not in txt:
        return raw
    m = re.search(r'anubis_challenge"[^>]*>(\{.*?\})\s*</script', txt, re.S)
    if not m:
        return raw
    chal = json.loads(m.group(1))
    rd = chal["challenge"]["randomData"]
    cid = chal["challenge"]["id"]
    diff = int(chal["rules"]["difficulty"])
    target = "0" * diff
    t0 = time.time()
    n = 0
    while True:
        h = hashlib.sha256((rd + str(n)).encode()).hexdigest()
        if h.startswith(target):
            break
        n += 1
    elapsed = int((time.time() - t0) * 1000)
    qs = urllib.parse.urlencode({
        "id": cid, "response": h, "nonce": n,
        "redir": url, "elapsedTime": elapsed,
    })
    resp = op.open(BASE + "/.within.website/x/cmd/anubis/api/pass-challenge?" + qs, timeout=30)
    resp.read()
    time.sleep(1)
    return fetch_html(op, url)


def main():
    target, out = sys.argv[1], sys.argv[2]
    url = target if target.startswith("http") else f"{BASE}/downloads/file_stream/{target}"
    op = make_opener()
    data = get(op, url)
    if data[:1] == b"<" and b"anubis" in data[:2000]:
        raise SystemExit("FAILED: still behind Anubis after solve")
    with open(out, "wb") as f:
        f.write(data)
    print(f"saved {len(data)} bytes -> {out}")


if __name__ == "__main__":
    main()
