import os
import time

import psycopg2

postgres_config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}


class PostgresManager:
    def __init__(self, config: dict[str, str], is_autocommit: bool = True):
        self.config = config
        self.is_autocommit = is_autocommit
        self.conn = None
        self.cur = None

    def __enter__(self):
        # Проверка готовности PostgreSQL для подключения
        for i in range(10):
            try:
                self.conn = psycopg2.connect(**self.config)
                break
            except psycopg2.OperationalError:
                print("Postgres not ready yet, retrying...")
                time.sleep(2)
        else:
            raise RuntimeError("Could not connect to Postgres after 10 tries")
        self.conn.autocommit = self.is_autocommit
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def create_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            size INTEGER NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_type TEXT NOT NULL
        );""")
        self.cur.execute("commit;")
        print("Table created successfully")

    def add_file(self, filename: str, original_name: str, size: float, file_type: str):
        try:
            self.cur.execute(
                """
                INSERT INTO images (filename, original_name, size, file_type) VALUES (%s, %s, %s, %s);""",
                (filename, original_name, size, file_type)
            )
            print(f"Файл {original_name} добавлен")
        except Exception as e:
            print(e)

    def show_table(self) -> list[tuple] | None:
        self.cur.execute("""SELECT * FROM images;""")
        return self.cur.fetchall()

    def get_page_by_page_num(self, page_number: int) -> list[tuple] | None:
        # page_num -> 1 - 100000
        offset = (page_number - 1) * 10
        self.cur.execute("""SELECT * FROM images OFFSET %s LIMIT 10;""", (offset,))
        return self.cur.fetchall()

    def get_id_by_filename(self, filename: str) -> int | None:
        self.cur.execute("""SELECT id FROM images WHERE filename = %s;""", (filename,))
        result = self.cur.fetchone()
        if result:
            return result[0]

    def delete_by_id(self, id_image: int):
        try:
            self.cur.execute("""DELETE FROM images WHERE id = %s;""", (id_image,))
            print(f"Запись с id {id} успешно удалена!")
        except Exception as e:
            print(e)
