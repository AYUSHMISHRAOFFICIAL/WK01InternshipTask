import subprocess
import sys
import os

def main():
    print("Starting pipeline...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    try:
        subprocess.run([sys.executable, '-u', 'scripts/run_describe_only.py'], check=True, env=env)
        print("Pipeline finished successfully. Running export...")
        subprocess.run([sys.executable, '-u', 'scripts/export_final_sheet.py'], check=True, env=env)
        print("Export finished successfully. Running report...")
        subprocess.run([sys.executable, '-u', 'scripts/post_run_report.py'], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error during execution: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
