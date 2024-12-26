from googleapiclient.discovery import build
from google.oauth2 import service_account

# 서비스 계정 키 파일 경로
SERVICE_ACCOUNT_FILE = "/YOUR/json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# 인증 및 서비스 생성
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=credentials)

# Google Sheets API 호출
SPREADSHEET_ID = "YOURID"  # 스프레드시트 ID
RANGE_SERVER = "Server_A!A1:Z10"  # Server 데이터 범위
RANGE_EXCEPTION = "Exception_A!A1:Z10"  # Exception 데이터 범위


def get_gpu_user_mappings():
    """
    Google Sheets 데이터를 기반으로 GPU 번호별 허가된 사용자와 예외 사용자 딕셔너리 생성
    """
    try:
        sheet = service.spreadsheets()

        # Server 데이터 가져오기
        result_server = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_SERVER).execute()
        values_server = result_server.get("values", [])

        # Exception 데이터 가져오기
        result_exception = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_EXCEPTION).execute()
        values_exception = result_exception.get("values", [])

        if not values_server or not values_exception:
            print("No data found in one or more sheets.")
            return {}, {}

        # Server 데이터 처리
        header_server = values_server[0][1:]  # 첫 번째 행에서 GPU 번호 추출 (열 1부터 끝까지)
        data_rows_server = values_server[1:]  # 데이터 행들

        gpu_user_mapping = {}
        for row in data_rows_server:
            for idx, user in enumerate(row[1:], start=1):  # 열 1부터 시작 (GPU 번호는 헤더에 매핑)
                if user:  # 값이 비어 있지 않은 경우에만 처리
                    gpu_number = int(header_server[idx - 1])  # 헤더에서 GPU 번호 가져오기
                    if gpu_number not in gpu_user_mapping:
                        gpu_user_mapping[gpu_number] = []
                    gpu_user_mapping[gpu_number].append(user)

        # Exception 데이터 처리
        header_exception = values_exception[0][1:]  # 첫 번째 행에서 GPU 번호 추출 (열 1부터 끝까지)
        data_rows_exception = values_exception[1:]  # 데이터 행들

        gpu_exception_mapping = {}
        for row in data_rows_exception:
            for idx, user in enumerate(row[1:], start=1):  # 열 1부터 시작 (GPU 번호는 헤더에 매핑)
                if user:  # 값이 비어 있지 않은 경우에만 처리
                    gpu_number = int(header_exception[idx - 1])  # 헤더에서 GPU 번호 가져오기
                    if gpu_number not in gpu_exception_mapping:
                        gpu_exception_mapping[gpu_number] = []
                    gpu_exception_mapping[gpu_number].append(user)

        return gpu_user_mapping, gpu_exception_mapping

    except Exception as e:
        print(f"Error: {e}")
        return {}, {}


    except Exception as e:
        print(f"Error: {e}")
        return {}
    
    return server_data