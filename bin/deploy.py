#!/usr/bin/env python3
from pathlib import Path
from fabric import Connection, config
from decouple import config as decouple

# Read from env
REMOTE_HOST = decouple("REMOTE_HOST", default="localhost")
REMOTE_PORT = decouple("REMOTE_PORT", default=22, cast=int)
REMOTE_USER = decouple("REMOTE_USER", default="root")
REMOTE_SUDO_PASSWORD = decouple("REMOTE_SUDO_PASSWORD")
REPO_URL = decouple("REPO_URL", default="example.com")
REPO_NAME = str(Path(REPO_URL).name)
SITE_NAME = REPO_NAME.split("-")[0]

# Set up fabric
fabric_config = config.Config(overrides={
    "run": {"hide": True},
    "sudo": {"password": REMOTE_SUDO_PASSWORD}})
conn_info = f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_PORT}"
target = Connection(conn_info, config=fabric_config)

# Deploy
dir_exists = target.run(f"file /tmp/{REPO_NAME}").exited == 0
if dir_exists:
    target.run("rm -rf /tmp/{REPO_NAME}")

target.sudo(f"rm -rf /var/www/{SITE_NAME}", pty=True)
target.sudo(f"mkdir /var/www/{SITE_NAME}", pty=True)

print(f"[$] Cloning {REPO_URL}...")
target.run(f"git clone {REPO_URL} /tmp/{REPO_NAME}")

print("[$] Updating files...")
target.sudo(f"cp -r /tmp/{REPO_NAME}/* /var/www/{SITE_NAME}", pty=True)
target.run(f"rm -rf /tmp/{REPO_NAME}")

print("[$] Restarting nginx.service...")
target.sudo("systemctl restart nginx", pty=True)

print("[+] Done!")
