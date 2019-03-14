# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 16:39:55 2017

@author: chuang
"""

## Get sentiment from paragraphs 
import os 
os.chdir('d:/usr-profiles/chuang/Desktop/Dev/textmining/2_imf_docs/1_use_xmls/process_search_docs')
import pandas as pd
#import csv 
from util import read_keywords,find_exact_keywords,construct_rex
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.stem import WordNetLemmatizer
import copy

#%%

## Merge both xml and txt pd together ##
def combine_df(xml_results,txt_results):
    """
    Pass in xml and txt result files 
    return combined and clearned df 
    """
    df_xml = pd.read_csv(xml_results)
    df_txt = pd.read_csv(txt_results)
    df = pd.concat([df_xml,df_txt],ignore_index=True)               ## append dataframes together 
    df_headers = df.columns.values.tolist()
    df_headers.remove('Unnamed: 0')                                 ## delete the first column 
    meta_list = ['doc_id','para_id','context','para_word_count']
    var_list = [v for v in df_headers if v not in meta_list ]
    ordered_vars =meta_list + var_list
    
    ## check for duplicates 
    assert len(ordered_vars) == len(set(ordered_vars)), 'duplicate in var names'    ## should return Ture
    df = df[ordered_vars]                   ## clean dataframe with both txt and xml 
    
    return df 

## Load sentiment keywords ##############
def get_sent_keys(sentiment_path):
    """
    pass in pos and neg keywords list 
    """
    sent_list = read_keywords(sentiment_path)
    pos_list = [p[0] for p in sent_list[1:] if len(p[0])>0]
    neg_list = [p[1] for p in sent_list[1:] if len(p[1])>0]
    return pos_list, neg_list

## tokenize lementize and remove stop words
def _process_text(text,stopw,lemmatizer):
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    tokens = [t for t in tokens if t not in stopw]
    return tokens

def check_negation(negation_check,negations):
    res = [t for t in negation_check if t in negations]
    if len(res)> 0 :
        return True
    else:
        return False
    
def get_negation_check(tokens,idx,ran=3):
    t_len = len(tokens)
    nidx = [idx-ran,idx+ran]
    if nidx[0]<0:nidx[0] = 0 
    if nidx[1]> t_len+1:nidx[0] = t_len+1
    negation_check = tokens[nidx[0]:nidx[1]] 
    return negation_check
    
def get_pos_count(text,pos_list,neg_list,negations,stopw,lemmatizer,search_keys,search_rex,by='sent'):
    
    if by == 'sent':
        sentences = sent_tokenize(text)
        s_list = [s for s in sentences if len(find_exact_keywords(s,search_keys,rex))>0]
        reduced_para = ' '.join(s_list)
        if len(reduced_para)==0: return 0,0,0,''
        text = reduced_para

    tokens = _process_text(text,stopw,lemmatizer)
    total_words = len(tokens)
    pos = 0 
    neg = 0 
    for idx,t in enumerate(tokens):
        if t in pos_list:
            negation_check = get_negation_check(tokens,idx,3)
            if check_negation(negation_check,negations):
                neg+=1 
            else:
                pos+=1 
        
        elif t in neg_list:
            negation_check = get_negation_check(tokens,idx,3)
            if check_negation(negation_check,negations):
                pos+=1 
            else:
                neg+=1 
            
    return pos,neg,total_words,text
    
#%%
xml_results = 'data/xml_results.csv'
txt_results = 'data/txt_results.csv'
sentiment_path = 'sentiment_words_modified.csv'
negations = ['not','no','nobody','nobody','none','never','neither','cannot',"can't"]
stopw = stopwords.words('english')
stopw = [s for s in stopw if s not in negations]
lemmatizer = WordNetLemmatizer()

df = combine_df(xml_results,txt_results)
pos_list, neg_list = get_sent_keys(sentiment_path)
search_keys = copy.deepcopy(df.columns.values.tolist())[4:]
rex = construct_rex(search_keys)

#%%
# test
#test = df['context'][:10].apply(get_pos_count,args=(pos_list,neg_list,negations,stopw,lemmatizer,search_keys,rex))

#%%
df['sentiment'] = df['context'].apply(get_pos_count,args=(pos_list,neg_list,negations,stopw,lemmatizer,search_keys,rex))
df[['sentiment_pos','sentiment_neg','total_words_no_stop','reduced_context']] = df['sentiment'].apply(pd.Series) 
#%%
df_headers = df.columns.values.tolist()
meta_list = ['doc_id','para_id','context','reduced_context','para_word_count','sentiment_pos','sentiment_neg','total_words_no_stop']
var_list = [v for v in df_headers if v not in meta_list ]
var_list.remove('sentiment')
ordered_var_list = meta_list + var_list
df = df[ordered_var_list]
df.to_csv('data/sentiment.csv',encoding='utf-8')

