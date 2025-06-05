import re
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox
import docx
import PyPDF2
import mysql.connector

def es_fecha(texto):
    patrones = [
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{2}-\d{2}-\d{4}\b"
    ]
    return any(re.search(p, texto) for p in patrones)

def leer_txt(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return f.readlines()

def leer_docx(ruta):
    doc = docx.Document(ruta)
    return [p.text for p in doc.paragraphs if p.text.strip()]

def leer_pdf(ruta):
    texto = []
    with open(ruta, "rb") as f:
        lector = PyPDF2.PdfReader(f)
        for page in lector.pages:
            texto.append(page.extract_text())
    return "\n".join(texto).splitlines()

def conectar_mysql():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="inacap2023" #Asegurate de cambiar la contraseña cada vez
    )
    cursor = conexion.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS datalake")
    cursor.execute("USE datalake")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datos_malos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ciudad VARCHAR(255)
        )
    """)
    return conexion, cursor

def guardar_error(cursor, ciudad):
    cursor.execute("INSERT INTO datos_malos (ciudad) VALUES (%s)", (ciudad,))

def analizar(lineas):
    solo_mayusculas = 0
    mal_escritos = 0
    con_numeros = 0
    con_fechas = 0
    nombres = []
    errores_registrados = []

    conexion, cursor = conectar_mysql()

    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue

        match = re.match(r"^\d+\.\s*(.+)", linea)
        if match:
            contenido = match.group(1)
        else:
            contenido = linea

        partes = contenido.split()
        if not partes:
            continue

        nombre_ciudad = " ".join(partes[:-1]) if es_fecha(partes[-1]) else " ".join(partes)
        nombres.append(nombre_ciudad)

        if nombre_ciudad.isupper():
            solo_mayusculas += 1
            errores_registrados.append(nombre_ciudad)
        elif nombre_ciudad != nombre_ciudad.title():
            mal_escritos += 1
            errores_registrados.append(nombre_ciudad)

        if len(partes) > 1 and partes[1].isdigit():
            con_numeros += 1
            errores_registrados.append(contenido)

        if len(partes) >= 2 and es_fecha(partes[-1]):
            con_fechas += 1
            errores_registrados.append(contenido)

    nombres_normalizados = [n.lower().strip() for n in nombres]
    conteo = Counter(nombres_normalizados)
    repetidos = [nombre for nombre, cantidad in conteo.items() if cantidad > 1]

    for nombre in repetidos:
        for original in nombres:
            if original.lower().strip() == nombre:
                errores_registrados.append(original)

    for ciudad in errores_registrados:
        guardar_error(cursor, ciudad)

    conexion.commit()
    cursor.close()
    conexion.close()

    resumen = (
        f"🔠 Se detectaron {solo_mayusculas} datos totalmente en mayúsculas.\n"
        f"⚠️ Se detectaron {mal_escritos} datos mal capitalizados (mal escritos).\n"
        f"🔢 Se detectaron {con_numeros} datos que tienen un número después del nombre.\n"
        f"📅 Se detectaron {con_fechas} datos que terminan en una fecha.\n"
        f"♻️ Se detectaron {len(repetidos)} nombres repetidos (sin importar mayúsculas/minúsculas)."
    )

    return resumen

def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[
        ("Archivos de texto", "*.txt"),
        ("Archivos de Word", "*.docx"),
        ("Archivos PDF", "*.pdf")
    ])
    return archivo

def ejecutar_analisis():
    ruta = seleccionar_archivo()
    if not ruta:
        return

    if ruta.endswith(".txt"):
        lineas = leer_txt(ruta)
    elif ruta.endswith(".docx"):
        lineas = leer_docx(ruta)
    elif ruta.endswith(".pdf"):
        lineas = leer_pdf(ruta)
    else:
        messagebox.showerror("Error", "Formato de archivo no compatible.")
        return

    resultado = analizar(lineas)
    messagebox.showinfo("Resultados del análisis", resultado)

def main():
    ventana = tk.Tk()
    ventana.title("Analizador de Datos")
    ventana.geometry("400x250")
    ventana.configure(bg="#f0f2f5")
    ventana.resizable(False, False)

    titulo = tk.Label(ventana, text="Analizador de Archivos", font=("Segoe UI", 16, "bold"), bg="#f0f2f5")
    titulo.pack(pady=(30, 10))

    subtitulo = tk.Label(ventana, text="Selecciona un archivo (.txt, .docx o .pdf)", font=("Segoe UI", 11), bg="#f0f2f5")
    subtitulo.pack(pady=(0, 20))

    boton = tk.Button(
        ventana, text="Seleccionar archivo", font=("Segoe UI", 10, "bold"),
        bg="#0078D7", fg="white", activebackground="#005A9E", activeforeground="white",
        relief="flat", padx=10, pady=6, command=ejecutar_analisis
    )
    boton.pack()

    footer = tk.Label(ventana, text="v3.2", font=("Segoe UI", 8), bg="#f0f2f5", fg="gray")
    footer.pack(side="bottom", pady=10)

    ventana.mainloop()

if __name__ == "__main__":
    main()
