import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import threading
from datetime import datetime

# Flag para detener el proceso
detener_proceso = False

# Función para escribir en el archivo de log con fecha y hora
def escribir_log(mensaje):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('conversion_log.txt', 'a') as log_file:
        log_file.write(f"{timestamp} - {mensaje}\n")

# Función para convertir archivos FLAC a MP3
def convertir_flac_a_mp3(input_flac, output_mp3, bitrate='320k'):
    comando = ['ffmpeg', '-i', input_flac, '-ab', bitrate, output_mp3]

    # Imprimir el comando para depuración
    print("Ejecutando comando:", comando)

    try:
        # Ejecutar el comando
        subprocess.run(comando, check=True)
        mensaje = f"Conversión completada: {output_mp3}"
        escribir_log(mensaje)  # Escribir en el log
        return True
    except subprocess.CalledProcessError as e:
        mensaje = f"No se pudo convertir el archivo: {input_flac}. Error: {e}"
        escribir_log(mensaje)  # Escribir en el log
        return False

# Función para seleccionar la carpeta de origen
def seleccionar_carpeta_origen():
    carpeta = filedialog.askdirectory()
    if carpeta:
        entrada.set(carpeta)
        buscar_archivos_flac(carpeta)

# Función para buscar archivos FLAC en la carpeta de origen
def buscar_archivos_flac(carpeta):
    archivos_flac = [f for f in os.listdir(carpeta) if f.endswith('.flac')]
    # Usar rutas completas
    archivos_flac_completos = [os.path.join(carpeta, f) for f in archivos_flac]
    entrada.set('\n'.join(archivos_flac_completos))

# Función para seleccionar la carpeta de salida
def seleccionar_carpeta_salida():
    carpeta = filedialog.askdirectory()
    salida.set(carpeta)

# Función para convertir todos los archivos seleccionados
def iniciar_conversion():
    global detener_proceso
    detener_proceso = False

    archivos_flac = entrada.get().split('\n')  # Obtiene la lista de archivos seleccionados
    carpeta_salida = salida.get()

    if not archivos_flac or not carpeta_salida:
        messagebox.showerror("Error", "Debes seleccionar una carpeta de origen y una carpeta de salida.")
        return

    exitos = []
    fallos = []

    # Configurar la barra de progreso
    progreso['maximum'] = len(archivos_flac)
    progreso['value'] = 0

    for archivo in archivos_flac:
        if detener_proceso:
            break

        if os.path.exists(archivo):
            nombre_salida = os.path.splitext(os.path.basename(archivo))[0] + '.mp3'
            ruta_salida = os.path.join(carpeta_salida, nombre_salida)

            # Mostrar el nombre del archivo en proceso
            archivo_actual.set(f"Convirtiendo: {os.path.basename(archivo)}")

            # Imprimir para depuración
            print(f"Convirtiendo: {archivo} a {ruta_salida}")
            if convertir_flac_a_mp3(archivo, ruta_salida):
                exitos.append(ruta_salida)
            else:
                fallos.append(archivo)
        else:
            mensaje = f"El archivo no existe: {archivo}"
            escribir_log(mensaje)  # Escribir en el log
            fallos.append(archivo)

        # Actualizar la barra de progreso
        progreso['value'] += 1
        root.update_idletasks()

    # Reiniciar la barra de progreso y el nombre del archivo actual
    progreso['value'] = 0
    archivo_actual.set("")

    # Mostrar resumen al final
    mensaje_resumen = f"Conversión completada.\n\nÉxitos:\n" + "\n".join(exitos) + "\n\nFallos:\n" + "\n".join(fallos)
    messagebox.showinfo("Resumen de Conversión", mensaje_resumen)

# Función para iniciar la conversión en un hilo separado
def iniciar_conversion_thread():
    thread = threading.Thread(target=iniciar_conversion)
    thread.start()

# Función para detener el proceso
def detener_conversion():
    global detener_proceso
    detener_proceso = True

# Configuración de la ventana principal de Tkinter
root = tk.Tk()
root.title("Convertidor FLAC a MP3")
root.minsize(700, 800)

# Variables para almacenar la selección del usuario
entrada = tk.StringVar()
salida = tk.StringVar()
archivo_actual = tk.StringVar()

# Botón para seleccionar la carpeta de origen
btn_seleccionar_origen = tk.Button(root, text="Seleccionar Carpeta de Origen", command=seleccionar_carpeta_origen)
btn_seleccionar_origen.pack(pady=10)

# Etiqueta para mostrar la ruta de los archivos FLAC encontrados
lbl_archivos = tk.Label(root, textvariable=entrada, wraplength=600, anchor='w', justify='left')
lbl_archivos.pack(pady=10)

# Botón para seleccionar la carpeta de salida
btn_seleccionar_salida = tk.Button(root, text="Seleccionar Carpeta de Salida", command=seleccionar_carpeta_salida)
btn_seleccionar_salida.pack(pady=10)

# Etiqueta para mostrar la ruta de la carpeta de salida
lbl_salida = tk.Label(root, textvariable=salida)
lbl_salida.pack(pady=10)

# Barra de progreso
progreso = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
progreso.pack(pady=20)

# Etiqueta para mostrar el archivo actual en proceso
lbl_archivo_actual = tk.Label(root, textvariable=archivo_actual)
lbl_archivo_actual.pack(pady=10)

# Botón para iniciar la conversión
btn_convertir = tk.Button(root, text="Convertir Archivos", command=iniciar_conversion_thread)
btn_convertir.pack(pady=20)

# Botón para detener la conversión
btn_detener = tk.Button(root, text="Detener Conversión", command=detener_conversion)
btn_detener.pack(pady=10)

# Ejecutamos el bucle principal de Tkinter
root.mainloop()
