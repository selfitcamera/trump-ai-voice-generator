import requests
import time
import uuid
import os
from datetime import datetime
from supabase import create_client, Client

try:
    OneKey = os.environ['OneKey'].strip()

    OneKey = OneKey.split("#")
    TrumpAiUrl = OneKey[0]
    ApiKey = OneKey[1]
    SUPABASE_URL = OneKey[2]
    UserUuid = OneKey[3]
    BackendUrl = OneKey[4]
    BackendApiKey = OneKey[5]
    SUPABASE_KEY = OneKey[6]
    # GRADIO_ALLOWED_HOSTNAMES = OneKey[7]
    # os.environ["GRADIO_ALLOWED_HOSTNAMES"] = GRADIO_ALLOWED_HOSTNAMES
except Exception as e:
    print(f"OneKey: {e}")
    # exit(1)


# 创建Supabase客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 任务状态枚举
class TaskStatus:
    Created = "created"
    Processing = "processing"
    TextRewrited = "text_rewrited"
    TextFormated = "text_formated"
    VoiceCompleted = "voice_completed"
    VoiceError = "voice_error"
    VideoCompleted = "video_completed"
    VideoPublished = "video_published"
    VideoError = "video_error"
    Completed = "completed"
    Failed = "failed"
    Cancelled = "cancelled"
    NoCredits = "no_credits"

# 视频模板枚举
class VideoTemplate:
    Outdoor = "outdoor"
    UsFlag = "us-flag"
    WhiteHouse = "white-house"

def create_task_v3(task_type, text, word_num, is_rewrite):
    import json
    is_rewrite = False
    url = f"{BackendUrl}/trump_process_ctx_api_v2"
    headers = {
        "Content-Type": "application/json"
    }
    print(url)
    data = {
        "video_template": "",
        "speaker_template": "https://www.trumpaivoice.net/SelfitAssert/Heygem/Trump/trump_shot01.MP3",
        "text": text,
        "word_num": word_num,
        "is_rewrite": False,
        "watermark": True,
        "type": "voice",
        "cost_credits": 2,
        "user_uuid": UserUuid,
        "secret_key": "219ngu"
    }
    try:
        resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
        if not resp.ok:
            print(f"调用trump_process_ctx_api失败: {resp.status_code} {resp.text}")
            return None
        try:
            ctx_json = resp.json()
        except Exception as e:
            print(f"解析trump_process_ctx_api返回异常: {e}")
            return None
        if not ctx_json or ctx_json.get("code") != 0 or not ctx_json.get("data") or not ctx_json["data"].get("task_id"):
            print(f"trump_process_ctx_api返回异常: {ctx_json}")
            return None
        return {
            "task_id": ctx_json["data"]["task_id"],
            "uuid": ctx_json["data"]["task_uuid"],
            "status": "created",
            "message": "任务创建成功，后台处理中"
        }
    except Exception as err:
        print(f"create_task_v3异常: {err}")
        return None

def get_task_result(task_id):
    # Poll for task status and result
    url = f"{TrumpAiUrl}/api/task-status/uuid/{task_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ApiKey}"
    }
    print(url)
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result
    except Exception as e:
        return {}


if __name__ == "__main__":

    task_type = "voice"
    text = "Hello, this is a test message for Trump AI Voice."
    word_num = 10
    is_rewrite = True
    task_result = create_task_v2(task_type, text, word_num, is_rewrite)
    print(f"task_result: {task_result}")
