from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from models import Base, Lead

# 🔸 Inicjalizacja bazy danych
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 🔓 CORS — żeby formularz działał nawet z innej domeny
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 Udostępnienie folderu static/
app.mount("/static", StaticFiles(directory="static"), name="static")

# 📄 Endpoint na stronę główną (formularz)
@app.get("/")
def serve_form():
    return FileResponse("static/formularz.html")

# 🧰 Sesja DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📩 Model danych z formularza
class FormData(BaseModel):
    name: str
    nip: str
    phone: str
    dmc: str
    wymiary: str
    winda: str
    start_date: str
    kody_startu: str
    zabudowa: str

# 📨 Zapis danych do bazy
@app.post("/submit")
async def submit_form(data: FormData, db: Session = Depends(get_db)):
    lead = Lead(
        name=data.name,
        nip=data.nip,
        phone=data.phone,
        dmc=data.dmc,
        wymiary=data.wymiary,
        winda=data.winda,
        start_date=data.start_date,
        kody_startu=data.kody_startu,
        zabudowa=data.zabudowa
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    return {"message": "✅ Dziękujemy! Zgłoszenie zostało zapisane."}

# 🧾 Podgląd wszystkich zgłoszeń (np. do panelu lub eksportu)
@app.get("/leads")
def get_all_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return leads
