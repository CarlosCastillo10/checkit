"""
  script que se encarga de guardar el reporte en la base de datos NoSQL couchDB.
"""
import sys

try:
    import couchdb
except:
    print('\033[91m\nError de importación (Verifique que tenga instalado couchDB, o '
        'que no existan un error en el nombre de la libreria)\n')
    sys.exit(1)

class Persistence:

    def __init__(self, course_report, couchDB_setup, file_adress):

        self.course_report = course_report
        self.couchDB_setup = couchDB_setup
        self.saveReportDB(file_adress)

    def saveReportDB(self, file_adress):
        """
        Guarda en la base en datos en el reporte total del curso
        """
        try:
            print(file_adress)
            couch_server = couchdb.Server('http://%s:%s@%s:%s'%(self.couchDB_setup['username'], 
                self.couchDB_setup['password'], self.couchDB_setup['domain'], self.couchDB_setup['port']))
            
            db = couch_server[self.couchDB_setup['database_name']]
            db.save(self.course_report)
            
            # Convertir a bytes el contenido del archivo
            file_index = bytes(open('index.html').read(), 'utf-8')
            
            # Guardar archivo en couchDB
            db.put_attachment(self.course_report, file_index, filename="index.html")
            
            print('\033[92m\nGuardado con exito en couchDB')
        
        # Si se esta ejecutando couchDB o en el puerto
        except ConnectionRefusedError:
            print('\033[91m\nError de conexión (Compruebe que haya iniciado couchDB, o que '
                'el valor del atributo <port> sea el correcto)\n')
        
        # Si el usuario o la contraseña son incorrectos
        except couchdb.http.Unauthorized:
            print('\033[91m\nError de autenticación (<username> o <password> incorrecto)\n')
        
        # Si la dirección IP del localhost no es correcta
        except OSError:
            print('\033[91m\nError de direccion IP (Compruebe la dirección IP del localhost)\n')
        
        # Cuando no se encuentra la base de datos creada o el nombre es incorrecto
        except couchdb.http.ResourceNotFound:
            print('\033[91m\nRecurso no encontrado (Compruebe si el nombre de la base de datos es '
                'correcto, o si la base de datos existe)\n')
        # Cuando el valor del atributo <database_name> del archivo config.yml esta vacio
        except TypeError:
            print('\033[91m\nError: Valor incorrecto (Debe ingresar el nombre de la base de datos en el atributo <database_name>)\n')
