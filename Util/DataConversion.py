# Util\DataConversion.py
#
# Copyright 2010 Friendzy Shop LLC

#from django.utils import simplejson as json
import json


def join_us_address_fields(csv_dic, new_field):
    """Join US address components in a dictionary to make a single dictionary entry.

       Specific key names are required for the address components.
    """
    address_str = '%s, %s, %s %s' %  (
                      csv_dic['Street Address'],
                      csv_dic['City'],
                      csv_dic['State'],
                      csv_dic['ZIP'])                         
        
    dic = csv_dic
    dic[new_field] = address_str
    del(dic['Street Address'])
    del(dic['City'])
    del(dic['State'])
    del(dic['ZIP'])
    
    return dic

def filter_dic_by_keys(dic,allowed_keys):
    """Filter dictionary dic by allowed_keys list.

    Any item in dic with a key that is not in the allowed_keys is removed,
    """
    new_dic = {}
    for key in dic:
        if key in allowed_keys:
            new_dic[key] = dic[key]
    return new_dic

def filter_dic_by_key_prefix(dic,key_prefix_list):
    """Filter out any dictionary dic items by key_prefix_list.

    Any item with a key that begins with a prefix in the list is deleted.
    """
    new_dic = {}
    for key in dic:
        retain = True
        for prefix in key_prefix_list:
            if key.startswith(prefix):
                retain = False
        if retain:
            new_dic[key] = dic[key]
    return new_dic

def filter_dic_by_key_content(dic,key_content,ignore_case):
    """Filter out any dictionary dic items strings in key_content_list.

    Any item with a key that contains an item in the list is deleted.
    """
    if ignore_case:
        contentCheck = key_content.upper()
    else:
        contentCheck = key_content

    new_dic = {}
    for key in dic:

        if ignore_case:
            noRetainCheckKey = key.upper()
        else:
            noRetainCheckKey = key

        if noRetainCheckKey.find(contentCheck) == -1:
            new_dic[key] = dic[key]

    return new_dic

def dict_to_json(dic):
    """Convert a dictionary dic to a JSON formatted string."""
    return json.dumps(dic)

def json_to_dict(json_str):
    """Convert a JSON formatted string to a dictionary."""
    if json_str == "":
        return ""
    elif json_str.startswith('Not found error'):
        return ""
    return json.loads(json_str)
