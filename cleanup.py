import os, shutil

DELETIONS = [
    "finlume-backend/temp.txt",
    "finlume-backend/test_final_output.txt",
    "finlume-backend/test_final_qa.txt",
    "finlume-backend/test_out.txt",
    "finlume-backend/test_phase6_out.txt",
    "finlume-backend/pytest_output_clean.txt",
    "finlume-backend/audit_test.txt",
    "finlume-backend/error_log.txt",
    "finlume-frontend/build_out.txt",
    "finlume-frontend/err.txt",
    "finlume-frontend/err2.txt"
]

MOVES = [
    ("finlume-frontend/run_tsc.py", "scripts/dev/run_tsc.py"),
    ("finlume-frontend/run_vite.py", "scripts/dev/run_vite.py"),
    ("finlume-backend/trace_dumper.py", "scripts/dev/trace_dumper.py"),
    ("finlume-backend/read_log.py", "scripts/dev/read_log.py"),
    ("finlume-backend/patch_attrs.py", "scripts/dev/patch_attrs.py"),
    ("finlume-backend/run_pytest.py", "scripts/dev/run_pytest.py"),
    ("finlume-backend/refactor_tests.py", "scripts/dev/refactor_tests.py"),
    ("finlume-backend/refactor_transaction.py", "scripts/dev/refactor_transaction.py")
]

os.makedirs("scripts/dev", exist_ok=True)

deleted = []
for p in DELETIONS:
    if os.path.exists(p):
        os.remove(p)
        deleted.append(p)
        
moved = []
for src, dst in MOVES:
    if os.path.exists(src):
        os.rename(src, dst)
        moved.append((src, dst))

# Also purge logs folder except .gitkeep
log_dir = "finlume-backend/logs"
if os.path.exists(log_dir):
    for f in os.listdir(log_dir):
        if f != ".gitkeep":
            p = os.path.join(log_dir, f)
            if os.path.isfile(p):
                os.remove(p)
                deleted.append(p)

print(f"Deleted: {deleted}")
print(f"Moved: {moved}")
