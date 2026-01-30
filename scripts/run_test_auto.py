"""
자동 실행용 테스트 스크립트 (Enter 자동 입력)
"""
import subprocess
import sys
import os

# 프로젝트 디렉토리
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_dir)

# 자동으로 Enter 입력하고 테스트 실행
python_exe = os.path.join(project_dir, "venv", "Scripts", "python.exe")
test_script = os.path.join(project_dir, "scripts", "test_real_images.py")

# Enter 키를 stdin으로 전달
process = subprocess.Popen(
    [python_exe, test_script],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Enter 키 전달
stdout, _ = process.communicate(input="\n")
print(stdout)
sys.exit(process.returncode)
