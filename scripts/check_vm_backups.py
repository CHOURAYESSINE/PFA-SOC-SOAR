"""Check local backup disks required by the public VM definitions. No writes to VMs."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def check_backups(backup_root):
    backup_root = Path(backup_root).resolve()
    records = json.loads((ROOT / "vms/disks-manifest.json").read_text(encoding="utf-8-sig"))
    results = []
    for record in records:
        disk = (backup_root / record["vm"] / record["disk"]).resolve()
        if not disk.is_relative_to(backup_root):
            raise ValueError("Disk path escapes backup root")
        vmx_files = list((ROOT / "vms" / record["vm"]).glob("*.vmx"))
        if len(vmx_files) != 1:
            raise ValueError("Expected one VMX per VM")
        text = vmx_files[0].read_text(encoding="utf-8-sig")
        references = re.findall(r'(?m)^\S+\.fileName\s*=\s*"([^"\n]+\.vmdk)"', text)
        exists = disk.is_file()
        size_matches = exists and disk.stat().st_size == record["bytes"]
        results.append({"vm": record["vm"], "disk_exists": exists,
                        "size_matches_manifest": size_matches,
                        "vmx_disk_reference_matches": references == [record["disk"]]})
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backup_root", type=Path)
    args = parser.parse_args()
    results = check_backups(args.backup_root)
    print(json.dumps(results, indent=2))
    raise SystemExit(0 if all(all(v for k, v in row.items() if k != "vm") for row in results) else 1)