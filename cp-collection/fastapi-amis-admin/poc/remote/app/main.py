from fastapi import FastAPI
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
import uvicorn

class Base(DeclarativeBase):
  pass

class Item(Base):
  __tablename__ = "items"
  id = Column(Integer, primary_key=True)
  name = Column(String(100), default="test")

app = FastAPI()
site = AdminSite(settings=Settings(database_url_async="sqlite+aiosqlite:///test.db"))
site.mount_app(app)

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)
