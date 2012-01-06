# HttpInterface\HttpInterface.py

import httplib

def post_data(host_and_port,page,action,json_content):
    """Post data to a web page. """
    headers = {"Content-Type": "text/html", "Accept": "text/plain"}

    connection = httplib.HTTPConnection(host_and_port)
    urlString = '/{0:>s}?action={1:>s}'.format(page, action)
    connection.request("POST",urlString,json_content,headers)
    
    r1 = connection.getresponse()
    
    # print "POST Status:",r1.status, "\nReason:",r1.reason,"\nMsg:",r1.msg
    connection.close()

def get_data(host_and_port,page,action,json_content):
    """Post data to a web page. """
    headers = {"Content-Type": "text/html", "Accept": "text/plain"}
    connection = httplib.HTTPConnection(host_and_port)
    urlString = '/{0:>s}?action={1:>s}'.format(page, action)
    #connection.request("GET",urlString,json_content,headers)
    connection.request("POST",urlString,json_content,headers)

    r1 = connection.getresponse()

    # print "GET Status:",r1.status, "\nReason:",r1.reason,"\nMsg:",r1.msg,"URL string:",urlString

    res = r1.read()
    return res
    connection.close()

def del_data(host_and_port,page,action,json_content):
    """Post data to a web page. """
    headers = {"Content-Type": "text/html", "Accept": "text/plain"}

    connection = httplib.HTTPConnection(host_and_port)
    urlString = '/{0:>s}?action={1:>s}'.format(page, action)
    connection.request("DELETE",urlString,json_content,headers)

    r1 = connection.getresponse()

    # print "GET Status:",r1.status, "\nReason:",r1.reason,"\nMsg:",r1.msg

    res = r1.read()
    return res
    connection.close()

