# 🎵 Discord Bot Música con youtube

[![Discord.js](https://img.shields.io/badge/discord.js-v14-blue.svg)](https://discord.js.org/)
[![Licencia](https://img.shields.io/badge/license-ISC-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue) 

Un bot de música para Discord, enfocado en ofrecer musical estable mediante **youtube**. Nace de la frustración con los bots masificados y los bloqueos de youtubr, permitiéndote hostear tu propio bot y olvidarte de las interrupciones.

> “Esta es la evolución del primer bot que hice que funcionase mediande **SoundCloud**, que honestamente y entre amigos, es una putisima mierda **SoundCloud**. Asi que para saltar el bloqueo de youtube he decidido hacer el bot en python en vez de JavaScript (lenguaje del anterior bot) ya que ofrece una biblioteca que facilita engañar a youtube haciendonos pasar por un usuario de la app desde un android o IOs” 

---

## ✨ Características Principales

*   **🎧 Reproducción de Música**: Reproducción de música en canales de voz con búsqueda de canciones en YouTube.
*   **💬 Soporte de enlaces**: Soporte para enlaces directos y soporte para playlists de YouTube.
*   **🕹️ Panel de Control Interactivo**: Controla la música con botones (⏮️ Anterior, ⏯️ Pausa/Reanudar, ⏭️ Siguiente, 🗑️ Limpiar cola) sin necesidad de escribir comandos.
*   **📜 Cola de Reproducción Paginada**: Visualiza la lista de canciones en espera con un sistema de páginas interactivo.
*   **🗑️ Gestión de Cola**: Elimina canciones específicas de la cola con un solo botón o comando.
*   **🔒 Sistema Anti-Crash**: Protección básica contra errores no manejados para mantener el bot en línea, y así no fastidiar la reproducción de muúica.
*   **⚙️ Fácil de Configurar**: Solo necesitas un token de Discord Bot y python para empezar.
*   **🔧 Código Abierto y Personalizable**: Haz un fork y adáptalo a tu gusto

---

## 📋 Requisitos Previos

- Python 3.10 o superior
- Un bot de Discord creado en el [Discord Developer Portal](https://discord.com/developers/applications)
- FFmpeg instalado y accesible desde la terminal
- Dependencias de Python:
  - `discord.py`
  - `yt-dlp`
  - `python-dotenv`
  - `PyNaCl`

> Si vas a usar el bot en voz, asegúrate de que Discord tenga permisos de conexión y habla en el servidor.

---

## 🚀 Instalación en local

### 1. Clona el repositorio

```bash
git clone https://github.com/Aremanky/discord-bot-musica.git
cd discord-bot-musica
```

### 2. Crea un entorno virtual

#### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instala dependencias

```bash
pip install --upgrade pip
pip install discord.py yt-dlp python-dotenv PyNaCl
```

### 4. Instala FFmpeg

#### Windows
Descarga FFmpeg, añádelo al PATH y comprueba que funciona con:

```bash
ffmpeg -version
```

#### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

### 5. Crea el archivo `.env`

En la raíz del proyecto crea un archivo llamado `.env` con este contenido:

```env
TOKEN=TU_TOKEN_DE_DISCORD
```

### 6. Activa los intents del bot

En el portal de desarrolladores de Discord, abre la aplicación del bot y activa:

- **Message Content Intent**

Esto es necesario porque el bot usa comandos con prefijo, como `.play`.

### 7. Ejecuta el bot

```bash
python bot.py
```

Si todo va bien, verás un mensaje parecido a:

```bash
Bot de Python encendido como: ...
```

---

## 🎮 Comandos y Uso

El bot usa el prefijo `.` (punto) por defecto pero en la linea 20 del `bot.py` verás `command_prefix = '.'`, cambialo a tu gusto. Todos los comandos deben escribirse en un canal de texto.

| Comando | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `.play <búsqueda>` | Busca y reproduce una canción en Youtube. | `.play linkin park` |
| `.cola` | Muestra la cola de reproducción actual con botones para navegar entre páginas. | `.cola` |
| `.fora <número>` | Elimina una canción específica de la cola según su número en la lista. | `.fora 3` |
| `.help` | Muestra un mensaje de ayuda con todos los comandos y sus funciones. | `.help` |

---

## 🕹️ Controles Interactivos del Reproductor

Cuando inicias una canción, el bot envía un mensaje con un panel de control visual que incluye:

*  ⏮️ (Anterior): Vuelve al inicio de la canción (si han pasado +10s) o a la canción anterior del historial.

*  ⏯️ (Pausa/Reanudar): Alterna entre pausar y reanudar la reproducción.

*  ⏭️ (Siguiente): Salta a la siguiente canción en la cola.

*  🗑️ (Limpiar): Vacía toda la cola de reproducción, excepto la canción que está sonando.

---

## ⚙️ Cómo funciona

- El bot usa `yt-dlp` para extraer información y audio desde YouTube.
- Reproduce el audio mediante `FFmpeg`.
- Mantiene una cola por servidor para que varios servidores puedan usarlo de forma independiente.
- Guarda historial y estado de reproducción para mejorar la experiencia.

---

## 🛠️ Problemas frecuentes

### El bot no se conecta al canal de voz
Comprueba que el bot tenga permisos de:
- Conectar
- Hablar
- Ver canal

### No reproduce audio
Revisa que:
- FFmpeg esté instalado correctamente.
- El token del bot sea válido.
- El bot tenga permisos en el canal.

### El comando `.play` no responde
Asegúrate de haber activado **Message Content Intent** en el portal de Discord.

---

## 📄 Licencia

Este proyecto está bajo licencia MIT. Consulta el archivo `LICENSE` para más información.

## 🤝 Contribuciones

Se aceptan mejoras, optimizaciones y nuevas funciones. Haz un fork, crea tu rama y abre un pull request.

---

Hecho para que cualquiera pueda levantarlo en local en pocos minutos.
