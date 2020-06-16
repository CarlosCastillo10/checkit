#!/usr/bin/env python

from pathlib import Path
from collections import defaultdict
from collections import OrderedDict
from datetime import datetime
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET 
from shutil import rmtree
import os, fnmatch
import pafy
import httplib2 
import html 
import couchdb


class Doc:
    
    def __makeCourse(self):
        """
        Crea una lista de capítulos leyendo course.xml
        """
        course_file_list = list(self.course_path.iterdir())
        self.course_file = [x for x in course_file_list if x.suffix == '.xml'][0]
        self.getCourseDetails()
        course_txt = self.course_file.open().readlines()
        for cline in course_txt:
            if 'chapter' in cline:
                chap_name = cline.split('"')[1]
                self.chapter_list.append(chap_name)
    
    def getCourseDetails(self):
        """
        Obtiene el id y el nombre del curso que se encuentra en course.xml.
        Establece la fecha y la hora de la generación del reporte
        """
        treeID = ET.parse('course.xml')
        rootID = treeID.getroot()
        
        treeName = ET.parse(str(self.course_file))
        rootName = treeName.getroot()
        
        if 'course' in rootID.attrib:
            self.courseReport['courseID'] = (rootID.attrib['course'])
        
        if 'display_name' in rootName.attrib:
            self.course_title = (rootName.attrib['display_name']).upper()
            self.courseReport['courseName'] = (rootName.attrib['display_name']) # Nuevo
        
    def setConfigCourse(self):
        """
        Establece los criterios que se van a evualuar que se encuentran detallados en 
        el archivo config.txt
        """
        file = open('config.txt', 'r')
        for line in file:
            if (line and line.strip()):   
                criteria_dict = {'criteriaName':line.replace('\n',''), 'errors': 0}
                self.criteria_list.append(criteria_dict)
        
    def formMainCard(self, file_index):
        """
        Genera la estructura básica del html, agregando los estilos de bootstrap.
        Establece el componente card propio de bootstrap, donde se detalla el 
        titulo del curso.       
        @param: file_index: Parametro de tipo _io.TextIOWrapper, guarda la estructura 
        del reporte en formato html.
        """
        file_index.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n<title>%s</title>\n<meta '
            'charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-'
            'scale=1, shrink-to-fit=no">\n<link rel="stylesheet" '
            'href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" '
            'integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" '
            'crossorigin="anonymous">\n</head>\n<body>\n<div class="container">\n<div class="card '
            'border-info mb-3 mt-5">\n<H5 class="card-header bg-info text-white text-center">'
            'REPORTE - %s</H5>\n<div class="card-body">\n'%(self.course_title, self.course_title.upper()))
        
        self.formResumeCard(file_index) 
        self.formDetailsCard(file_index)
        file_index.write('</div>\n</div>\n</div>\n<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" '
            'integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous">'
            '</script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" '
            'integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" '
            'crossorigin="anonymous"></script>\n<script '
            'src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" '
            'integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous">'
            '</script>\n</body>\n</html>')
 
    def formResumeCard(self, file_index):
        """
        Establece el componente card propio de bootstrap, donde se detalla el resumen del reporte.       
        @param: file_index: Parametro de tipo _io.TextIOWrapper, guarda la estructura del
        reporte en formato html.
        """
        file_index.write('<div class="card bg-transparent border-success mb-5">\n<div class="card-header text-center '
            'bg-success border-success text-white">RESUMEN</div>\n<div class="card-body">\n'
            '<div class="table-responsive-sm">\n<table class="table table-sm table-hover">\n'
            '<p class="card-text text-dark">Aqui escribir algo</p>\n<thead class="table-success">\n<tr>\n'
            '<th scope="col"># Errores</th>\n<th scope="col">Criterio</th>\n'
            '<th scope="col">Estado</th>\n</tr>\n</thead>\n<tbody>\n')
        
        total_errors = self.formResumeTable(file_index)
        file_index.write('</tbody>\n<caption>Total errores: %d\n</table>\n</div>\n</div>\n</div>\n'%total_errors)
    
    def formResumeTable(self, file_index):
        """
        Establece la tabla de resumen donde se define la siguiente estructura
            +-----------+-----------+-----------+
            +  Errors   +  Criterio +   Estado  + 
            +-----------+-----------+-----------+
            +    0      +    ----   +   ----    +
            +    0      +    ----   +   ----    +
            +    0      +    ----   +   ----    +
            +-----------+-----------+-----------+
            + Total errores: 0                  +
            +-----------------------------------+ 

        Establece un icono check o un icono error de bootstrap, dependiente del valor de errores de 
        cada criterio evaluado
        @param: file_index: Parametro de tipo _io.TextIOWrapper, guarda la estructura del
        reporte en formato html.
        @return: total_errors: Numero total de errores del curso
        """
        total_errors = 0 
        for criterion in self.criteria_list:
            total_errors += criterion['errors']
            file_index.write('<tr>\n<th scope="row">%s</th>\n<td>%s</td>\n<td>\n'%(criterion['errors'], 
                criterion['criteriaName']))
            
            if criterion['errors'] == 0:
                file_index.write('<svg class="bi bi-check-circle-fill text-success" width="1.5em" height="1.5em" '
                    'viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n'
                    '<path fill-rule="evenodd" d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 '
                    '0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 '
                    '1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>\n</svg>\n')
            else:
                file_index.write('<svg class="bi bi-x-octagon-fill text-danger" width="1.5em" height="1.5em" '
                    'viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n'
                    '<path fill-rule="evenodd" d="M11.46.146A.5.5 0 0 0 11.107 0H4.893a.5.5 0 0 0-.353.146L.146 '
                    '4.54A.5.5 0 0 0 0 4.893v6.214a.5.5 0 0 0 .146.353l4.394 4.394a.5.5 0 0 0 .353.146h6.214a.5.5 '
                    '0 0 0 .353-.146l4.394-4.394a.5.5 0 0 0 .146-.353V4.893a.5.5 0 0 0-.146-.353L11.46.146zm.394 '
                    '4.708a.5.5 0 0 0-.708-.708L8 7.293 4.854 4.146a.5.5 0 1 0-.708.708L7.293 8l-3.147 3.146a.5.5 '
                    '0 0 0 .708.708L8 8.707l3.146 3.147a.5.5 0 0 0 .708-.708L8.707 8l3.147-3.146z"/>\n</svg>\n')
            
            file_index.write('</td>\n</tr>\n')
        return total_errors

    def formDetailsCard(self,file_index):
        """
        Establece el componente card propio de bootstrap, donde consta el detalle del reporte. 
        Obtiene cada capitulo de la lista de capitulos generada en __makeCourse y por cada uno genera 
        un componente card propio de bootstrap.     
        @param: file_index: Parametro de tipo _io.TextIOWrapper, guarda la estructura del
        reporte en formato html.
        """
        file_index.write('<div class="card bg-light border-secondary mb-3">\n'
            '<div class="card-header text-center bg-secondary border-success text-white">DETALLE</div>\n'
            '<div class="card-body">\n<div id="accordion">\n')
        num_heading = 0
        
        for chap_detail in self.detailChapters:
            num_heading += 1
            file_index.write('<div class="card border-info mb-3">\n'
                '<div class="card-header" id="heading%d">\n'
                '<button class="btn btn-outline-light" data-toggle="collapse" data-target="#collapse%d" '
                'aria-expanded="true" aria-controls="collapse%d">\n<svg class="bi bi-plus-square-fill text-dark" '
                'width="2em" height="2em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n'
                '<path fill-rule="evenodd" d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm6.5 '
                '4a.5.5 0 0 0-1 0v3.5H4a.5.5 0 0 0 0 1h3.5V12a.5.5 0 0 0 1 0V8.5H12a.5.5 0 0 0 0-1H8.5V4z"/>\n'
                '</svg>\n</button>\n%s       '%(num_heading, num_heading, num_heading, chap_detail['chapterName']))
            
            if chap_detail['totalErrors'] > 0:
                file_index.write('<span class="badge badge-pill badge-danger">')
            else:
                file_index.write('<span class="badge badge-pill badge-success">')
            
            file_index.write('%d</span>\n</div>\n'
                '<div id="collapse%d" class="collapse hide" aria-labelledby="heading%d" data-parent="#accordion">\n'
                '<div class="card-body">\n<div id="accordion1">\n'%(chap_detail['totalErrors'],num_heading, num_heading))
            
            # Por cada capítulo obtenemos la lista de secciones
            self.formDetailSections(file_index, chap_detail['sections']) 
            
            file_index.write('</div>\n</div>\n</div>\n</div>\n')    
        file_index.write('</div>\n</div>\n</div>\n')
    

    def formDetailSections(self, file_index, section_list):
        """ 
        Por cada seccion que contiene cada capítulo genera que contiene un componente card propio de bootstrap.     
        @param: file_index: Parametro de tipo _io.TextIOWrapper, guarda la estructura del reporte en formato html.
        @param: section_list: Lista de secciones de cada capítulo
        """
        for section in section_list:
            self.num_sectionErrors = 0
            self.num_subHeading += 1
            aux_typeCard = ''
            
            if section['totalErrors'] > 0:
                file_index.write('<div class="card border-danger mb-3">\n')
                aux_typeCard = '%s<span class="badge badge-pill badge-danger text-center">%d</span>\n'%(aux_typeCard, 
                    section['totalErrors'])
            else:
                file_index.write('<div class="card border-success mb-3">\n')
                aux_typeCard = '%s<span class="badge badge-pill badge-success text-center">%d</span>\n'%(aux_typeCard, 
                    section['totalErrors'])
            
            if ((len(section['subsections'][0]) == 0) and (section['totalErrors'] == 0)):
                file_index.write('<div class="card-header" id="subHeading%d">\n'
                    '%s     %s</div>\n</div>\n'%(self.num_subHeading, section['sectionName'], aux_typeCard))
            else:
                file_index.write('<div class="card-header" id="subHeading%d">\n'
                    '<button class="btn btn-outline-light" data-toggle="collapse" data-target="#subcollapse%d" '
                    'aria-expanded="true" aria-controls="subcollapse%d">\n<svg class="bi bi-plus-square-fill '
                    'text-dark" width="1.25em" height="1.25em" viewBox="0 0 16 16" fill="currentColor" '
                    'xmlns="http://www.w3.org/2000/svg">\n<path fill-rule="evenodd" d="M2 0a2 2 0 0 0-2 2v12a2 '
                    '2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm6.5 4a.5.5 0 0 0-1 0v3.5H4a.5.5 0 0 0 0 '
                    '1h3.5V12a.5.5 0 0 0 1 0V8.5H12a.5.5 0 0 0 0-1H8.5V4z"/>\n</svg>\n</button>\n%s     %s</div>\n'
                    '<div id="subcollapse%d" class="collapse hide" aria-labelledby="subHeading%d" '
                    'data-parent="#accordion1">\n<div class="card-body">\n'%(self.num_subHeading, self.num_subHeading, 
                        self.num_subHeading, section['sectionName'], aux_typeCard, self.num_subHeading, self.num_subHeading))
                
                # Si es que la sección contiene subsecciones
                if len(section['subsections'][0]) != 0:
                    self.formDetailSubSections(file_index, section['subsections']) 
                
                self.formListErrors(file_index, section['errors'],section['emptyContent'])
                file_index.write('</div>\n</div>\n</div>\n')
    
    def formDetailSubSections(self, file_index, subSection_list):
        """ 
        Obtiene de la lista de  que contiene 'chapterDetails' y por cada uno genera 
        un componente card propio de bootstrap.     
        @param: file_index: Parametro de tipo _io.TextIOWrapper, guarda la estructura del
        reporte en formato html.
        @param: section_list: Lista de secciones de cada capítulo
        """
        for subsection in subSection_list:
            self.num_subSectionHeading += 1
            aux_typeCard = ''
            if len(subsection['errors']) > 0:
                file_index.write('<div class="card border-danger mb-3">\n')
                aux_typeCard = '%s<span class="badge badge-pill badge-danger text-center">%d</span>\n'%(aux_typeCard, 
                    len(subsection['errors']))
            else:
                file_index.write('<div class="card border-success mb-3">\n')
                aux_typeCard = '%s<span class="badge badge-pill badge-success text-center">%d</span>\n'%(aux_typeCard, 
                    len(subsection['errors']))
            if len(subsection['errors']) == 0:
                file_index.write('<div class="card-header" id="subSectionHeading%d">\n'
                    '%s     %s</div>\n</div>\n'%(self.num_subSectionHeading, subsection['subsectionName'], 
                        aux_typeCard))
            else:
                file_index.write('<div class="card-header" id="subSectionHeading%d">\n'
                    '<button class="btn btn-outline-light" data-toggle="collapse" data-target="#subSectioncollapse%d" '
                    'aria-expanded="true" aria-controls="subSectioncollapse%d">\n<svg class="bi bi-plus-square-fill '
                    'text-dark" width="1.25em" height="1.25em" viewBox="0 0 16 16" fill="currentColor" '
                    'xmlns="http://www.w3.org/2000/svg">\n<path fill-rule="evenodd" d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 '
                    '2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm6.5 4a.5.5 0 0 0-1 0v3.5H4a.5.5 0 0 0 0 '
                    '1h3.5V12a.5.5 0 0 0 1 0V8.5H12a.5.5 0 0 0 0-1H8.5V4z"/>\n</svg>\n</button>\n%s     %s</div>\n'
                    '<div id="subSectioncollapse%d" class="collapse hide" aria-labelledby="subSectionHeading%d" '
                    'data-parent="#accordion1">\n<div class="card-body">\n'%(self.num_subSectionHeading, 
                        self.num_subSectionHeading, self.num_subSectionHeading, subsection['subsectionName'], 
                        aux_typeCard, self.num_subSectionHeading, self.num_subSectionHeading))
                
                self.formListErrors(file_index, subsection['errors'], subsection['emptyContent'])
                file_index.write('</div>\n</div>\n</div>\n')
            
    def formListErrors(self,file_index, list_errors, emptyContent):
        """
        Establece la tabla de descripción de errores donde se define la siguiente estructura
            +------------+-----------------------+
            + <criterio> +          ---          +
            +------------+          ---          +
            + <criterio> +          ---          +
            +------------+          ---          +
            + <criterio> +          ---          +
            +------------+-----------------------+

        @param: file_index: Parametro de tipo _io.TextIOWrapper, guarda la estructura del
        reporte en formato html.
        @param: list_errors: Listado de errores por cada unidad que contiene el curso
        """
        if emptyContent:
            list_errors.append({'errorName':'contenido vacio'})
        
        if list_errors:
            self.num_sectionErrors += 1
            file_index.write('<div class="row">\n<div class="col-4">\n<div class="list-group" id="list-tab" '
                'role="tablist">\n')
            txt_tabContent = '<div class="tab-content" id="nav-tabContent">\n'
            num_errors = 0
            for error in list_errors:
                nameError = error['errorName'].split(' ')[0]
                txt_details = ''
                if num_errors == 0:
                    file_index.write('<a class="list-group-item d-flex justify-content-between align-items-center '
                        'list-group-item-action list-group-item-info active" id="list-%s-list" data-toggle="list" '
                        'href="#list-%s" role="tab" aria-controls="%s">%s\n<span class="badge badge-danger '
                        'badge-pill">%d</span>\n</a>\n'%(nameError, nameError, nameError, error['errorName'], 
                            len(list_errors)))
                    
                    txt_tabContent = '%s<div class="tab-pane fade show active" id="list-%s" role="tabpanel" \
                        aria-labelledby="list-%s-list">'%(txt_tabContent, nameError, nameError)
                    num_errors+=1
                else:

                    file_index.write('<a class="list-group-item d-flex justify-content-between align-items-center '
                        'list-group-item-action list-group-item-info" id="list-%s-list" data-toggle="list" '
                        'href="#list-%s" role="tab" aria-controls="%s">%s\n<span class="badge badge-danger '
                        'badge-pill">%d</span>\n</a>\n'%(nameError, nameError, nameError, error['errorName'], 
                            len(list_errors)))
                    txt_tabContent = '%s<div class="tab-pane fade" id="list-%s" role="tabpanel" \
                        aria-labelledby="list-%s-list">'%(txt_tabContent, nameError, nameError)
                
                if error['errorName'] == 'contenido vacio':
                    txt_details = 'Solo se ha creado la sección pero no se ha ingresado contenido'
                
                elif error['errorName'] == 'url con error' or error['errorName'] == 'videos con error':
                    for url in error['urls']:
                        txt_details = '%s<li>%s\n'%(txt_details, url)

                txt_tabContent = '%s%s\n</div>'%(txt_tabContent,txt_details)
            file_index.write('</div>\n</div>\n<div class="col-8">\n%s\n</div>\n</div>\n</div>\n'%txt_tabContent)
    

    def checkUrls(self, file_adress):
        """
        Genera un diccionario con el detalle de urls que contiene cada unidad del curso
        @param: file_adress: Parametro de tipo Path que contiene la direccion de los archivos .html
        @return: dict_reportUrl: Diccionario que contiene el archivo analizado y el listado de urls
        """
        dict_reportUrl = {'file': '','urls':self.getUrls(file_adress)}
        return dict_reportUrl

    def getNumberErrors(self, criterion_dictionary):
        """
        Obtiene el numero de urls con error
        @param: criterion_dictionary: Parametro de tipo dict que contiene el listado de urls analizadas
        por cada unidad que contiene el curso.
        @return: num_errors: Numero de url con error
        """
        num_errors = 0 
        for criterion in criterion_dictionary['urls']:
            if 'incorrecto' in criterion['estado']:
                num_errors += 1
        return num_errors
    
    def getErrorsUrl(self, criterion_dictionary):
        """
        Obtiene el listado de urls con error
        @param: criterion_dictionary: Parametro de tipo dict que contiene el listado de urls analizadas
        por cada unidad que contiene el curso.
        @return: url_errorList: Numero de url con error
        """
        url_errorsList = [] 
        for criterion in criterion_dictionary['urls']:
            if 'incorrecto' in criterion['estado']:
                url_errorsList.append(criterion['url'])
        return url_errorsList
    
    def getUrls(self, file_adress):
        """
        Obtiene el listado de url que contiene cada archivo.
        @param: file_adress: Parametro de tipo Path que contiene la direccion de los archivos .html
        @return: list_stateUrls: Listado de urls.
        """
        list_stateUrls = []
        file_content = file_adress.open().readlines()
        url_pattern = re.compile(r'["]http([^"]*)') # Expresión regular

        list_url = [] 

        for line in file_content:
            match = url_pattern.search(line)
            if match:
                list_url.append(match.group().lstrip('"'))
        if list_url:
            list_stateUrls = self.validateUrlStatus(list_url) # Siempre y cuando el archivo contenga urls
        return list_stateUrls

    def validateUrlStatus(self, list_url):
        """
        Realiza una solicitud http por cada url. Si la respuesta devuelve un valor  diferenre de 200
        significa que la solicitud no pudo ser procesada y se determina como una url con error.
        @param: list_url: Parametro de tipo list que contiene el listado de urls de cada unidad.
        @return: list_states: Listado de urls con su estado.
        """
        list_states = []
        for url in list_url:
            try:
                response, content = httplib2.Http(disable_ssl_certificate_validation=True).request(html.unescape(url))
                if response.status != 200:
                    list_states.append({'url' : url, 'estado' : 'incorrecto'})                                    
            except httplib2.HttpLib2Error as err:
                pass
            
        return list_states
        
    def checkVideos(self, file_adress):
        """
        Obtiene por cada archivo .xml que se encuentre en la carpeta video,
        el valor que contiene el atributo youtube_id_1_0 y si le agrega a ese valor
        la estructura común de un video de youtube.
        @param: file_adress: Parametro de tipo Path que contiene la direccion de los archivos .xml
        @return: getVideoStatus(): Metodo que devuelve un True o False dependiente del estado del video.
        """
        tree = ET.parse(str(file_adress))
        root = tree.getroot()
        video_url = ''
        if 'youtube_id_1_0' in root.attrib:
            video_url = 'https://www.youtube.com/watch?v=%s'%(root.attrib['youtube_id_1_0'])
            self.url_video = video_url
        
        return self.getVideoStatus(video_url)

    def getVideoStatus(self, video_url):
        """
        Por cada url genera una instancia a través de la librería pafy.
        @param: video?url: Parametro de tipo str que contiene la direccion del video de youtube.
        @return: video_status: Contiene el estado del video, True si pudo obtener información del video
        caso contrario False.
        """
        video_status = True
        try:
            if video_url:
                video = pafy.new(video_url)
                video_status = True
        except:
            video_status = False
        return video_status

    def saveReportDB(self):
        """
        Guarda en la base en datos en el reporte total del curso
        """
        couchServer = couchdb.Server('http://openCampus:openCampus@127.0.0.1:5984')
        db = couchServer['course-report']
        db.save(self.courseReport)

    def __makeDraftStruct(self):
        """
        Obtener la estructura del curso
        """
        for v in self.draft_vert_path.iterdir():
            if v.suffix != '.xml':
                continue
            v_txt = v.open().readlines()
            fline = v_txt[0]
            sec_name = fline.split('parent_url=')[1].split('"')[1].split('/')[-1].split('@')[-1]
            rank = fline[fline.index('index'):].split('"')[1]
            comp_list = [int(rank), str(v)]
            for vline in v_txt[1:]:
                if '<problem ' in vline:
                    prob = vline.split('"')[1]
                    comp_list.append(['problem',prob])
                elif '<video ' in vline:
                    prob = vline.split('"')[1]
                    comp_list.append(['video', prob])
                elif '<html ' in vline:
                    prob = vline.split('"')[1]
                    comp_list.append(['html', prob])
            if sec_name not in self.draft_problems_struct.keys():
                self.draft_problems_struct[sec_name] = [comp_list]
            else:
                self.draft_problems_struct[sec_name].append(comp_list)
        for k in self.draft_problems_struct:
            sorted_struct = sorted(self.draft_problems_struct[k], key = lambda x: x[0])
            self.draft_problems_struct[k] = [s[1:] for s in sorted_struct]

    def __init__(self, start_path):
       
        if not os.path.isdir(start_path):
            sys.exit("\033[91m ERROR: can't find directory {} \033[0m".format(start_path))

        ## variables  numericas
        self.num_subHeading = 0
        self.num_subSectionHeading = 0
        self.num_sectionErrors = 0
        self.number_urlErrors = 0
        self.number_sectionErrors = 1
        self.number_videoErrors = 0
        self.number_emptyContent = 0

        # Varibales str
        self.url_video = ''
        self.course_title = ''

        # Variables de Path
        self.path = Path(start_path)
        self.course_path = self.path / 'course'
        self.chapter_path = self.path / 'chapter'
        self.seq_path = self.path / 'sequential'
        self.vert_path = self.path / 'vertical'

        self.draft_path = self.path / 'drafts'
        self.draft_vert_path = self.draft_path / 'vertical'

        # Variables auxiliares
        self.aux_course_path = 'course'
        self.aux_chapter_path = 'chapter'
        self.aux_seq_path = 'sequential'
        self.aux_vert_path ='vertical'

        self.aux_draft_path = 'drafts'
        self.aux_draft_vert_path = 'vertical'

        self.chapter_list = [] # lista de capitulos

        self.criteria_list = [] # lista de criterios

        ## Estructura de secciones y unidades
        self.draft_problems_struct = OrderedDict()
        self.public_problems_struct = OrderedDict()
        self.all_problems_struct = OrderedDict()
        self.detailChapters = []
        self.tmp_dictionary = {}
        self.seq_Details_list = []
        self.seqDetails_dict  = {}
        self.tmp_subsectionsDict = {}

        self.courseReport = {'courseID': '','courseName':'','reportDate': '',
            'reportTime':'','status':{}}
       

        self.__makeCourse()

        if self.draft_path.exists() and self.draft_vert_path.exists():
            self.__makeDraftStruct()
            
    def describeCourse(self):
        
        if os.path.isdir('%s/course-report'%self.path):
            rmtree('%s/course-report'%self.path) # Eliminar directorio 'course-report'
        
        os.mkdir('%s/course-report'%self.path) # Crear directorio 'course-report'
        
        file_index = open(str(self.path)+'/course-report/index.html','w') # Crear archivo 'index.html'
        self.setConfigCourse()
        self.describeChapter()
        self.criteria_list[0]['errors'] = self.number_sectionErrors
        self.criteria_list[1]['errors'] = self.number_urlErrors
        self.criteria_list[2]['errors'] = self.number_videoErrors
        self.criteria_list[3]['errors'] = self.number_emptyContent
        self.formMainCard(file_index)
        currentDate = datetime.now()
        self.courseReport['reportDate'] = str(currentDate.date())
        self.courseReport['reportTime'] = str('%d:%d:%d'%(currentDate.hour, currentDate.minute,
            currentDate.second))
        self.courseReport['status']['detailChapters'] = self.detailChapters
        self.saveReportDB()
        file_index.close()

    def describeChapter(self):
        """
        Obtener la informacion de cada capítulo del curso.
        """
        for c in self.chapter_list:
            self.tmp_dictionary = {}
            c += '.xml'
            cFile = self.chapter_path / c
            
            if os.path.isfile(str(cFile)):
                aux_cFile = '%s/%s'%(self.aux_chapter_path, c)
                chap_txt = cFile.open().readlines()
                cFile = cFile.relative_to(*cFile.parts[:1])

                first_line = chap_txt[0]
                chap_name = first_line.split('"')[1]
                self.tmp_dictionary = {'chapterName': chap_name, 'emptyContent': False,'totalErrors': 0
                    ,'sections':[]}
                
                if chap_name.lower() in ['espacio colaborativo','espacios colaborativo', 'collaborative space']:
                    self.number_sectionErrors = 0


                # eliminar el item inicial
                seq_list = [l.split('"')[1] for l in chap_txt if "sequential" in l]
                
                if not seq_list:
                    self.tmp_dictionary['emptyContent'] = True
                
                pub_seq_struct, all_seq_struct = self.describeSequen(seq_list)
                self.detailChapters.append(self.tmp_dictionary)

                ### estructura publica
                self.public_problems_struct[chap_name] = pub_seq_struct

                self.all_problems_struct['('+c[-9:-4]+')'+chap_name] = (str(cFile), all_seq_struct)

        self.public_problems_struct = dict((k, v) for k, v in self.public_problems_struct.items() if v)


    def describeSequen(self, seq):
        """
        Obtener la lista de secciones que contiene cada capítulo
        @param: seq: Listado de secciones
        """
        pub_seq = OrderedDict()
        all_seq = OrderedDict()
        tmp_seqDetails_list = []
        for s in seq:
            self.seqDetails_dict  = {}
            unpublished = False
            s_name = s + '.xml'
            sFile = self.seq_path / s_name
            aux_sFile = '%s/%s'%(self.aux_seq_path, s)
            seq_txt = sFile.open().readlines()
            sFile = sFile.relative_to(*sFile.parts[:1])
            first_line = seq_txt[0]
            sequ_name = first_line.split('"')[1]
            self.seqDetails_dict = {'sectionName': sequ_name, 'emptyContent': False, 'errors': [], 
                'totalErrors':0, 'subsections':[]}

            if len(seq_txt) > 2:
                unit_list = [l.split('"')[1] for l in seq_txt if "vertical" in l]
                
                pub_dict, all_dict = self.describeUnit(unit_list, sequ_name)
                pub_seq[sequ_name] = pub_dict

                if s in self.draft_problems_struct.keys():

                    old_list = self.draft_problems_struct[s][:]
                    for u in old_list:
                        u_id = u[0].split('/')[-1].split('.xml')[0]
                        if u_id in unit_list:
                            unpublished = True
                            self.draft_problems_struct[s].remove(u)
                    if self.draft_problems_struct[s]:
                        all_dict2 = self.describeDraftUnit(self.draft_problems_struct[s], sequ_name)
                        for d in all_dict2:
                            all_dict[d] = all_dict2[d]
                    
                    all_seq['('+s_name[-9:-4]+')'+sequ_name] = (str(sFile), all_dict)

                    if unpublished:
                        print('\033[93m Warning: There are unpublished changes in published problems under subsection {}. '
                            'Only looking at published version.\033[0m'.format(sequ_name))

            else: #check draft
                if s not in self.draft_problems_struct.keys():
                    all_dict = OrderedDict()
                else:
                    if not self.draft_problems_struct[s]:
                        self.seqDetails_dict['emptyContent'] = True
                    else:
                        all_dict = self.describeDraftUnit(self.draft_problems_struct[s], sequ_name)
                all_seq['('+s_name[-9:-4]+')'+sequ_name] = (str(sFile), all_dict)
            
            tmp_seqDetails_list.append(self.seqDetails_dict)
        
        self.tmp_dictionary['sections'] = tmp_seqDetails_list
        pub_seq = dict((k, v) for k, v in pub_seq.items() if v)
        return pub_seq, all_seq

    def describeUnit(self, uni, sequ_name):
        """
        Obtener la lista de unidades que contiene cada seccion.
        Se determina si el contenido de cada unidad, es un problema, un video o un html.
        @param: uni: Listado de subsecciones
        @param: sequ_name: Nombre de sección
        """
        tmp_subsectionsList = []
        pub_uni = OrderedDict()
        all_uni = OrderedDict()
        number_sectionErrors = 0
        for u in uni:
            u += '.xml'
            uFile = self.vert_path / u
            aux_uFile = '%s/%s'%(self.aux_vert_path, u)
            uni_txt = uFile.open().readlines()
            uFile = uFile.relative_to(*uFile.parts[:1])
            first_line = uni_txt[0]
            u_name = first_line.split('"')[1]
            self.tmp_subsectionsDict = {}
            aux_u_name = u_name
            if (len(uni) > 1):
                self.tmp_subsectionsDict = {'subsectionName': u_name, 'emptyContent': False, 
                    'errors': []}
            prob_list = []
            for l in uni_txt[1:]:
                if '<problem ' in l:
                    prob = l.split('"')[1]
                    prob_list.append(['problem',prob])
                elif '<video ' in l:
                    prob = l.split('"')[1]
                    prob_list.append(['video', prob])
                elif '<html ' in l:
                    prob = l.split('"')[1]
                    prob_list.append(['html', prob])
            
            if(u_name.lower() != 'encuesta de satisfacción'):
                if not prob_list:
                    number_sectionErrors += 1
                    self.tmp_dictionary['totalErrors'] += number_sectionErrors
                    self.number_emptyContent += 1
                    self.seqDetails_dict['totalErrors'] += number_sectionErrors
                    # Para validar contenido vacio de subsecctionaes
                    if 'errors' in self.tmp_subsectionsDict.keys():
                        self.tmp_subsectionsDict['emptyContent'] = True
                    else:
                        self.seqDetails_dict['emptyContent'] = True

            tmp_subsectionsList.append(self.tmp_subsectionsDict)
        
            pub_dict, all_dict = self.describeProb(prob_list, aux_u_name.lower())
            pub_uni[u_name] = pub_dict
            all_uni['('+u[-9:-4]+')'+u_name] = (str(uFile), all_dict)
        pub_uni = dict((k, v) for k, v in pub_uni.items() if v)
        self.seqDetails_dict['subsections'] = tmp_subsectionsList
        return pub_uni, all_uni

    def describeProb(self, prob_list, name):
        """
        Obtener la información de cada archivo detallado en la lista de secciones, o subsecciones
        @param: prob_list: Listado de archivos que conforman cada unidad del curso
        @param: name: Nombre unidad
        """
        pub_prob = OrderedDict()
        pro_list = []

        pat1 = re.compile(r'<problem ([^>]+)>')
        pat2 = re.compile(r'(\S+)="([^"]+)"')
        num_files = 0
        aux_u_name = name
        number_errorsUrl = 0
        errors_urlList = []
        number_errorsVideo = 0
        error_videoList = []

        for pro in prob_list:
            if pro[0] == 'html': # Condicion para ver si el archivo es un html
                pro_name = pro[1]+'.xml'
                pro_name_html = pro[1]+'.html' # obtener el arhivo html
                
                pFile = self.path / pro[0] / pro_name
                pFile_html = self.path / pro[0] / pro_name_html

                # Variable nueva
                file_adress = self.path / pro[0] / pro_name_html # direccion del archivo
                
                aux_pFile = '%s/%s'%(pro[0], pro_name)
                
                p_txt = pFile.open().readlines()
                p_txt_html = pFile_html.open().readlines()
                pFile = pFile.relative_to(*pFile.parts[:1])
                fline = p_txt[0]
                m = pat1.match(fline)
                if m:
                    params = m.group(1)
                    m2 = pat2.findall(params)
                    Dict= {key:val for key,val in m2 if key!='markdown'}
                    p_name = Dict['display_name']
                    if 'weight' in Dict.keys():
                        weight = Dict['weight']
                        if 'max_attempts' in Dict.keys():
                            max_att = Dict['max_attempts']
                            pub_prob[p_name] = {'file':pro_name, 'weight':Dict['weight'], 
                                'max_attempts':Dict['max_attempts']}
                        else:
                            pub_prob[p_name] = {'file':pro_name, 'weight':Dict['weight']}
                else:
                    '''
                    number_seqErrorsUrl = 0 
                    list_seqUrlErrors = []
                    list_subSeqUrlErrors = []
                    criterion_dictionary = self.checkUrls(file_adress)
                    
                    if criterion_dictionary['urls']:
                        number_errorsUrl = self.getNumberErrors(criterion_dictionary) 
                        errors_urlList = self.getErrorsUrl(criterion_dictionary)
                        number_seqErrorsUrl = number_errorsUrl 
                        list_seqUrlErrors = errors_urlList
                        
                        if 'errors' in self.tmp_subsectionsDict.keys():
                            list_subSeqUrlErrors = errors_urlList
                            criterio_dict = {'errorName': 'url con error', 'urls':list_subSeqUrlErrors}
                            self.tmp_subsectionsDict['errors'].append(criterio_dict)
                        else:
                            criterio_dict = {'errorName': 'url con error', 'urls': list_seqUrlErrors}
                            self.seqDetails_dict['errors'].append(criterio_dict)
                        self.number_urlErrors += number_errorsUrl
                    
                    self.seqDetails_dict['totalErrors'] +=  number_seqErrorsUrl
                    '''
                pro_list.append((str(pFile), pro[0]))
                
            
            elif pro[0] == 'video':
                pro_name = pro[1]+'.xml'
                pFile = self.path / pro[0] / pro_name
                file_adress = self.path / pro[0] / pro_name
                '''
                number_seqErrorsVideo = 0
                number_subSeqErrorsVideo = 0
                list_seqVideoErrors = []
                list_subSeqVideoErrors = []
                
                if not self.checkVideos(file_adress):
                    number_errorsVideo += 1
                    number_seqErrorsVideo += 1
                    error_videoList.append(self.url_video)
                    if 'errors' in self.tmp_subsectionsDict.keys():
                        criterio_dict = {'errorName': 'videos con error', 'urls': error_videoList}
                        self.tmp_subsectionsDict['errors'].append(criterio_dict)
                    else:
                        criterio_dict = {'errorName': 'videos con error', 'urls': error_videoList}
                        self.seqDetails_dict['errors'].append(criterio_dict)
                    self.number_videoErrors += 1
                
                self.seqDetails_dict['totalErrors'] += number_seqErrorsVideo
                '''

            elif pro[0] == 'problem':
                letters = list(range(97,123))
                pro_name = pro[1]+'.xml'
                pFile = self.path / pro[0] / pro_name
                txt_problem = pFile.open().readlines()
                txt_problem = txt_problem[1:]
                txt_problem = txt_problem[:-1]
                
        if number_errorsUrl > 0:
            self.tmp_dictionary['totalErrors'] += number_errorsUrl
        if number_errorsVideo > 0:
            self.tmp_dictionary['totalErrors'] += number_errorsVideo
        
        return pub_prob, pro_list

    def describeDraftUnit(self, unit, sequ_name):
        """
        Obtener la lista de unidades que contiene la seccion de anuncios.
        @param: unit: Listado de unidades
        @param: sequ_name: Nombre de sección
        """
        all_uni = OrderedDict()
        tmp_subsectionsList = []

        for u in unit:
            uFile = Path(u[0])
            aux_uFile = u[0].split('/')
            aux_uFile = '%s/%s/%s'%(aux_uFile[-3],aux_uFile[-2],aux_uFile[-1])
            first_line = uFile.open().readlines()[0]
            uFile = uFile.relative_to(*uFile.parts[:1])
            u_name = first_line.split('"')[1]
            aux_u_name = u_name
            if (len(unit) > 1):
                self.tmp_subsectionsDict = {'subsectionName': u_name, 'errors': []}

            tmp_subsectionsList.append(self.tmp_subsectionsDict)
            prob_list = self.describeDraftProb(u[1:], aux_u_name.lower())
            all_uni['('+u[0][-9:-4]+')(draft)'+u_name] = (str(uFile), prob_list)
        self.seqDetails_dict['subsections'] = tmp_subsectionsList
        return all_uni

    
    def describeDraftProb(self, probs, aux_u_name):
        """
        Obtener la información de cada archivo detallado en la lista de unidades de la seccion
        de anuncios
        @param: probs: Listado de archivos que conforman la seccion de anuncios
        @param: aux_u_name: Nombre unidad
        """
        prob_list = []
        txt_prob = ''
        num_drafts_prob = 0
        number_errorsUrl = 0
        errors_urlList = []
        tmp_aux_u_name = aux_u_name
        for pro in probs:
            pro_name = pro[1]+'.xml'
            pro_name_html = pro[1]+'.html'
            pFile = self.draft_path / pro[0] / pro_name
            aux_pFile = '%s/%s/%s'%(self.aux_draft_path,pro[0],pro_name_html)
            
            pFile_html = self.draft_path / pro[0] / pro_name_html
            
            file_adress = self.draft_path / pro[0] / pro_name_html
            
            p_txt = pFile.open().readlines()

            p_txt_html = pFile_html.open().readlines()
    
            pFile = pFile.relative_to(*pFile.parts[:1])
            fline = p_txt[0]
            p_name = fline.split('"')[1]
           
            if pro[0] == 'problem':
                pass
            else:
                '''
                number_seqErrorsUrl = 0
                list_seqUrlErrors = []
                list_subSeqUrlErrors = []
                criterion_dictionary = self.checkUrls(file_adress)
                if criterion_dictionary['urls']:
                    number_errorsUrl = self.getNumberErrors(criterion_dictionary)
                    errors_urlList = self.getErrorsUrl(criterion_dictionary)
                    number_seqErrorsUrl = number_errorsUrl
                    list_seqUrlErrors = errors_urlList
                    if 'errors' in self.tmp_subsectionsDict.keys():
                        list_subSeqUrlErrors = errors_urlList
                        criterio_dict = {'errorName': 'url con error', 'urls':list_subSeqUrlErrors}
                        self.tmp_subsectionsDict['errors'].append(criterio_dict)
                    else:
                        criterio_dict = {'errorName': 'url con error', 'urls': list_seqUrlErrors}
                        self.seqDetails_dict['errors'].append(criterio_dict)
                    self.number_urlErrors += number_errorsUrl
                
                self.seqDetails_dict['totalErrors'] +=  number_seqErrorsUrl
                '''
            prob_list.append((str(pFile), '(draft)'+pro[0]))
            
        if number_errorsUrl > 0:
            self.tmp_dictionary['totalErrors'] += self.tmp_dictionary['totalErrors'] + number_errorsUrl
        return prob_list

if __name__ == "__main__":
    if len(sys.argv) != 2:
        pass
    else:
        folder_name = sys.argv[1]
        os.getcwd()
    writeDoc = Doc(os.getcwd())
    writeDoc.describeCourse()