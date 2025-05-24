# scraping_to_speech/utils/scraper.py

import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DOWNLOAD_DIR = "audio_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def dividir_em_partes(prompt, limite=999):
    paragrafos = prompt.split("\n")
    partes, atual = [], ""
    for p in paragrafos:
        if len(atual) + len(p) + 1 <= limite:
            atual += p + "\n"
        else:
            partes.append(atual.strip())
            atual = p + "\n"
    if atual:
        partes.append(atual.strip())
    return partes

def iniciar_driver():
    chrome_options = Options()
    prefs = {"download.default_directory": os.path.abspath(DOWNLOAD_DIR)}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def gerar_audio_partes(prompt, instructions, voice):
    partes = dividir_em_partes(prompt)
    arquivos = []
    for i, parte in enumerate(partes):
        print(f"[INFO] Gerando parte {i+1}/{len(partes)}...")
        arquivo = gerar_audio_uma_parte(parte, instructions, voice, i + 1)
        if arquivo:
            arquivos.append(arquivo)
    return arquivos

def gerar_audio_uma_parte(prompt, instructions, voice, numero):
    driver = iniciar_driver()
    driver.get("https://www.openai.fm/")

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "prompt"))
        )

        driver.find_element(By.ID, "prompt").clear()
        driver.find_element(By.ID, "prompt").send_keys(prompt)

        driver.find_element(By.ID, "input").clear()
        driver.find_element(By.ID, "input").send_keys(instructions)

        # Espera os botões de voz carregarem
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@role='button']//span"))
        )

        # Busca a voz correta
        voice_buttons = driver.find_elements(By.XPATH, "//div[@role='button']//span")
        voice_found = False

        for span in voice_buttons:
            if span.text.strip().lower() == voice.strip().lower():
                button = span.find_element(By.XPATH, "./ancestor::div[@role='button']")
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.5)
                button.click()
                voice_found = True
                break

        if not voice_found:
            print(f"[ERRO] Voz '{voice}' não encontrada na interface.")
            driver.quit()
            return None

        # Clicar no botão de download
        download_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and .//text()='Download']"))
        )
        arquivos_antes = set(os.listdir(DOWNLOAD_DIR))
        download_button.click()

        time.sleep(5)
        WebDriverWait(driver, 60).until(lambda d: len(set(os.listdir(DOWNLOAD_DIR)) - arquivos_antes) > 0)
        novos = list(set(os.listdir(DOWNLOAD_DIR)) - arquivos_antes)
        driver.quit()

        for f in novos:
            if f.endswith(".wav"):
                novo_nome = os.path.join(DOWNLOAD_DIR, f"audio{numero}.wav")
                os.rename(os.path.join(DOWNLOAD_DIR, f), novo_nome)
                return novo_nome

    except Exception as e:
        import traceback
        print("[ERRO] Falha ao gerar áudio:")
        traceback.print_exc()
        driver.quit()
        return None


def limpar_audios():
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
