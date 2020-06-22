"""
    script que se encarga de guardar el reporte en la base de datos NoSQL couchDB
"""
import sys

try:
    import couchdb
except:
    print('\033[91m\nError de importación (Verifique que tenga instalado couchDB, o '
        'que no existan un error en el nombre de la libreria)\n')
    sys.exit(1)

class Persistence:

    def __init__(self, course_report, couchDB_setup):

        self.course_report = course_report
        self.couchDB_setup = couchDB_setup
        self.saveReportDB()

    def saveReportDB(self):
        """
        Guarda en la base en datos en el reporte total del curso
        """
        try:
            couch_server = couchdb.Server('http://%s:%s@%s:%s'%(self.couchDB_setup['username'], 
                self.couchDB_setup['password'], self.couchDB_setup['domain'], self.couchDB_setup['port']))
            
            db = couch_server[self.couchDB_setup['database_name']]
            db.save(self.course_report)
            print('\033[92m\nGuardado con exito en couchDB\n')
        
        # Si existen fallos en el inicio de couchDB o en el puerto
        except ConnectionRefusedError:
            print('\033[91m\nError de conexión (Compruebe que haya iniciado couchDB, o que '
                'el valor del atributo <port> sea el correcto)\n')
        
        # Si el usuario o la contraseña son incorrectos
        except couchdb.http.Unauthorized:
            print('\033[91m\nError de autenticación (Usuario o contraseña incorrecto)\n')
        
        # Si la dirección IP del localhost no es correcta
        except OSError:
            print('\033[91m\nError de direccion IP (Compruebe la dirección IP del localhost)\n')
        
        # Cuando no se encuentra la base de datos creada o el nombre es incorrecto
        except couchdb.http.ResourceNotFound:
            print('\033[91m\nRecurso no encontrado (Compruebe si el nombre de la base de datos es '
                'correcto, o si la base de datos existe)\n')
