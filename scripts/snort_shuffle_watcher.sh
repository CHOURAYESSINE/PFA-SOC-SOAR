#!/bin/bash
set -u

ALERT_FILE="/var/log/snort/alert"
HOOK_URL="${SNORT_RELAY_URL:?Configure SNORT_RELAY_URL}"
STATE_DIR="/var/lib/snort-shuffle"
IP_FILE="$STATE_DIR/blocked_ips.txt"
LOG_FILE="/var/log/snort/snort-shuffle-watcher.log"
mkdir -p "$STATE_DIR"
touch "$LOG_FILE" "$IP_FILE"

is_soc_alert() {
  case "$1" in
    *"Nmap SYN scan detected"*|*"TCP SYN port scan detected"*|*"Telnet brute force detected"*|*"SSH brute force detected"*|*"FTP brute force detected"*|*"ICMP ping flood detected"*|*"ICMP ping detected"*|*"PING vers Metasploitable detecte"*|*"HTTP flood detected"*|*"SQL injection"*|*"SQLmap scan detected"*|*"Web XSS attempt detected"*|*"Command injection attempt detected"*) return 0 ;;
    *) return 1 ;;
  esac
}

extract_msg() {
  printf '%s\n' "$1" | sed -n 's/.*\[\*\*\] \(.*\) \[\*\*\].*/\1/p'
}

extract_src() {
  line="$1"
  src="$(printf '%s\n' "$line" | sed -n 's/.*{[A-Z]*} \([0-9][0-9.]*\):[0-9][0-9]* -> .*/\1/p')"
  [ -n "$src" ] || src="$(printf '%s\n' "$line" | sed -n 's/.*{[A-Z]*} \([0-9][0-9.]*\) -> .*/\1/p')"
  printf '%s' "$src"
}

tail -n 0 -F "$ALERT_FILE" | while IFS= read -r line; do
  is_soc_alert "$line" || continue
  sid="$(printf '%s\n' "$line" | sed -n 's/.*\[1:\([0-9][0-9]*\):[0-9][0-9]*\].*/\1/p')"
  src="$(extract_src "$line")"
  # Set protected infrastructure addresses in a space-separated environment variable.
  if [[ " ${PROTECTED_IPS:-} " == *" $src "* ]]; then
    printf '%s ignored infrastructure src=%s\n' "$(date -Is)" "$src" >> "$LOG_FILE"
    continue
  fi
  msg="$(extract_msg "$line")"
  msg="$(printf '%s\n' "$msg" | sed 's/^\[1:[0-9][0-9]*:[0-9][0-9]*\] *//')"
  [ -n "$msg" ] || msg="selected_snort_alert"
  if [ -z "$sid" ] || [ -z "$src" ]; then
    printf '%s parse_failed line=%s\n' "$(date -Is)" "$line" >> "$LOG_FILE"
    continue
  fi

  key="$STATE_DIR/${sid}_${src}"
  now="$(date +%s)"
  last=0
  [ -f "$key" ] && last="$(cat "$key" 2>/dev/null || echo 0)"
  if [ $((now - last)) -lt 10 ]; then
    printf '%s dedupe sid=%s src=%s msg=%s\n' "$(date -Is)" "$sid" "$src" "$msg" >> "$LOG_FILE"
    continue
  fi
  echo "$now" > "$key"

  grep -Fxq "$src" "$IP_FILE" || echo "$src" >> "$IP_FILE"
  blocked_json="$(python3 - "$IP_FILE" <<'PY'
import json, sys, ipaddress
ips = []
for line in open(sys.argv[1], encoding="utf-8"):
    ip = line.strip()
    if not ip:
        continue
    try:
        str(ipaddress.ip_address(ip))
    except ValueError:
        continue
    if ip not in ips:
        ips.append(ip)
print(json.dumps(ips))
PY
)"

  payload="$(python3 - "$src" "$sid" "$msg" "$blocked_json" <<'PY'
import json, sys
src, sid, msg, blocked = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
print(json.dumps({"attacker_ip": src, "sid": sid, "alert": msg, "blocked_ips": blocked}))
PY
)"
  response="$(curl -sS -m 15 -X POST "$HOOK_URL" -H 'Content-Type: application/json' -d "$payload" 2>&1)"
  rc=$?
  printf '%s sent sid=%s src=%s msg=%s blocked=%s rc=%s response=%s\n' "$(date -Is)" "$sid" "$src" "$msg" "$blocked_json" "$rc" "$response" >> "$LOG_FILE"
done
