from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from models import Base, Lead
from twilio.rest import Client

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

    # return {"message": "✅ Dziękujemy! Zgłoszenie zostało zapisane."}

    # 📲 WhatsApp powiadomienie
    try:
        account_sid = "ACd1a54d3c7490ca7c956dedf7b347e593"
        auth_token = "2b0dc350de029bd197acc424ff39e149"
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_="whatsapp:+14155238886",   # numer WhatsApp Twilio
            to="whatsapp:+48517431258",      # Twój numer
            # body=f"🚛 Nowe zgłoszenie od {data.name}\nTel: {data.phone}\nNIP: {data.nip}\nDMC: {data.dmc}"
                body=(
                    "🚛 *Nowe zgłoszenie z formularza*\n\n"
                    f"👤 Imię i nazwisko: {data.name}\n"
                    f"🏢 NIP: {data.nip}\n"
                    f"📞 Telefon: {data.phone}\n"
                    f"⚖️ DMC: {data.dmc}\n"
                    f"📏 Wymiary: {data.wymiary}\n"
                    f"🔼 Winda: {data.winda}\n"
                    f"📅 Data startu: {data.start_date}\n"
                    f"🌍 Kody startu: {data.kody_startu}\n"
                    f"🚚 Typ zabudowy: {data.zabudowa}\n\n"
                    "──────────────────────\n"
                    "💡 Truck24 – nowe zgłoszenie"
                )
        )

        print(f"✅ WhatsApp wysłany: {message.sid}")
    except Exception as e:
        print("❌ Błąd przy wysyłce WhatsApp:", e)

    # return {"message": "✅ Zgłoszenie zapisane i wysłane na WhatsApp."}
    return {"message": "✅ Dziękujemy! Zgłoszenie zostało zapisane."}

# 🧾 Podgląd wszystkich zgłoszeń (np. do panelu lub eksportu)
@app.get("/leads")
def get_all_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return leads
