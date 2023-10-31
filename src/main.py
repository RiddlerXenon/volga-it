
from db import create_tables, fill_tables, drop_tables
from app import app
import uvicorn


drop_tables()
create_tables()
fill_tables()


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, workers=4, reload=True)
