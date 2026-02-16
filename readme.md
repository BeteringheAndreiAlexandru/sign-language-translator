Cerințe Sistem 

-Hardware 

Webcam sau cameră externă 

Calculator cu 4GB+ RAM (8GB recomandat) 

(Opțional) CPU pentru antrenare mai rapidă 

-Software 

Python 3.11 

Mediapipe 0.10.11 

opencv-python 4.9.0.80 

tensorflow 2.15.0 

scikit-learn 1.4.0 

numpy 1.24.3 

pandas 2.1.4 

matplotlib 3.8.2 

 

Instalare 

# Clonează repository-ul 

git clone https://github.com/utilizator/detector-limbaj-semne.git 

cd detector-limbaj-semne 

 

# Creaza mediul virtual 

py -3.11 -m venv detectvenv 

.\detectvenv\Scripts\activate 

 

# Instalează dependențele 

pip install -r requirements.txt 

Structură Proiect 

 

detector-limbaj-semne/ 

│ 

├── data_collection.py     # Colectează date pentru antrenare 

├── train_model.py    # Antrenează modelul 

├── detector.py           # Rulează detectarea în timp real 

│ 

├── date/                 # Datele colectate (se creează automat) 

│   ├── A/                # Mostre pentru litera A 

│   ├── B/                # Mostre pentru litera B 

│   ├── multumesc/        # Mostre pentru cuvânt 

│   └── ... 

│ 

└── model/                # Modelul antrenat (se creează automat) 

     

 

 

 Cum Să Folosești 

1. Colectare Date 

python data_collection.py 

Comenzi: 

A-Z - Înregistrează litera respectivă 

1 - "mulțumesc" 

2 - "mâncare" 

3 - "bomboană" 

4 - "da" 

5 - "nu" 

6 - "te rog" 

ESC - Ieșire 

 

2. Antrenare Model 

python train_model.py 

Rulează automat și salvează modelul în folderul model/ 

 

3. Detectare în Timp Real 

python detector.py 

Comenzi în timpul rulării: 

ESC – Ieșire 

 

Personalizare 

Adăugare Cuvinte Noi 

În data_collection.py, modifică lista cuvinte: 

cuvinte = ["multumesc", "mancare", "bomboana", "da", "nu", "te_rog", "cuvant_nou"] 

Schimbare Număr Mostre 

În data_collection.py: 

target_samples = 300  # implicit 200 

Ajustare Prag Încredere 

În detector.py: 

confidence_threshold = 0.7  # între 0 și 1	 



Folosire cu interfata: 

Se va deschide fisierul detector.py , unde se vor tasta comenzile
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python detector.py  #pentru a porni serverul prin websocket
Apoi deschide fisierul index.html in google , unde se va porni camera , si buton de recunoastere pentru a incepe 
traducerea limbajului semnelor
 

Licență 

Acest proiect este open-source și poate fi folosit gratuit pentru educație. 