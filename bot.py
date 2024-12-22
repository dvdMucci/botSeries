import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la URL y notificación
URL = "https://solotorrent.org/series/silo/"
CHECK_INTERVAL = 3600  # Tiempo entre comprobaciones en segundos (1 hora)
LATEST_EPISODE_FILE = "latest_episode.txt"

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_latest_episode():
    """Obtiene el episodio más reciente de la página web."""
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Modifica esto según la estructura de la página
    episode_element = soup.find('a', class_='title')  # Ejemplo de búsqueda
    if episode_element:
        return episode_element.text.strip()
    return None

def send_telegram_notification(episode):
    """Envía una notificación por Telegram."""
    message = f"Nuevo capítulo disponible: {episode}\nPuedes verlo aquí: {URL}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"Notificación enviada: {episode}")
    else:
        print(f"Error al enviar notificación: {response.text}")

def load_last_episode():
    """Carga el último episodio registrado."""
    try:
        with open(LATEST_EPISODE_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def save_last_episode(episode):
    """Guarda el último episodio registrado."""
    with open(LATEST_EPISODE_FILE, "w") as file:
        file.write(episode)

def main():
    """Función principal del script."""
    last_episode = load_last_episode()

    while True:
        print("Comprobando nuevos episodios...")
        try:
            latest_episode = get_latest_episode()
            if latest_episode and latest_episode != last_episode:
                print(f"Nuevo episodio encontrado: {latest_episode}")
                send_telegram_notification(latest_episode)
                save_last_episode(latest_episode)
                last_episode = latest_episode
            else:
                print("No hay nuevos episodios.")
        except Exception as e:
            print(f"Error al comprobar episodios: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
