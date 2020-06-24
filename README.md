# GENERACIÓN DE REPORTES DE CURSOS EDX
## Documentación
Actualmente el proyecto ofrece los siguientes servicios:
* Validar que se encuentren creadas secciones que se definan como obligatorias.
* Validar todas las urls que se encuentran incorporados en el curso.
* Validar todos los videos que se encuentran incorporados en el curso.
* Validar que se puedan visualizar los archivos en formato pdf que se encuentren incorporados en el curso.
* Validar si existen secciones sin contenido agregado.
* Visualización del estado en el que se encuentra el curso edX analizado, a través de una página web offline (```index.html```).
* Almacenamiento del estado en el que se encuentra el curso edX analizado, en la  base de datos NoSQL apache couchDB.
* Archivo configurable (```config.yml```) para la activación o desactivación de servicios requeridos.

###### Nota: En el archivo ```config.yml``` se establece por defecto que se apliquen todos estos servicios detallados. Si desea que alguno de estos servicios no se aplique debe dirigirse a este archivo y cambiar el estado a ```false``` en el atributo ```value``` de cada servicio

###### Importante: En el caso de que se encuentre activada la opcion que se almacene el estado del curso edX en couchDB (Revisar si es```true``` el estado en el archivo ```config.yml``` en el servicio ```couchDB_setup``` en el atributo ```value```) debe agregar o modificar los valores por defecto en caso de que sea necesario en los atributos que se detallan dentro del servicio ```couchDB_setup```.

## Ejecución
* Exporte el curso de edX
* Descomprima el archivo .tar.gz (le debe generar una carpeta con el nombre ```course```)
* Clone el repositoio (```Edx-Course-Report```) en el mismo directorio donde se encuentra el curso descomprimido de edX.   
		 
		 git clone https://github.com/CarlosCastillo10/Edx-Course-Report.git
* Ubiquese en el repositorio clonado.
		
		cd Edx-Course-Report
* Ejecute el script principal .
		
		python checkit.py
* El script le generá una carpeta dentro del curso (directorio ```course```) llamada ```course-report``` y dentro de la carpeta encontrará el archivo ``index.html`` donde se encuentra detallado el reporte del curso.
