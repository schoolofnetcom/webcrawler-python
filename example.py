import string
import os
import urllib2
import MySQLdb

from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('latin-1')

if os.path.exists('errorLog.txt'):
    os.remove('errorLog.txt')

errorLog = open('errorLog.txt', 'w')

link_base = "http://www9.prefeitura.sp.gov.br"
link_pag = link_base + "/secretarias/smads/estouaqui/pessoas/todos/page:"

headers = {}
headers['User-Agent'] = 'GoogleBot'

def run(link):
    if link is None:
        return
    
    for i in range(1, 11):
    
        soup = get_html(link_pag + str(i))

        if soup is None:
            return

        people_list = soup.find(attrs={"id": "lista_pessoas"})

        for people in people_list.findAll(attrs={"class": "pessoa"}):
            if people is None:
                continue
        
            people_data = people.find(attrs={"class": "pessoa_dados"})

            if people_data is None:
                return
    
            name = people_data.h3.a.text
            link = people_data.h3.a.get("href")

            get_data_child(link_base + link)


def get_data_child(link):
    soup = get_html(link)

    if soup is None:
        return
    
    data = soup.find(attrs={"id": "conteudo"})

    name = data.h2.text
    address = ""
    district = ""
    phone = ""
    email = ""

    conn = connecDB()
    conn.autocommit(False)
    cursor = conn.cursor()

    count = 1
    insert = "INSERT INTO pessoa (nome, endereco, telefone, email) VALUES ('%s', '%s', '%s', '%s')"

    for p in data.find(attrs={"class": "entidade_dados"}).findAll("p"):
        
        if count == 1:
            address = p.text
        elif count == 2:
            district = p.text
        elif count == 3:
            phone = p.text
        elif count == 5:
            email = p.text

        count += 1
            
    insert %= (name, address, phone, email)
    cursor.execute(insert)
    conn.commit()

    print name

def connecDB():
    return MySQLdb.connect(host="localhost", user="root", passwd="", db="webcrawler")


def get_html(link):
    request = urllib2.Request(link, headers=headers)
    return BeautifulSoup(urllib2.urlopen(request), "html.parser")


if __name__ == "__main__":
    run(link_base + '/secretarias/smads/estouaqui/pessoas/todos')
