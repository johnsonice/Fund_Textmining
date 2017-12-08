# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 10:39:26 2017

@author: chuang
"""
import shutil 
import os 
#import glob
from bs4 import BeautifulSoup
import csv
import pickle
import re
from collections import Counter
import pandas as pd


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

class text_document(object):
    def __init__(self,file_id,txt_path):
        #print('initiate doc object')
        self.file_id = file_id
        self.txt_path = txt_path
        self.paras = self.load_txt()
        self.meta = {}
    
    def load_txt(self):
        return  self.extract_txt_paras()
    
    def check_useless(self,delete_words,target):
        """
        Check if useless word are in the sentance, if yes 
        return False 
        else return true 
        """
        for w in delete_words:
            if w in target:
                return False
        return True
    
    def extract_txt_paras(self):
        with open(self.txt_path,'r',encoding='utf-8') as f:
            lines = f.readlines()
            lines = [x.split('\t')[1].strip('\n') for x in lines]
        
        
        delete_words = ['____','DOCUMENT OF INTERNATIONAL MONETARY FUND','Download Date']
        #replace_regex = re.compile(r'\uf0b7|\x0c')
        number_regex = re.compile(r'\d+?\.\d+|\.\d+|\d+-\d+|\d+/\d+|\d+/|-\d+|\d+|½|¼|¼|⅔|¾/')   
        
        clean_para= list()
        for line in lines:
            if self.check_useless(delete_words,line):
                line = number_regex.sub(' ',line)
                line = re.sub(r'\(.*?\d+.*?\)|\s\s+|\d/',' ',line)  # clean up things like '(box 1)' and  '    '
                tokens = line.split()
                if len(tokens)>15:                                  # only keep paragraphs that is long enough
                    clean_para.append(line)
        
        return clean_para


def construct_rex(keywords):
    r_keywords = [r'\b' + re.escape(k) + r'(s|es)?\b'for k in keywords]    # tronsform keyWords list to a patten list, find both s and es 
    rex = re.compile('|'.join(r_keywords),flags=re.I)                        # use or to join all of them, ignore casing
    #match = [(m.start(),m.group()) for m in rex.finditer(content)]          # get the position and the word
    return rex

def find_exact_keywords(content,keywords,rex=None):
    if rex is None: 
        rex = construct_rex(keywords)
    content = content.replace('\n', '').replace('\r', '')#.replace('.',' .')
    match = Counter([m.group() for m in rex.finditer(content)])             # get all instances of matched words 
                                                                             # and turned them into a counter object, to see frequencies
                                                                             # group 1, only return the fist element 
    return match

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

def read_meta(file):
    """
    file: csv file with meta data for file ids 
    return: a list of ids, a matrix of all metadatafile 
    """
    with open(file,'r') as f:
        reader = csv.reader(f)
        meta = list(reader)
        ids = [row[3] for row in meta ][1:]
    return ids,meta

def read_ids(file):
    """
    file: csv file with file ids 
    return: a list of ids
    """
    with open(file,'r') as f:
        reader = csv.reader(f)
        ids = list(reader)
    return ids