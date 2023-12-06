from flask import Flask, request, render_template
import mysql.connector
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, mm
from datetime import datetime
import os
import win32print
import win32api

app = Flask(__name__)

def conectar_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_estudiantes"
    )

def obtener_informacion_usuario(id_usuario):
    mydb = conectar_mysql()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id, name, email, consultas FROM informacion WHERE rut = %s OR id = %s", (id_usuario, id_usuario))
    resultado = mycursor.fetchone()
    mycursor.execute("UPDATE informacion SET consultas = consultas + 1 WHERE rut = %s OR id = %s", (id_usuario, id_usuario))
    mydb.commit()

    mydb.close()
    return resultado

def imprimir_pdf(pdf_filename):
    try:
        printer_name = win32print.GetDefaultPrinter() #"TxPOS80" 
        win32print.SetDefaultPrinter(printer_name)
        win32api.ShellExecute(0, "print", pdf_filename, '/d:"%s"' % printer_name, ".", 0)
    except Exception as e:
        print(f"Error al imprimir: {e}")

def eliminar_archivo(pdf_filename):
    os.remove(pdf_filename)

def imprimir_informe(texto):
    try:
        printer_name = "TxPOS80"
        win32print.SetDefaultPrinter(printer_name)
        win32api.ShellExecute(0,"print",texto,'/d:"%s"'%printer_name,".",0)
    except Exception as e:
        print(f"Error al imprimir: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pagina_atrasos')
def pagina_atrasos():
    return render_template('pases.html')

@app.route('/pagina_certificado')
def pagina_certificado():
    return render_template('certificado.html')

@app.route('/generar_informe', methods=['POST'])
def generar_informe():
    id_usuario = request.form['id_lci']
    resultado = obtener_informacion_usuario(id_usuario)
    imprimir_informe(f"aca debe ir un pase de atraso")
    return "El informe se generó con éxito y se imprimió."

@app.route('/generar_certificado', methods=['POST'])
def generar_certificado():
    id_usuario = request.form['id_lci']
    resultado = obtener_informacion_usuario(id_usuario)
    pdf_filename = f"certificado_{str(resultado[0])}.pdf"
    pdf = canvas.Canvas(pdf_filename, pagesize=letter)
    pdf.setLineWidth(.3)
    pdf.setFont('Helvetica', 12)
    pdf.drawString(100, 800, "Rut: " + str(resultado[0]))
    pdf.drawString(100, 750, "Nombre: " + str(resultado[1]))
    pdf.drawString(100, 700, "Email: " + resultado[2])
    pdf.drawString(100, 650, "Fecha y hora de consulta: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    pdf.save()
    imprimir_pdf(pdf_filename)
    eliminar_archivo(pdf_filename)
    return "El certificado se generó con éxito y se imprimió."

if __name__ == '__main__':
    app.run(debug=True)
