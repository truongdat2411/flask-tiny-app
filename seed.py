import sqlite3
from datetime import datetime

def adapt_datetime(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def convert_datetime(s):
    return datetime.strptime(s.decode('utf-8'), '%Y-%m-%d %H:%M:%S')

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter('DATETIME', convert_datetime)

def insert_sample_posts():
    conn = sqlite3.connect('instance/flaskr.sqlite')  # Đường dẫn đến database của bạn
    cursor = conn.cursor()
    users = [('user1', 2), ('user2', 3)]  # (username, id)
    for i in range(20):  # Tạo 20 bài viết
        user_id = users[i % 2][1]  # Luân phiên giữa user1 và user2
        title = f'Post {i+1}'
        body = f'Body content for post {i+1}'
        created = datetime.now()
        cursor.execute(
            'INSERT INTO post (title, body, author_id, created) VALUES (?, ?, ?, ?)',
            (title, body, user_id, created)
        )
    conn.commit()
    conn.close()

if __name__ == '__main__':
    insert_sample_posts()