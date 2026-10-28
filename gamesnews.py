import requests
import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect(r"news.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT
)
""")
conn.commit()

rss_url = "https://www.igromania.ru/rss/news.xml"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

response = requests.get(rss_url, headers=headers)

if response.status_code == 200:
    root = ET.fromstring(response.content)

    for item in root.findall('.//item'):
        title = item.find('title').text.strip()
        
        href = item.find('guid').text.strip()
        
        cursor.execute("SELECT id FROM articles WHERE url = ?", (href,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute("INSERT INTO articles (url, title) VALUES (?, ?)", (href, title))
            conn.commit() 
            
            print(f"⚡ ИГРОМАНИЯ: {title}")
            print(f"🔗 {href}")
            print("-" * 40)
else:
    print(f"Не удалось загрузить Игроманию: {response.status_code}")

cursor.close()
conn.close()
