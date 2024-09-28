# import os
from dotenv import load_dotenv
# import aiomysql
# from typing import Optional
import logging

# 환경 변수 로드 및 로깅 설정
load_dotenv()
logging.basicConfig(level=logging.INFO)

# # 환경 변수에서 MySQL 연결 정보 가져오기
# DB_HOST = os.getenv('DB_HOST')
# DB_PORT = os.getenv('DB_PORT')
# DB_USER = os.getenv('DB_USER')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_NAME = os.getenv('DB_NAME')

# if None in (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME):
#     raise ValueError(".env에 DB 환경변수 셋팅이 제대로 진행되지 않았습니다.")

class Database:
    # def __init__(self):
    #     self._pool: Optional[aiomysql.Pool] = None

    async def connect(self):
        logging.info("Connecting to MySQL database...")
        # self._pool = await aiomysql.create_pool(
        #     host=DB_HOST,
        #     port=int(DB_PORT),
        #     user=DB_USER,
        #     password=DB_PASSWORD,
        #     db=DB_NAME,
        #     autocommit=True,
        #     charset='utf8mb4'
        # )
        logging.info("DB 연결 완료")

    async def disconnect(self):
        # if self._pool:
        #     self._pool.close()
        #     await self._pool.wait_closed()
        logging.info("DB 연결 해제 완료")

    # async def execute_query(self, query: str, params: Optional[tuple] = None) -> int:
    #     if not self._pool:
    #         raise RuntimeError("Connection pool is not initialized.")

    #     async with self._pool.acquire() as conn:
    #         async with conn.cursor(aiomysql.DictCursor) as cursor:
    #             await cursor.execute(query, params)
    #             result = await cursor.fetchall() 
    #             return result

# Database 인스턴스 생성
database = Database()