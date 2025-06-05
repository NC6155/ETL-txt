import mysql.connector
import unicodedata

class Limpieza_Datos():
    def __init__(self):
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="inacap2023" #Asegurate de cambiar la contraseña cada vez
        )
        self.cursor = self.conexion.cursor()

    def limpiar_datos(self):
        contador=1
        lista_ciudades={}
        ciudades_eliminadas=[]
        sql1="select ciudad from datos_malos;"
        try:
            self.cursor.execute(sql1)
            todas_las_ciudades=self.cursor.fetchall()
        except Exception as err:
            self.conexion.rollback()
            print(err)
        
        #Comenzamos a limpiar los datos
        while True:
            eleccion=input("¿Cómo desea que se vean sus datos?\n\
                        Su primera letra en mayúscula (C)\n\
                        Todo en mayúscula (U)\n\
                        Todo en minúscula (L)\n\
                        \t: ").upper()
            if eleccion=="C":
                for ciudad in todas_las_ciudades:
                    ciudad=str(ciudad).capitalize()

                    #Ahora quitamos todos los acentos, tildes, etc con unicode
                    ciudad_nfkc=unicodedata.normalize("NFKC",ciudad) #Normaliza los datos de ciudad a nfkc
                    ciudad=ciudad_nfkc.encode("ASCII",'ignore') #Y luego los deuvuelve a como estaba en ASCII

                    #Si no está la ciudad en la lista de ciudades se agrega
                    if ciudad not in lista_ciudades.values():
                        lista_ciudades.update({contador:ciudad})
                        contador+=1
                    #Si no, lo guardaremos en una lista especial para mostrar cuantos datos se eliminaron
                    else:
                        ciudades_eliminadas.append(ciudad)
                    
                break
            elif eleccion=="U":
                for ciudad in todas_las_ciudades:
                    ciudad=str(ciudad).upper()

                    #Ahora quitamos todos los acentos, tildes, etc con unicode
                    ciudad_nfkc=unicodedata.normalize("NFKC",ciudad) #Normaliza los datos de ciudad a nfkc
                    ciudad=ciudad_nfkc.encode("ASCII",'ignore') #Y luego los deuvuelve a como estaba en ASCII

                     #Si no está la ciudad en la lista de ciudades se agrega
                    if ciudad not in lista_ciudades.values():
                        lista_ciudades.update({contador:ciudad})
                        contador+=1
                    #Si no, lo guardaremos en una lista especial para mostrar cuantos datos se eliminaron
                    else:
                        ciudades_eliminadas.append(ciudad)
                    
                break
            elif eleccion=="L":
                for ciudad in todas_las_ciudades:
                    ciudad=str(ciudad).lower()

                    #Ahora quitamos todos los acentos, tildes, etc con unicode
                    ciudad_nfkc=unicodedata.normalize("NFKC",ciudad) #Normaliza los datos de ciudad a nfkc
                    ciudad=ciudad_nfkc.encode("ASCII",'ignore') #Y luego los deuvuelve a como estaba en ASCII

                     #Si no está la ciudad en la lista de ciudades se agrega
                    if ciudad not in lista_ciudades.values():
                        lista_ciudades.update({contador:ciudad})
                        contador+=1
                    #Si no, lo guardaremos en una lista especial para mostrar cuantos datos se eliminaron
                    else:
                        ciudades_eliminadas.append(ciudad)
                    
                break
            else:
                print("Elija una opción correcta ¡Alcornoque!")
        #Terminó la limpieza, ahora toca insertar
        if len(lista_ciudades.keys())!=0: #Si hay datos dentro de la lista de ciudades
            self.cursor.execute("CREATE TABLE IF NOT EXISTS datos_buenos (id INT PRIMARY KEY, ciudad VARCHAR(255))""") #Crea la tabla de los datos buenos
            for idCiudad, ciudadInsert in lista_ciudades.items(): #Utilizamos los datos guardados en nuestro diccionario anterior para comenzar a insertar los datos
                sql2="insert into datos_buenos values("+idCiudad+","+repr(ciudadInsert)+");"
                try:
                    self.cursor.execute(sql2)
                    self.conexion.commit()
                except Exception as err:
                    self.conexion.rollback()
                    print(err)
            print("Datos ingresados a la tabla")
    