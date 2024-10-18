import requests

# Label Studio 설정
LABEL_STUDIO_URL = 'http://localhost:8081'
API_TOKEN = '84809a8eede0a82b2e6d0ff439f9a9f6703afffe'  # 발급받은 Access Token
PROJECT_ID = '13'  # 프로젝트 ID를 여기에 입력

# 예측 요청 함수
def retrieve_predictions(task_ids, project_id):
    url = f'{LABEL_STUDIO_URL}/api/projects/{project_id}/tasks/predictions/'
    headers = {
        'Authorization': f'Token {API_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'task_ids': task_ids,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Predictions retrieved successfully")
    else:
        print(f"Failed to retrieve predictions: {response.content}")

# 예측할 작업 ID 목록 설정
task_ids = [1699]  # 예측할 작업 ID를 여기에 입력

# 예측 요청 실행
retrieve_predictions(task_ids, PROJECT_ID)