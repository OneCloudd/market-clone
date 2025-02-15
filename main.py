from fastapi import FastAPI, UploadFile, Form, Response
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import sqlite3
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()

cur.execute(f"""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                image BLOB,
                price INTEGER NOT NULL,
                description TEXT,
                place TEXT NOT NULL,
                insertAt INTEGER NOT NULL
            );
            """)

app = FastAPI()

@app.post('/items')
async def create_item(image:UploadFile,
                title:Annotated[str, Form()],
                price:Annotated[int, Form()],
                description:Annotated[str, Form()],
                place:Annotated[str, Form()],
                insertAt:Annotated[int, Form()]
                ):
    
    # 이미지는 파일이 커서 읽는데 시간을 주기위해 await를 씀
    image_bytes = await image.read()
    cur.execute(f"""
                INSERT INTO items(title, image, price, description, place, insertAt)
                VALUES ('{title}', '{image_bytes.hex()}', {price}, '{description}', '{place}', '{insertAt}')
                """)
    con.commit()
    return '200'
    
@app.get('/items')
async def get_items():
    # 컬럼명도 같이 가져옴  ex) [[ id:1], [title:'제목']]
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(f"""
                       SELECT * FROM items;
                       """).fetchall()
    
    return JSONResponse(jsonable_encoder(dict(row) for row in rows))
    
@app.get("/images/{item_id}")
async def get_image(item_id):
    cur = con.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id={item_id}
                              """).fetchone()[0]
    
    return Response(content=bytes.fromhex(image_bytes))

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
