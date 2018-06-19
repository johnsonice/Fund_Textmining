# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 18:55:37 2017

@author: HNguyen5
"""

from bs4 import BeautifulSoup

class document_db:
    def __init__(self, xml):
        #print('initiate doc object')
        self.print_id = xml.PrintIsbn
        self.PublisherId = xml.PublisherId
        self.series_id = xml.SeriesNumber
        self.country = xml.Country
        self.PublicationDate = xml.PublicationDate
        self.ProjectedYear = xml.ProjectedYear
        self.PageCount = xml.PageCount
        self.content = xml.Content
        self.paras = self.load_xml()

    def load_xml(self):
        return  self.extract_xml_paras()

    def clean_fig_table(self,soup):  
        '''
        Uncomment the following 2 line of code if you want to 
        delete tables and figures to prevent picking up headers and footnotes
        Please note that this will also delete text tables.
        
        '''
        #for tag in soup.body.find_all(['fig','table-wrap']):
            #tag.decompose()    
       
        ## group list points together in one paragraph
        if len(soup.body.find_all('list'))>0:
            for li in soup.body.find_all('list'):
                s = [t.get_text() for t in li.find_all('list-item')]
                s = ' '.join(s)
                tag = soup.new_tag('p')
                tag.string = s    
                li.replaceWith(tag)
        
        return soup 

    def extract_xml_paras(self):
        soup = BeautifulSoup(self.content, 'xml')
        try:
            soup = self.clean_fig_table(soup)
            p_list = soup.body.find_all('p')
            ## check see if documents are structure in this way 
            if len(p_list) ==0 : 
                print('no paragraph found: {}'.format(self.PublisherId))
                return p_list 
        except:
            print('file corrupted: {}'.format(self.PublisherId))
            return []
        
        p_list =  [ele.get_text().replace('\n',' ') for ele in p_list]
        
        return p_list
