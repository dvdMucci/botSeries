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

def get_latest_episodes():
    """Obtiene la lista de episodios más recientes de la página web."""
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Modifica esto según la estructura de la página
    episodes = []
    for episode_element in soup.find_all('a', class_='title'):  # Ejemplo de búsqueda
        episodes.append(episode_element.text.strip())
    return episodes

def send_telegram_notification(message):
    """Envía una notificación por Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"Notificación enviada: {message}")
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

def notify_existing_episodes():
    """Notifica los episodios que actualmente figuran en la página al iniciar el script."""
    print("Enviando episodios existentes...")
    try:
        episodes = get_latest_episodes()
        if episodes:
            message = "Episodios actuales disponibles:\n" + "\n".join(episodes)
            send_telegram_notification(message)
        else:
            print("No se encontraron episodios en la página.")
    except Exception as e:
        print(f"Error al notificar episodios existentes: {e}")

def main():
    """Función principal del script."""
    notify_existing_episodes()  # Notificar episodios existentes al iniciar

    last_episode = load_last_episode()

    while True:
        print("Comprobando nuevos episodios...")
        try:
            latest_episodes = get_latest_episodes()
            if latest_episodes and latest_episodes[0] != last_episode:
                print(f"Nuevo episodio encontrado: {latest_episodes[0]}")
                send_telegram_notification(f"Nuevo capítulo disponible: {latest_episodes[0]}\nPuedes verlo aquí: {URL}")
                save_last_episode(latest_episodes[0])
                last_episode = latest_episodes[0]
            else:
                print("No hay nuevos episodios.")
        except Exception as e:
            print(f"Error al comprobar episodios: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
