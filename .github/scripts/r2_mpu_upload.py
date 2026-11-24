#!/usr/bin/env python3
"""R2 multipart upload (r2htmlbig at rhb.d51.dpdns.org).
Usage: python3 r2_mpu_upload.py <local_file> <remote_key> [parts]
Password via env R2_UPLOAD_PASSWORD (or arg 4).
"""
import json, subprocess, os, sys, math

HOST = os.environ.get("R2_HOST", "https://rhb.d51.dpdns.org")

def curl(args, timeout=600):
    cmd = ["curl", "-s", "--noproxy", "*", "-m", str(timeout)] + args
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+15)
    if r.returncode != 0:
        print("CURL FAIL:", cmd[-1][:80], r.stderr[:200], flush=True)
        sys.exit(1)
    return r.stdout

def main():
    if len(sys.argv) < 3:
        print("usage: r2_mpu_upload.py <local> <key> [nparts] [password]")
        sys.exit(1)
    local = sys.argv[1]
    key = sys.argv[2]
    nparts = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    pw = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("R2_UPLOAD_PASSWORD", "")
    if not pw:
        print("no password (R2_UPLOAD_PASSWORD env or arg4)")
        sys.exit(1)

    fsize = os.path.getsize(local)
    part_size = math.ceil(fsize / nparts)
    # 保证前 nparts-1 片等长、最后一片 <= part_size
    # R2 要求：除最后一片外所有片完全等长
    BASE = f"{HOST}/mpu/{key}"

    # 1. create
    out = curl(["-X", "POST", "-H", f"Password: {pw}", f"{BASE}?action=mpu-create"])
    d = json.loads(out)
    uploadId = d.get("uploadId")
    if not uploadId:
        print("mpu-create failed:", out[:200]); sys.exit(1)
    print(f"[create] uploadId={uploadId[:16]}...", flush=True)

    # 2. upload parts (all equal except last)
    parts = []
    with open(local, "rb") as f:
        # 计算实际片数：让最后一片 <= part_size
        total_parts = math.ceil(fsize / part_size)
        for i in range(1, total_parts + 1):
            chunk = f.read(part_size) if i < total_parts else f.read()
            tmpf = f"/tmp/mpu_part_{i}"
            open(tmpf, "wb").write(chunk)
            out = curl(["-X", "PUT", "-H", f"Password: {pw}",
                        "--data-binary", f"@{tmpf}",
                        f"{BASE}?action=mpu-uploadpart&uploadId={uploadId}&partNumber={i}"])
            dd = json.loads(out)
            etag = dd.get("etag")
            if not etag:
                print(f"[part {i}] FAILED:", out[:200]); sys.exit(1)
            print(f"[part {i}/{total_parts}] {len(chunk)}B etag={etag[:14]}", flush=True)
            parts.append({"partNumber": i, "etag": etag})
            os.remove(tmpf)

    # 3. complete (password in body)
    body = json.dumps({"parts": parts, "password": pw})
    open("/tmp/mpu_complete.json", "w").write(body)
    out = curl(["-X", "POST", "-H", "Content-Type: application/json",
                "--data-binary", "@/tmp/mpu_complete.json",
                f"{BASE}?action=mpu-complete&uploadId={uploadId}"])
    d = json.loads(out)
    if not d.get("success"):
        print("[complete] FAILED:", out[:250]); sys.exit(1)
    print(f"[complete] OK etag={d.get('etag')}", flush=True)
    print("DONE")

if __name__ == "__main__":
    main()
