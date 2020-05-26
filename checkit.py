#!/usr/bin/env python

from pathlib import Path
from collections import defaultdict
from collections import OrderedDict
import re
import json
import sys
import os
import unicodedata
import xml.etree.ElementTree as ET 
from shutil import rmtree
import os, fnmatch
import pafy
import shutil
import httplib2 # Nueva


class Doc:
    
    # Pendiente documentar todo

    # Obtener curso
    def __makeCourse(self):
        """
        Create a list of chapters by reading course.xml
        """
        course_file_list = list(self.course_path.iterdir())
        self.course_file = [x for x in course_file_list if x.suffix == '.xml'][0]
        self.obtener_course_title()
        course_txt = self.course_file.open().readlines()
        for cline in course_txt:
            if 'chapter' in cline:
                chap_name = cline.split('"')[1]
                self.chapter_list.append(chap_name)
    
    def obtener_course_title(self):
        tree = ET.parse(str(self.course_file))
        root = tree.getroot()
        if 'display_name' in root.attrib:
            self.course_title = (root.attrib['display_name']).upper()
    
    # Metodo para formar el card principal
    def formMainCard(self, file_index):
        file_index.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n<title>%s</title>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">\n'
            '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">\n</head>\n<body>\n'
            '<div class="container">\n<div class="card border-info mb-3 mt-5">\n<H5 class="card-header bg-info text-white text-center">REPORTE - %s</H5>\n<div class="card-body">\n'
            %(self.course_title, self.course_title.upper()))
        self.formResumeCard(file_index)
        self.formDetailsCard(file_index)
        file_index.write('</div>\n</div>\n</div>\n'
            '<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>\n'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>\n'
            '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>\n'
            '</body>\n</html>')
 
    # Metodo para formar el card de Resumen
    def formResumeCard(self, file_index):
        file_index.write('<div class="card bg-transparent border-success mb-5">\n<div class="card-header text-center bg-success border-success text-white">RESUMEN</div>\n'
            '<div class="card-body">\n<div class="table-responsive-sm">\n<table class="table table-sm table-hover">\n'
            '<p class="card-text text-dark">Aqui escribir algo</p>\n'
            '<thead class="table-success">\n<tr>\n<th scope="col"># Errores</th>\n<th scope="col">Criterio</th>\n<th scope="col">Estado</th>\n</tr>\n</thead>\n<tbody>\n')
        total_errors = self.formResumeTable(file_index)
        file_index.write('</tbody>\n<caption>Total errores: %d\n</table>\n</div>\n</div>\n</div>\n'%total_errors)
    
    # Metodo para formar la tabla de resumen
    def formResumeTable(self, file_index):
        total_errors = 0
        for criterion in self.criteria_list:
            total_errors += criterion['errores']
            file_index.write('<tr>\n<th scope="row">%s</th>\n<td>%s</td>\n<td>\n'%(criterion['errores'], criterion['criterio']))
            if criterion['errores'] == 0:
                file_index.write('<svg class="bi bi-check-circle-fill text-success" width="1.5em" height="1.5em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n'
                    '<path fill-rule="evenodd" d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>\n'
                    '</svg>\n')
            else:
                file_index.write('<svg class="bi bi-x-octagon-fill text-danger" width="1.5em" height="1.5em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n'
                    '<path fill-rule="evenodd" d="M11.46.146A.5.5 0 0 0 11.107 0H4.893a.5.5 0 0 0-.353.146L.146 4.54A.5.5 0 0 0 0 4.893v6.214a.5.5 0 0 0 .146.353l4.394 4.394a.5.5 0 0 0 .353.146h6.214a.5.5 0 0 0 .353-.146l4.394-4.394a.5.5 0 0 0 .146-.353V4.893a.5.5 0 0 0-.146-.353L11.46.146zm.394 4.708a.5.5 0 0 0-.708-.708L8 7.293 4.854 4.146a.5.5 0 1 0-.708.708L7.293 8l-3.147 3.146a.5.5 0 0 0 .708.708L8 8.707l3.146 3.147a.5.5 0 0 0 .708-.708L8.707 8l3.147-3.146z"/>\n'
                    '</svg>\n')
            file_index.write('</td>\n</tr>\n')
        return total_errors

    def formDetailsCard(self,file_index):
        file_index.write('<div class="card bg-light border-secondary mb-3">\n'
            '<div class="card-header text-center bg-secondary border-success text-white">DETALLE</div>\n'
            '<div class="card-body">\n<div id="accordion">\n')
        num_heading = 0
        for chap_detail in self.chapterDetails:
            num_heading += 1
            file_index.write('<div class="card border-info mb-3">\n'
                '<div class="card-header" id="heading%d">\n'
                '<button class="btn btn-outline-light" data-toggle="collapse" data-target="#collapse%d" aria-expanded="true" aria-controls="collapse%d">\n'
                '<svg class="bi bi-plus-square-fill text-dark" width="2em" height="2em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n'
                '<path fill-rule="evenodd" d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm6.5 4a.5.5 0 0 0-1 0v3.5H4a.5.5 0 0 0 0 1h3.5V12a.5.5 0 0 0 1 0V8.5H12a.5.5 0 0 0 0-1H8.5V4z"/>\n'
                '</svg>\n</button>\n%s       '%(num_heading, num_heading, num_heading, chap_detail['chapter_name']))
            if chap_detail['total_errors'] > 0:
                file_index.write('<span class="badge badge-pill badge-danger">')
            else:
                file_index.write('<span class="badge badge-pill badge-success">')
            file_index.write('%d</span>\n</div>\n'
                '<div id="collapse%d" class="collapse hide" aria-labelledby="heading%d" data-parent="#accordion">\n'
                '<div class="card-body">\n<div id="accordion1">\n'%(chap_detail['total_errors'],num_heading, num_heading))
            self.formDetailSections(file_index, chap_detail['sections'])
            file_index.write('</div>\n</div>\n</div>\n</div>\n')    
        file_index.write('</div>\n</div>\n</div>\n')
    
    def formDetailSections(self, file_index, section_list):
        for section in section_list:
            self.num_subHeading += 1
            aux_typeCard = ''
            if section['total_errors'] > 0:
                file_index.write('<div class="card border-danger mb-3">\n')
                aux_typeCard = '%s<span class="badge badge-pill badge-danger text-center">%d</span>\n'%(aux_typeCard, section['total_errors'])
            else:
                file_index.write('<div class="card border-success mb-3">\n')
                aux_typeCard = '%s<span class="badge badge-pill badge-success text-center">%d</span>\n'%(aux_typeCard, section['total_errors'])
            
            file_index.write('<div class="card-header" id="subHeading%d">\n'
                '<button class="btn btn-outline-light" data-toggle="collapse" data-target="#subcollapse%d" aria-expanded="true" aria-controls="subcollapse%d">\n'
                    '<svg class="bi bi-plus-square-fill text-dark" width="1.25em" height="1.25em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n'
                    '<path fill-rule="evenodd" d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm6.5 4a.5.5 0 0 0-1 0v3.5H4a.5.5 0 0 0 0 1h3.5V12a.5.5 0 0 0 1 0V8.5H12a.5.5 0 0 0 0-1H8.5V4z"/>\n'
                    '</svg>\n</button>\n%s     %s</div>\n<div id="subcollapse%d" class="collapse hide" aria-labelledby="subHeading%d" data-parent="#accordion1">\n'
                    '<div class="card-body">Aqui va el detalle de errores</div>\n</div>\n</div>\n'%(self.num_subHeading, self.num_subHeading, self.num_subHeading, section['name_seq'], aux_typeCard, self.num_subHeading, self.num_subHeading))    
    
    # Metodo para validar cada url de cada archivo
    def checkUrls(self, file_adress):
        dict_reportUrl = {'file': '','urls':self.getUrls(file_adress)}
        return dict_reportUrl

    # Metodo para obtener el numero de errores de cada criterio
    def getNumberErrors(self, criterion_dictionary):
        num_errors = 0 
        for criterion in criterion_dictionary['urls']:
            if 'incorrecto' in criterion['estado']:
                num_errors += 1
        return num_errors
    
    # Metodo para obtener las url de cada archivo
    def getUrls(self, file_adress):

        list_stateUrls = []
        file_content = file_adress.open().readlines()

        # Expresión regular que obtiene solo las urls
        url_pattern = re.compile(r'["]http([^"]*)')

        list_url = [] # Lista que almacenara las url

        for line in file_content:
            match = url_pattern.search(line)
            if match:
                list_url.append(match.group().lstrip('"'))
        if list_url:
            list_stateUrls = self.validateUrlStatus(list_url)
        
        return list_stateUrls

    # Metodo para validar cada url
    def validateUrlStatus(self, list_url):
        list_states = []
        for url in list_url:
            try:
                # Diccionario donde se almacena la url y su estado
                dict_urlState = {'url' : url, 'estado' : ''}

                response, content = httplib2.Http(disable_ssl_certificate_validation=True).request(url)
                if response.status == 200:
                    dict_urlState['estado'] = 'correcto'
                else:
                    dict_urlState['estado'] = 'incorrecto'
                list_states.append(dict_urlState)
            except httplib2.HttpLib2Error as err:
                pass
            
        return list_states
        
    # Metodo para validar cada video de la carpeta 'video'
    def checkVideos(self, file_adress):
        tree = ET.parse(str(file_adress))
        root = tree.getroot()
        video_url = ''
        if 'youtube_id_1_0' in root.attrib:
            video_url = 'https://www.youtube.com/watch?v=%s'%(root.attrib['youtube_id_1_0'])
        
        return self.getVideoStatus(video_url)
    
    # Metodo que permite verificar si el video esta disponible
    def getVideoStatus(self, video_url):
        video_status = True
        try:
            if video_url:
                video = pafy.new(video_url)
                video_status = True
        except:
            video_status = False
        return video_status
    '''
    def checkEmptyContent(self, file_adress):
        tree = ET.parse(file_adress)
        root = tree.getroot()

        # Lista que obtiene la url de cada nodo hijo 
        list_urlNames = [child.attrib.get('url_name') for child in root ]
        
        if not list_urlNames:
            return False
        
        return True
    '''

    # Obtener estructura del curso
    def __makeDraftStruct(self):
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

    # Constructor
    def __init__(self, start_path):
       
        if not os.path.isdir(start_path):
            sys.exit("\033[91m ERROR: can't find directory {} \033[0m".format(start_path))

        ## variables  numericas
        self.first_page = ''
        self.num_chapts = 0
        self.num_seq = 0
        self.num_units = 0
        self.num_pages = 0
        self.num_drafts = 0
        self.tmp_name_equal = ''
        self.url_video = ''
        self.type_content = 0
        self.course_title = ''
        self.num_id_seq = 0
        self.num_subHeading = 0

        # Variables nuevas
        self.number_urlErrors = 0
        self.number_sectionErrors = 1
        self.number_videoErrors = 0
        self.number_emptyContent = 0
        self.chapter_name = ''

        # Variables de Path
        self.path = Path(start_path)
        self.course_path = self.path / 'course'
        self.chapter_path = self.path / 'chapter'
        self.seq_path = self.path / 'sequential'
        self.vert_path = self.path / 'vertical'

        self.draft_path = self.path / 'drafts'
        self.draft_vert_path = self.draft_path / 'vertical'

        ## Variables auxiliares
        self.aux_course_path = 'course'
        self.aux_chapter_path = 'chapter'
        self.aux_seq_path = 'sequential'
        self.aux_vert_path ='vertical'

        self.aux_draft_path = 'drafts'
        self.aux_draft_vert_path = 'vertical'
        self.file_uno = ''

        ## lista de capitulos
        self.chapter_list = []
        self.pathsHtml = []
        self.criteria_list = [{'criterio':'seccion espacio colaborativo', 'errores': 0}, {'criterio': 'url con error', 'errores': 0},
            {'criterio':'videos con error','errores':0}, {'criterio': 'contenido vacio','errores': 0},{'criterio':'pdf con error', 'errores': 0}]
        ## Estructura de secciones y unidades
        self.draft_problems_struct = OrderedDict()
        self.public_problems_struct = OrderedDict()
        self.all_problems_struct = OrderedDict()
        self.chapterDetails = []
        self.tmp_dictionary = {}
        self.seq_Details_list = []
        self.seqDetails_dict  = {}

        ## obtener estructura del curso
        self.__makeCourse()

        if self.draft_path.exists() and self.draft_vert_path.exists():
            self.__makeDraftStruct()
            
    def describeCourse(self):
        
        # Validar si el directorio 'course-report' existe
        if os.path.isdir('%s/course-report'%self.path):
            rmtree('%s/course-report'%self.path) # Eliminar directorio 'course-report'
        
        os.mkdir('%s/course-report'%self.path) # Crear directorio 'course-report'
        
        file_index = open(str(self.path)+'/course-report/index.html','w') # Crear archivo 'index.html'
        '''
        file_index.write('<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n</head>\n'
            '<style>\nimg{\ndisplay:inline-block;\nwidth: %s\n}\n'
            'body{\nborder-bottom: 3px solid #CE7D35;\n}\n'
            'h1{\nvertical-align:top;\ndisplay:inline-block;\ntext-align: center;\npadding-top: 20px;\nwidth: %s\n}\n</style>\n'
            '<title>REPORTE %s</title>\n</head>\n<body>\n<div>\n'
            '<img src="http://opencampus.utpl.edu.ec/static/themes/utpl_final/images/openCampus_logo.3c9532a0c56d.png">\n'
            '<h1>%s\n</h1>\n</div>\n<ul>\n'%('15%;','70%;',self.course_title, self.course_title))
        '''

        readme = open(str(self.path)+'/README.md', 'w')
        readme.write("###Course structure - [course/{0}](course/{0})\n".format(self.course_file.name))     
        self.describeChapter(readme, file_index)
        self.criteria_list[0]['errores'] = self.number_sectionErrors
        self.criteria_list[1]['errores'] = self.number_urlErrors
        self.criteria_list[2]['errores'] = self.number_videoErrors
        self.criteria_list[3]['errores'] = self.number_emptyContent
        
        self.formMainCard(file_index)
        file_index.close()
        readme.close()
        # file_index.write('</ul>\n</body>\n</html>')
        # file_index.close()

    # Obtener menu principal
    def describeChapter(self, readme, file_index):
   
        num_id = 0
        # print(self.chapter_list)
        for c in self.chapter_list:
            self.tmp_dictionary = {}
            # build path
            c += '.xml'
            cFile = self.chapter_path / c
            
            if os.path.isfile(str(cFile)):
                aux_cFile = '%s/%s'%(self.aux_chapter_path, c)
                chap_txt = cFile.open().readlines()
                cFile = cFile.relative_to(*cFile.parts[:1])

                first_line = chap_txt[0]
                chap_name = first_line.split('"')[1]
                self.tmp_dictionary = {'chapter_name': chap_name,'total_errors': 0,'sections':[]}
                if chap_name.lower() in ['espacio colaborativo','espacios colaborativo', 'collaborative space']:
                    self.number_sectionErrors = 0

                readme.write('* [Section] {0} - [{1}]({1})\n'.format(chap_name, aux_cFile))

                # Formar menu principal
                num_id+=1
                # file_index.write('<li>%s'%chap_name)
                '''
                frame_izquierdo.write('<div class="row">\n<li class="col-11 nav-item" id="principal"><a class="nav-link" '
                    'href="#" role="button" data-toggle="collapse" data-target="#submenu%d" aria-haspopup="true" '
                    'aria-expanded="false">%s</a>'%(num_id,chap_name))
                '''
                # Nombre del directorio
                # namePath_html = '%s'%(self.eliminar_carateres_especiales(chap_name.replace(' ','-').lower()))
                '''
                if os.path.isdir('%s/course-html/content/%s'%(str(self.path), namePath_html)):
                    self.num_chapts =+ 1
                    namePath_html = '%s-%d'%(namePath_html,self.num_chapts)
               
                os.mkdir('%s/course-html/content/%s'%(str(self.path),namePath_html))
                '''
                
                # namePath = self.eliminar_carateres_especiales(chap_name.replace(' ','-').lower())
                
                # self.pathsHtml.append(namePath_html)
                #index.write('<section><h1> %s</h1></section>\n'%(chap_name))

                # eliminar el item inicial
                seq_list = [l.split('"')[1] for l in chap_txt if "sequential" in l]

                pub_seq_struct, all_seq_struct = self.describeSequen(seq_list, readme, file_index, num_id)
                self.chapterDetails.append(self.tmp_dictionary)
                # file_index.write('</li>\n')
                # frame_izquierdo.write('</li>\n<span class="pt-3 col-1 dropdown-toggle"></span>\n</div>\n')

                ### estructura publica
                self.public_problems_struct[chap_name] = pub_seq_struct

                self.all_problems_struct['('+c[-9:-4]+')'+chap_name] = (str(cFile), all_seq_struct)
            #print(self.pathsHtml)
        

        self.public_problems_struct = dict((k, v) for k, v in self.public_problems_struct.items() if v)


    def describeSequen(self, seq, readme, file_index, num_id):
        pub_seq = OrderedDict()
        all_seq = OrderedDict()
        tmp_seqDetails_list = []
        # file_index.write('\n<ul>\n')
        # frame_izquierdo.write('\n<ul class="collapse navbar-nav flex-column" id="submenu%d">\n'%num_id) 
        for s in seq:
            self.seqDetails_dict  = {}
            self.num_units = 0;
            unpublished = False
            s_name = s + '.xml'
            sFile = self.seq_path / s_name
            aux_sFile = '%s/%s'%(self.aux_seq_path, s)
            seq_txt = sFile.open().readlines()
            sFile = sFile.relative_to(*sFile.parts[:1])
            first_line = seq_txt[0]
            sequ_name = first_line.split('"')[1]
            self.seqDetails_dict = {'name_seq': sequ_name, 'total_errors': 0}
            readme.write('\t* [Subsection] {0} - [{1}]({1})  \n'.format(sequ_name, aux_sFile))
            self.tmp_name_equal = sequ_name
            '''
            if os.path.isdir('%s/course-html/content/%s/%s'%(str(self.path), path,sequ_name):
                self.num_seq =+ 1
                sequ_name = '%s-%d'%(sequ_name,self.num_seq)
            os.mkdir('%s/course-html/content/%s/%s'%(str(self.path), path,sequ_name))
            '''

            if len(seq_txt) > 2:
                unit_list = [l.split('"')[1] for l in seq_txt if "vertical" in l]
                
                if (len(unit_list) > 1):
                    self.num_id_seq +=1
                    # file_index.write('<li>%s'%self.tmp_name_equal)
                    '''
                    frame_izquierdo.write('<div class="row">\n<li class="col-11 nav-item" id="principal2"><a class="nav-link" '
                        'href="#" role="button" data-toggle="collapse" data-target="#menu-submenu%d" aria-haspopup="true" '
                        'aria-expanded="false">%s</a></li>\n'
                        '<span class="pt-3 col-1 dropdown-toggle"></span>\n</div>\n'%(self.num_id_seq, self.tmp_name_equal))
                    
                    frame_izquierdo.write('\n<ul class="collapse navbar-nav flex-column" id="menu-submenu%d">\n'%self.num_id_seq) 
                    '''
                    # file_index.write('\n<ul>\n')
                    pub_dict, all_dict = self.describeUnit(unit_list, readme, file_index, sequ_name)
                    # frame_izquierdo.write('</ul>\n')
                    # file_index.write('</ul>\n')
                else:
                    pub_dict, all_dict = self.describeUnit(unit_list, readme, file_index, sequ_name)
                pub_seq[sequ_name] = pub_dict

                if s in self.draft_problems_struct.keys():

                    old_list = self.draft_problems_struct[s][:]
                    for u in old_list:
                        u_id = u[0].split('/')[-1].split('.xml')[0]
                        if u_id in unit_list:
                            unpublished = True
                            self.draft_problems_struct[s].remove(u)
                    if self.draft_problems_struct[s]:
                        all_dict2 = self.describeDraftUnit(self.draft_problems_struct[s], readme, file_index, sequ_name)
                        for d in all_dict2:
                            all_dict[d] = all_dict2[d]
                

                all_seq['('+s_name[-9:-4]+')'+sequ_name] = (str(sFile), all_dict)

                if unpublished:
                    print('\033[93m Warning: There are unpublished changes in published problems under subsection {}. Only looking at published version.\033[0m'.format(sequ_name))

            else: #check draft
                if s not in self.draft_problems_struct.keys():
                    all_dict = OrderedDict()
                else:
                    all_dict = self.describeDraftUnit(self.draft_problems_struct[s], readme, file_index, sequ_name)
                all_seq['('+s_name[-9:-4]+')'+sequ_name] = (str(sFile), all_dict)
            
            tmp_seqDetails_list.append(self.seqDetails_dict)
        # frame_izquierdo.write('</ul>\n')
        # file_index.write('</ul>\n')
        self.tmp_dictionary['sections'] = tmp_seqDetails_list
        print(self.tmp_dictionary)
        print('\n')
        pub_seq = dict((k, v) for k, v in pub_seq.items() if v)
        return pub_seq, all_seq

    def describeUnit(self, uni, readme, file_index, sequ_name):
        # aux_sequ_name = self.eliminar_carateres_especiales(sequ_name).replace(' ','-')
        #print(uni)
        #print('\n\n')
        pub_uni = OrderedDict()
        all_uni = OrderedDict()
        number_sectionErrors = 0
        # direccion = ''
        for u in uni:
            u += '.xml'
            uFile = self.vert_path / u
            aux_uFile = '%s/%s'%(self.aux_vert_path, u)
            uni_txt = uFile.open().readlines()
            uFile = uFile.relative_to(*uFile.parts[:1])
            first_line = uni_txt[0]
            u_name = first_line.split('"')[1]
            readme.write('\t\t* [Unit] {0} - [{1}]({1})\n'.format(u_name, aux_uFile))
            aux_u_name = u_name
            # aux_u_name = self.eliminar_carateres_especiales(u_name.replace(' ','-'))
            #print(uni_txt[0])
            '''
            if (len(uni) > 1):
                file_index.write('<li>%s</li>\n'%u_name)
            else:
                file_index.write('<li>%s</li>\n'%sequ_name)
            '''
            ''''
            # Formar el submenu
            if (len(uni) > 1):
                if os.path.isdir('%s/course-html/content/%s/%s'%(str(self.path), path,u_name)):
                    self.num_units+=1
                    aux_u_name = '%s-%d'%(aux_u_name,self.num_units)
                    os.mkdir('%s/course-html/content/%s/%s/%s'%(str(self.path), path, self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower()
                        ,aux_u_name.lower()))
                else:
                    os.mkdir('%s/course-html/content/%s/%s/%s'%(str(self.path), path, self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower()
                        , aux_u_name.lower()))
                # frame_izquierdo.write('<li class="nav-item"><a class="nav-link" href="%s/%s/%s/%s.html" target="derecho">%s</a></li>\n'%(path,
                    # aux_sequ_name.lower(),aux_u_name.lower(),aux_u_name.lower(),u_name))
                # frame_derecho = open(str(self.path)+'/course-html/content/%s/%s/%s/%s.html'%(path,aux_sequ_name.lower(),aux_u_name.lower(),aux_u_name.lower()), 'w')
                direccion = str(self.path)+'/course-html/content/%s/%s/%s'%(path,aux_sequ_name.lower(),aux_u_name.lower())
                self.type_content = 1
            else:
                # frame_izquierdo.write('<li class="nav-item"><a class="nav-link" href="%s/%s/%s.html" target="derecho">%s</a></li>\n'%(path,aux_sequ_name.lower(),aux_u_name.lower(),sequ_name))
                if(self.num_pages == 0):
                    self.first_page = '%s%s/%s/%s.html'%(self.first_page,path,aux_sequ_name.lower(),aux_u_name.lower())
                    self.num_pages+=1
                # Crear los archivos.html en el directorio creado para cada section
                # frame_derecho = open(str(self.path)+'/course-html/content/%s/%s/%s.html'%(path,aux_sequ_name.lower(),aux_u_name.lower()), 'w')
                direccion = str(self.path)+'/course-html/content/%s/%s'%(path,aux_sequ_name.lower())
                self.type_content = 0
            #if(aux_u_name.lower() == 'encuesta de satisfacción'):
                #print("Es una encuesta")
            '''
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
                #elif '<discussion ' in l:
                #    prob = l.split('"')[1]
                #    comp_list.append(['discussion', prob])
            
            if(u_name.lower() != 'encuesta de satisfacción'):
                if not prob_list:
                    number_sectionErrors += 1
                    self.tmp_dictionary['total_errors'] += number_sectionErrors
                    self.number_emptyContent += 1
                    self.seqDetails_dict['total_errors'] += number_sectionErrors
            #print(prob_list)
            # print(u_name)
            pub_dict, all_dict = self.describeProb(prob_list, readme, file_index, aux_u_name.lower())
            pub_uni[u_name] = pub_dict
            all_uni['('+u[-9:-4]+')'+u_name] = (str(uFile), all_dict)
        pub_uni = dict((k, v) for k, v in pub_uni.items() if v)
        return pub_uni, all_uni

    def describeProb(self, prob_list, readme, file_index, name):
        '''
        print(prob_list)
        print(len(prob_list))
        print('\n\n')
        '''
        """
        Write component information into readme
        Input:
            [prob_list]: the list of problems to describe further
        """
        pub_prob = OrderedDict()
        pro_list = []

        pat1 = re.compile(r'<problem ([^>]+)>')
        pat2 = re.compile(r'(\S+)="([^"]+)"')
        num_files = 0
        aux_u_name = name
        number_errorsUrl = 0
        number_errorsVideo = 0
        # files_list = []
        # txt_prob = ''
        #file_idx_prob = open('%s/idx-%s.html'%(direccion,aux_u_name),'w')
        #file_idx_prob.write('<html>\n<body>\n')

        for pro in prob_list:
            if num_files > 0:
                aux_u_name = '%s-%d'%(name,num_files)
            # print('%s/%s.html'%(direccion,name))
            # frame_derecho = open('%s/%s.html'%(direccion,aux_u_name),'w')
            # files_list.append('%s/%s.html'%(direccion,aux_u_name))
            num_files +=1
            # Pendiente agregar condicion para ver si es un video o un html.
            if pro[0] == 'html': # Condicion para ver si el archivo es un html
                # txt_prob = '%s<a class="btn btn-outline-dark border-0 col-auto" href="%s.html" data-toggle="button" aria-pressed="false" autocomplete="off">Page</a>\n'%(txt_prob, aux_u_name)
                #'<a href="#" class="btn btn-primary btn-lg active" role="button" aria-pressed="true">Primary link</a>'
                #'data-toggle="button" aria-pressed="false" autocomplete="off"'
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
                #print(m)
                if m:
                    params = m.group(1)
                    m2 = pat2.findall(params)
                    Dict= {key:val for key,val in m2 if key!='markdown'}
                    p_name = Dict['display_name']
                    if 'weight' in Dict.keys():
                        weight = Dict['weight']
                        if 'max_attempts' in Dict.keys():
                            max_att = Dict['max_attempts']
                            pub_prob[p_name] = {'file':pro_name, 'weight':Dict['weight'], 'max_attempts':Dict['max_attempts']}
                        else:
                            pub_prob[p_name] = {'file':pro_name, 'weight':Dict['weight']}
                    #print('\t\t\t* [{0}] {1} - [{2}]({2})\n'.format(pro[0], p_name, aux_pFile))
                    readme.write('\t\t\t* [{0}] {1} - [{2}]({2})\n'.format(pro[0], p_name, aux_pFile))
                    #readme.write('\t\t\t\t Weight: {0}, Max Attempts: {1}\n'.format(weight, max_att))
                else:

                    number_seqErrorsUrl = 0
                    
                    criterion_dictionary = self.checkUrls(file_adress)
                    if criterion_dictionary['urls']:
                        number_errorsUrl = self.getNumberErrors(criterion_dictionary)
                        number_seqErrorsUrl = number_errorsUrl
                        self.number_urlErrors += number_errorsUrl
                    
                    self.seqDetails_dict['total_errors'] +=  number_seqErrorsUrl
                    

                    readme.write('\t\t\t* [{0}] - [{1}]({1})\n'.format(pro[0], aux_pFile))
                    #print(str(p_txt_html))
                    '''
                    for text in p_txt_html:
                        for line in text.split('\n'):
                            if 'http' not in line:
                                line = line.replace('_','-')
                            if self.type_content == 0:
                                frame_derecho.write('%s\n'%line.replace('/static/','../../../static/'))
                            else:
                                frame_derecho.write('%s\n'%line.replace('/static/','../../../../static/'))
                    frame_derecho.close()
                    '''
                
                pro_list.append((str(pFile), pro[0]))
            elif pro[0] == 'video':
                # print('Ok')
                pro_name = pro[1]+'.xml'
                pFile = self.path / pro[0] / pro_name
                file_adress = self.path / pro[0] / pro_name
                
                number_seqErrorsVideo = 0
                
                if not self.checkVideos(file_adress):
                    number_errorsVideo += 1
                    number_seqErrorsVideo += 1
                    self.number_videoErrors += 1

                self.seqDetails_dict['total_errors'] += number_seqErrorsVideo
                
                '''
                frame_derecho.write('<h4>VIDEO: %s</h4>\n<iframe class=»youtube-player» type=»text/html» width=»846″ height=»484″ src=%s ' 
                    'frameborder=»0″></iframe>\n'%(self.obtener_titulo_video().upper(),video_title))
                # frame_derecho.write('<iframe class=»youtube-player» type=»text/html» width=»846″ height=»484″ src=%s ' 
                    # 'frameborder=»0″></iframe>\n'%video_title)
                txt_prob = '%s<a class="btn btn-outline-dark border-0 col-auto" href="%s.html" data-toggle="button" aria-pressed="false" autocomplete="off">Video</a>\n'%(txt_prob, aux_u_name)
                frame_derecho.close()
                '''
            elif pro[0] == 'problem':
                letters = list(range(97,123))
                pro_name = pro[1]+'.xml'
                pFile = self.path / pro[0] / pro_name
                txt_problem = pFile.open().readlines()
                txt_problem = txt_problem[1:]
                txt_problem = txt_problem[:-1]
                type_question = ''
                num_groups = 0
                name = ''
                '''
                for line in txt_problem:
                    if '<choicegroup' in line:
                        type_question = 'radio'
                        num_groups+=1
                        name = 'name%d'%(num_groups)
                    elif '<checkboxgroup' in line:
                        type_question = 'checkbox'
                    elif ('multiplechoiceresponse' not in line) and ('choicegroup' not in line) and ('checkboxgroup' not in line) and ('choiceresponse' not in line):
                        if type_question == 'radio':
                            line = line.replace('    <choice','&nbsp;&nbsp;&nbsp;&nbsp;<input type="%s" name="%s"'%(type_question,name))
                        else:
                            line = line.replace('    <choice','&nbsp;&nbsp;&nbsp;&nbsp;<label><input type="%s"'%(type_question))
                        line = line.replace('correct','value')
                        line = line.replace('</choice>','</label><br>')
                        line = line.replace('</html>','</html><br>')
                        line = line.replace('<p>','<br>\n<p>')
                        frame_derecho.write(line.replace('/static/','../../../../static/'))
                '''
                '''
                num_answers = 0
                for line in txt_problem:
                    if ('multiplechoiceresponse' not in line) and ('choicegroup' not in line) and ('checkboxgroup' not in line) and ('choiceresponse' not in line):
                        line = line.replace('<p>','<br><p>')
                        if '    <choice' in line:
                            style_option = '%s.'%chr(letters[num_answers])
                            style_option2 = '%s)'%chr(letters[num_answers])
                            if((style_option in line) or (style_option2 in line)):
                                line = line.replace(style_option,'')
                                line = line.replace(style_option2,'')
                            line = line.replace('    <choice','<p>&nbsp;&nbsp;&nbsp;&nbsp;%s) '%chr(letters[num_answers]))
                            num_answers += 1
                        else:
                            num_answers = 0
                        line = line.replace('correct="false">','')
                        line = line.replace('correct="true">','')
                        line = line.replace('</choice>','</p>')
                        line = line.replace('</html>','</html><br>')
                        frame_derecho.write(line.replace('/static/','../../../static/'))
                    
                txt_prob = '%s<a class="btn btn-outline-dark border-0 col-auto" href="%s.html" data-toggle="button" aria-pressed="false" autocomplete="off">Problem</a>\n'%(txt_prob, aux_u_name)
                frame_derecho.close()
                '''
        '''
        if aux_u_name.lower() == 'encuesta-de-satisfaccion':
            frame_derecho = open('%s/%s.html'%(direccion,aux_u_name),'w')
            frame_derecho.write('<iframe style="width:%s; height:%s;" '
                'src="https://docs.google.com/forms/d/e/1FAIpQLSeyvQFO-e-VDuuL0TMFTYrIwdVr73UyZ7IGGdgMMXaMYITo9g/viewform"></iframe>'%('100%', '100%'))
            frame_derecho.close()
        '''
        '''
        for name_file in files_list:
            file = open(name_file,'r')
            file_lines = file.readlines()
            txt_file = ''
            for line in file_lines:
                txt_file += line
            file = open(name_file,'w')
            file.write('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" '
                'integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">\n'
                '<style type="text/css">\n.botones{\nborder-radius: 23px;\n}\n</style>\n'
                '<div class ="container">\n<div class="row justify-content-center">\n'
                '<div class="btn-group btn-group-lg col-6 p-0 my-4 border border-dark botones" role="group" aria-label="Toolbar with button groups">\n'
                '%s</div><br><br>\n</div>\n%s'
                '<script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>\n'
                '<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>\n'
                '<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>'%(txt_prob, txt_file))
            file.close()
        '''
        
        if number_errorsUrl > 0:
            self.tmp_dictionary['total_errors'] += number_errorsUrl
        if number_errorsVideo > 0:
            self.tmp_dictionary['total_errors'] += number_errorsVideo
        
        # self.reescribir_archivos(files_list, txt_prob)
        return pub_prob, pro_list

    # Obtener informacion de unidades
    def describeDraftUnit(self, unit, readme, file_index, sequ_name):
        # aux_sequ_name = self.eliminar_carateres_especiales(sequ_name).replace(' ','-')
        all_uni = OrderedDict()
        # files_list = []
        # direccion = ''
        for u in unit:
            uFile = Path(u[0])
            aux_uFile = u[0].split('/')
            aux_uFile = '%s/%s/%s'%(aux_uFile[-3],aux_uFile[-2],aux_uFile[-1])
            first_line = uFile.open().readlines()[0]
            uFile = uFile.relative_to(*uFile.parts[:1])
            u_name = first_line.split('"')[1]
            aux_u_name = u_name
            # aux_u_name = self.eliminar_carateres_especiales(u_name.replace(' ','-'))
            '''
            if os.path.isdir('%s/course-html/content/%s/%s/%s'%(str(self.path), path, self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower()
                ,aux_u_name.lower())):
                self.num_drafts+=1
                aux_u_name = '%s-%d'%(aux_u_name,self.num_drafts)
            
            os.mkdir('%s/course-html/content/%s/%s/%s'%(str(self.path), path, self.eliminar_carateres_especiales(sequ_name).replace(' ','-').lower()
                , aux_u_name.lower()))
        
            frame_izquierdo.write('<li class="nav-item"><a class="nav-link" href="%s/%s/%s/%s.html" target="derecho">%s</a></li>\n'%(path,aux_sequ_name.lower(),
                aux_u_name.lower(),aux_u_name.lower(),u_name))
            '''

            # direccion = str(self.path)+'/course-html/content/%s/%s/%s'%(path,aux_sequ_name.lower(),aux_u_name.lower())
            # frame_derecho = open(str(self.path)+'/course-html/content/%s/%s/%s/%s.html'%(path,aux_sequ_name.lower(),aux_u_name.lower(),aux_u_name.lower()), 'w')
            # files_list.append(str(self.path)+'/course-html/content/%s/%s/%s/%s.html'%(path,aux_sequ_name.lower(),aux_u_name.lower(),aux_u_name.lower()))
            # files_list.append(str(self.path)+'/course-html/content/%s/%s/%s/%s.html'%(path,aux_sequ_name.lower(),aux_u_name.lower(),aux_u_name.lower()))
            # file_index.write('<li>%s</li>\n'%u_name)
            readme.write('\t\t* [Unit]\(Draft\) {0} - [{1}]({1})\n'.format(u_name, aux_uFile))
            prob_list = self.describeDraftProb(u[1:], readme, aux_u_name.lower())
            # frame_derecho.close()
            all_uni['('+u[0][-9:-4]+')(draft)'+u_name] = (str(uFile), prob_list)
        return all_uni

    
    def describeDraftProb(self, probs, readme, aux_u_name):
        # print(aux_u_name)
        prob_list = []
        # print(probs)
        # print('\n\n')
        txt_prob = ''
        # files_list = []
        num_drafts_prob = 0
        number_errorsUrl = 0
        #print(probs)
        #print(files_list)
        #print('\n\n')
        tmp_aux_u_name = aux_u_name
        for pro in probs:
            if num_drafts_prob > 0:
                aux_u_name = '%s-%d'%(tmp_aux_u_name,num_drafts_prob)
            num_drafts_prob+=1
            # frame_derecho = open('%s/%s.html'%(direccion,aux_u_name),'w')
            # files_list.append('%s/%s.html'%(direccion,aux_u_name))
            #txt_prob = '%s<a class="btn btn-outline-dark border-0 col-4" href="%s.html" data-toggle="button" aria-pressed="false" autocomplete="off">Page</a>\n'%(txt_prob, aux_u_name)
            pro_name = pro[1]+'.xml'
            pro_name_html = pro[1]+'.html'
            pFile = self.draft_path / pro[0] / pro_name
            aux_pFile = '%s/%s/%s'%(self.aux_draft_path,pro[0],pro_name_html)
            
            pFile_html = self.draft_path / pro[0] / pro_name_html
            
            # Variable nueva
            file_adress = self.draft_path / pro[0] / pro_name_html # direccion del archivo
            
            p_txt = pFile.open().readlines()

            p_txt_html = pFile_html.open().readlines()
    
            pFile = pFile.relative_to(*pFile.parts[:1])
            fline = p_txt[0]
            p_name = fline.split('"')[1]
           
            if pro[0] == 'problem':
                readme.write('\t\t\t* [{0}]\(Draft\) {1} - [{2}]({2})\n'.format(pro[0], p_name, aux_pFile))
            else:
                number_seqErrorsUrl = 0
                
                criterion_dictionary = self.checkUrls(file_adress)
                if criterion_dictionary['urls']:
                    number_errorsUrl = self.getNumberErrors(criterion_dictionary)
                    number_seqErrorsUrl = number_errorsUrl
                    self.number_urlErrors += number_errorsUrl
                
                self.seqDetails_dict['total_errors'] +=  number_seqErrorsUrl
    
                readme.write('\t\t\t* [{0}]\(Draft\) - [{1}]({1})\n'.format(pro[0], aux_pFile))
                '''
                txt_prob = '%s<a class="btn btn-outline-dark border-0 col-auto" href="%s.html" data-toggle="button" aria-pressed="false" autocomplete="off">Page</a>\n'%(txt_prob, aux_u_name)
                for text in p_txt_html:
                    for line in text.split('\n'):
                        frame_derecho.write('%s\n'%line.replace('/static/','../../../../static/'))
                '''
            # frame_derecho.close()
            prob_list.append((str(pFile), '(draft)'+pro[0]))
        if number_errorsUrl > 0:
            self.tmp_dictionary['total_errors'] += self.tmp_dictionary['total_errors'] + number_errorsUrl
        # self.reescribir_archivos(files_list, txt_prob)
        return prob_list


if __name__ == "__main__":

    if len(sys.argv) != 2:
        pass
    else:
        folder_name = sys.argv[1]
        os.getcwd()
    writeDoc = Doc(os.getcwd())
    writeDoc.describeCourse()
 


