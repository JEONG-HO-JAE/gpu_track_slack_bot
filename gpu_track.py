# -*- coding: utf-8 -*-
import subprocess
import json
from get_gpu_id_from_sp import get_gpu_user_mappings

WEBHOOK_URL = "https://hooks.slack.com/services/YOURAPPSID"  # 본인의 웹훅 URL

def send_slack_message(message):
    """
    Send a message to Slack via webhook.

    Parameters:
        message (str): The message to send to Slack.
    """
    payload = {"text": message}  # Message content
    try:
        subprocess.run(
            ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json",
             "-d", json.dumps(payload), WEBHOOK_URL],
            stdout=subprocess.DEVNULL,  # Suppress standard output
            stderr=subprocess.DEVNULL   # Suppress standard error
        )
    except subprocess.CalledProcessError as e:
        print("Slack message failed: {}".format(e))


def get_gpu_processes_with_users_and_gpu():
    """GPU에서 실행 중인 프로세스의 사용자 정보와 GPU 번호 수집"""
    try:
        nvidia_command = (
            "nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory "
            "--format=csv,noheader,nounits | while IFS=',' read -r gpu_uuid pid process_name used_memory; "
            "do gpu_index=$(nvidia-smi -L | grep \"$gpu_uuid\" | awk '{print $2}' | tr -d ':'); "
            "user=$(ps -o user= -p $pid 2>/dev/null); "
            "echo \"GPU: $gpu_index, User: $user, PID: $pid, Process: $process_name, Used Memory: ${used_memory}MiB\"; "
            "done"
        )
        result = subprocess.check_output(nvidia_command, shell=True, executable="/bin/bash").decode().strip()
        return result.split("\n")
    except subprocess.CalledProcessError as e:
        print(f"nvidia-smi 실행 실패: {e}")
        return []


def construct_current_gpu_users(processes):
    """
    GPU에서 실행 중인 프로세스 데이터를 기반으로
    AUTHORIZED_GPU_USERS 구조 생성
    """
    authorized_gpu_users = {}

    for process in processes:
        try:
            gpu_number = int(process.split(",")[0].split(":")[1].strip())
            user = process.split(",")[1].split(":")[1].strip()
            if gpu_number not in authorized_gpu_users:
                authorized_gpu_users[gpu_number] = []
            if user not in authorized_gpu_users[gpu_number]:
                authorized_gpu_users[gpu_number].append(user)
        except (IndexError, ValueError):
            print(f"데이터 파싱 실패: {process}")
            continue

    return authorized_gpu_users


def find_violations(authorized_users, exception_users, active_users):
    """
    허가된 사용자, 예외 사용자, 실제 GPU 사용자를 비교하여
    허가되지 않은 사용자를 찾는 함수.
    """
    violations = []

    for gpu_number, users in active_users.items():
        for user in users:
            assigned_gpus = [gpu for gpu, allowed_users in authorized_users.items() if user in allowed_users]

            all_authorized_users = set(user for users in authorized_users.values() for user in users)
            all_exception_users = set(user for users in exception_users.values() for user in users)

            if user not in all_authorized_users and user not in all_exception_users:
                violations.append(
                    f"CRITICAL ISSUE: {user} is using GPU {gpu_number}, but is not authorized for any GPU"
                )

            elif gpu_number not in assigned_gpus and user not in exception_users.get(gpu_number, []):
                violations.append(
                    f"WARNING: {user} is using GPU {gpu_number}, but is only authorized for GPUs {assigned_gpus}"
                )

    return violations


def print_gpu_processes_and_users():
    """GPU 프로세스 및 사용자 정보 출력"""
    processes = get_gpu_processes_with_users_and_gpu()
    if not processes:
        print("현재 GPU에서 실행 중인 프로세스가 없습니다.")
        return

    print("==============GPU에서 실행 중인 프로세스 목록=================")
    for process in processes:
        print(process)

    authorized_users, exception_users = get_gpu_user_mappings()
    active_gpu_users = construct_current_gpu_users(processes)

    print("\nAUTHORIZED_GPU_USERS (from Google Sheets):")
    print(authorized_users)

    print("\nCurrently Active GPU Users:")
    print(active_gpu_users)

    violations = find_violations(authorized_users, exception_users, active_gpu_users)
    if violations:
        print("\n=== Violations Found ===")
        for violation in violations:
            print(violation)
            send_slack_message(violation)  # Slack으로 위반 사항 전송
    else:
        print("\nNo violations found. All users are authorized.")


if __name__ == "__main__":
    print_gpu_processes_and_users()