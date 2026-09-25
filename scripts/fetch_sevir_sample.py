"""Download a small, reproducible real-event SEVIR sample from public AWS S3.

SEVIR is a real US storm benchmark, not Indian operational data. This utility is
for demonstrating the complete radar/satellite/lightning temporal pipeline tomorrow
without claiming India-specific validation. The bucket is public and needs no AWS
credentials when using the AWS CLI.

The script deliberately downloads only metadata by default. Use --sync-mode for a
small prefix selected by the operator after inspecting the public bucket.
"""
from __future__ import annotations
import argparse
import shutil
import subprocess
from pathlib import Path

BUCKET = "s3://sevir"

def run(args):
    if shutil.which("aws") is None:
        raise SystemExit("AWS CLI is required. Install it, then rerun with --no-sign-request support.")
    command=["aws","s3",*args,"--no-sign-request"]
    print("$", " ".join(command)); subprocess.run(command,check=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("data/external/sevir"))
    parser.add_argument("--prefix",default="data/",help="Public S3 prefix to inspect/sync after checking its size")
    parser.add_argument("--sync-mode",action="store_true",help="Sync the selected prefix; not enabled by default")
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    if not args.sync_mode:
        run(["ls",f"{BUCKET}/{args.prefix}"])
        print(f"Metadata listing complete. To download the selected prefix: --sync-mode --prefix {args.prefix}")
        return 0
    run(["sync",f"{BUCKET}/{args.prefix}",str(args.output)])
    return 0
if __name__ == "__main__": raise SystemExit(main())
