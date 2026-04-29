import sqlite3
import os
import pandas as pd

# Définition du chemin de la base de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'assurance_cameroun.db')

def get_connection():
    """Établit la connexion avec SQLite."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_table():
    """Crée la table principale avec toutes les variables d'étude (Version Enrichie)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collectes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_soumission DATETIME DEFAULT CURRENT_TIMESTAMP,
            -- Section 1: Profil
            sexe TEXT,
            age_tranche TEXT,
            ville TEXT,
            region TEXT,
            profession TEXT,
            secteur_activite TEXT,
            revenu_mensuel TEXT,
            -- Section 2: Culture & Perception
            perception_assurance TEXT,
            connaissance_assurance TEXT,
            culture_cima TEXT,
            niveau_confiance INTEGER,
            barriere_principale TEXT,
            -- Section 3: Habitudes
            possession_assurance TEXT, -- Liste des types possédés
            canal_souscription TEXT,
            experience_sinistre TEXT,
            critere_choix TEXT,
            -- Section 4: Futur & Digital
            pret_pour_insurtech TEXT,
            risque_majeur_raint TEXT,
            besoin_prioritaire TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Base de données synchronisée (Structure XL).")

def save_entry(data_dict):
    """Enregistre les données du formulaire."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        columns = ', '.join(data_dict.keys())
        placeholders = ':' + ', :'.join(data_dict.keys())
        query = f"INSERT INTO collectes ({columns}) VALUES ({placeholders})"
        cursor.execute(query, data_dict)
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")
    finally:
        conn.close()

def get_all_data():
    """Récupère toutes les données pour les analyses et KPIs."""
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM collectes", conn)
    except Exception as e:
        print(f"Erreur de lecture : {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df