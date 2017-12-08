# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 09:00:39 2017

@author: chuang

data utility functions 
"""
from urllib.request import urlretrieve
import os
from os.path import isfile, isdir
from tqdm import tqdm
import zipfile
from bs4 import BeautifulSoup

#%%

## download xml function
def download_data(download_path,download_link,extract_path):
    class DLProgress(tqdm):
        last_block = 0

        def hook(self, block_num=1, block_size=1, total_size=None):
            self.total = total_size
            self.update((block_num - self.last_block) * block_size)
            self.last_block = block_num
        
    with DLProgress(unit='B', unit_scale=True, miniters=1, desc='article iv') as pbar:
        urlretrieve(download_link,download_path,pbar.hook)
            
    zip_ref = zipfile.ZipFile(download_path, 'r')
    zip_ref.extractall(extract_path)
    zip_ref.close()

    os.remove(download_path)
    
## make directory function
def maybe_create(path):
    if isdir(path):
        print("folder already exist")
    else:
        os.mkdir(path)
        print("data folder created")
        
## create a document object to hold xml files 
class document(object):
    def __init__(self,series_id,file_id,xml_path):
        #print('initiate doc object')
        self.file_id = file_id
        self.series_id = series_id
        self.xml_path = xml_path
        self.paras = self.load_xml()
        self.meta = {}

    def load_xml(self):
        return  self.extract_xml_paras()

    def clean_fig_table(self,soup):
        for tag in soup.body.find_all(['fig','table-wrap']):
            tag.decompose()
        ## group list points together in one paragraph
        for li in soup.body.find_all('list'):
            s = [t.get_text() for t in li.find_all('list-item')]
            s = ' '.join(s)
            tag = soup.new_tag('p')
            tag.string = s    
            li.replaceWith(tag)
        
        return soup 

    def extract_xml_paras(self):
        with open(self.xml_path,'r',encoding='utf8') as f:
            soup = BeautifulSoup(f, 'xml')
        try:
            soup = self.clean_fig_table(soup)
            p_list = soup.body.find_all('p')
            ## check see if documents are structure in this way 
            if len(p_list) ==0 : 
                print('no paragraph found: {}'.format(self.file_id))
                return p_list 
        except:
            print('file corropted: {}'.format(self.file_id))
            return []
        
        p_list =  [ele.get_text().replace('\n',' ') for ele in p_list]
        
        return p_list

def get_ids(xml):
    """
    input xml full name, return series id and file id 
    """
    series_id,xml_name = xml.split('-')
    file_id,_ = xml_name.split('_') 
    return series_id,file_id

def read_keywords(file):
    """
    file: csv file with keyword list
    """
    with open(file,'r') as f:
        reader = csv.reader(f)
        mylist = list(reader)
    return mylist







