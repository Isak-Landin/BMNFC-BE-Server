# Taggsystem (Deprecated) - Replaced with newer software - Completely refactored 

Ett säkert och smidigt system för att använda **NFC-taggar** som in- och utloggning.  
Systemet är utvecklat för att i realtid visa vilka personer som befinner sig i byggnaden, med särskilt fokus på säkerhet vid exempelvis brand eller evakuering.

---

## 🛠 Funktioner

- NFC-tag scanning för **in- och utloggning** vid entré
- Webbaserad översikt av **aktuellt inloggade användare**
- Möjlighet att **exportera närvarolistan** som CSV vid utrymning
- Automatisk **nollställning vid midnatt** (ny arbetsdag)
- Flaggar användare som fortfarande är inloggade vid purge (säkerhetskontroll)
- Responsiv design anpassad för skärmar vid entréer
- Enkel och säker drift via **Docker Compose**
- **Persistenta databaser** så historik inte går förlorad vid serveromstart

---

## 🔒 Syfte

Systemet används för att:

- Snabbt identifiera vilka som är närvarande vid **brand eller nödsituation**
- Kunna överlämna aktuell närvarolista till **räddningstjänst**
- Underlätta in-/utpasseringskontroll utan manuella listor

---

## 📦 Teknologi

- **Python** (Flask Web Framework)
- **Docker** & **Docker Compose** (kontainrar och drift)
- **PostgreSQL** (säker databaslagring)
- **HTML/CSS/JavaScript** (frontend)

---

# (Optional) Needed to initialize database in volume in unknown amount of environments
```bash
docker exec -it baramineraler-db psql -U baramineraler_admin -d baramineraler_tagsystem -h localhost

python
```

```python
from app import app, db

with app.app_context():
    db.create_all()

```


## 📦 Package and Module Setup for NFC Project

### 🔹 Host System Requirements

#### Install PC/SC daemon to enable smartcard/NFC readers
```bash
sudo apt update
sudo apt install -y pcscd
```
#### Start the PC/SC daemon
```bash
sudo systemctl enable pcscd
sudo systemctl start pcscd
```

#### Ensure the NFC kernel module (pn533_usb) does not auto-load and block access (Kill this mf with fire)
```bash
echo "blacklist pn533_usb" | sudo tee /etc/modprobe.d/blacklist-pn533.conf
sudo update-initramfs -u
```

#### (Optional) To manually unload the pn533_usb module if already loaded
```bash
sudo modprobe -r pn533_usb
```

#### Verify pcscd is running and ready to provide /run/pcscd/pcscd.comm
```bash
sudo systemctl status pcscd
```

### 🔹 Docker Container Setup (Informational since it is native to the Dockerfile and docker-compose.yml)

#### Base system requirements for building and running the NFC stack
```
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        gcc \
        libusb-1.0-0-dev \
        libudev-dev \
        libpcsclite-dev \
        libpcsclite1 && \
    rm -rf /var/lib/apt/lists/*
```

#### Python dependencies for NFC backend and PC/SC access
```
libusb1==3.3.1
ndeflib==0.3.3
nfcpy==1.0.4
pyDes==2.0.1
pyscard==2.2.2
pyserial==3.5
six==1.17.0
requests==2.31.0
```
#### Docker must mount the host's USB devices and the pcscd socket (docker-compose.yml or docker run)
```
volumes:
  - /dev/bus/usb:/dev/bus/usb
  - /run/pcscd/pcscd.comm:/run/pcscd/pcscd.comm
```

#### Optional: set environment variable to point to the pcscd socket
```
environment:
  - PCSC_SOCKET=/run/pcscd/pcscd.comm
```

## Licence
GPL 3
IOW - Fuck it. It's here, is it not.

## License (Deprecated)

This project is proprietary software...