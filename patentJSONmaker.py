 
import json 
import urllib
import string
import re
from bs4 import BeautifulSoup


class MyOpener(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'
 

def isNumber(s):    #helper function
    try:
        float(s)
        return True
    except ValueError:
        return False

def contains_digits(d):	#helper function
    _digits = re.compile('\d')
    return bool(_digits.search(d))

def getSoup(url):   #converts html into navigable nested data structure
    myopener = MyOpener()
    page = myopener.open(url)
    text = page.read()
    text = ''.join(s for s in text if s in string.printable)
    page.close()
    soup = BeautifulSoup(text)
    return soup

def getClassNumberAndName(key, data, soup):    #obtains every class number and name, placing them in a dictionary
    value = ""
    dataStart = False
    for line in soup.findAll(['big']):
        if not line == None:
            line = line.string
            tokens = line.split()
            for token in tokens:
                if dataStart :
                    value = value + " " + token
                if isNumber(token) or (token.startswith('D') and contains_digits(token)) or token == 'G9B' or token == 'PLT':
                    dataStart = True              
    data[key] = [value.strip()]                   
    return data, key

def getSections(soup, data, num):   #Obtains everything up until the subclass references
    
    #First obtains the class definition and adds it to data 
    parsing = False
    term = ""
    for line in soup.findAll('p'):
        text = line.string
        if not text == None:
            if text.startswith("SECTION") or text.startswith("SUBCLASSES") :
                parsing = False 
            if parsing:
                term = term + " " + text
            if text.startswith("SECTION I - CLASS DEFINITION"):
                parsing = True
    term = term.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ').strip()      
    data[num].append(term)
    
    
    #Obtains any NOTES and adds it to data 
    term = ""        
    for line in soup.findAll('font'):
        text = line.string
        if not text == None:
            if text.startswith("SECTION") or text.startswith("SUBCLASSES") :
                parsing = False 
            if parsing:
                term = term + " " + text
            if "NOTES TO THE CLASS DEFINITION" in text:
                parsing = True
    term = term.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ').strip()           
    data[num].append(term)
    

    #Obtains the LINES WITH OTHER CLASSES AND WITHIN THIS CLASS and adds it to data 
    term = ""        
    for line in soup.findAll('p'):
        text = line.string
        if not text == None:
            if text.startswith("SECTION")or text.startswith("SUBCLASSES") :
                parsing = False 
            if parsing:
                term = term + " " + text
            if "LINES WITH OTHER CLASSES AND WITHIN THIS CLASS" in text:
                parsing = True
    term = term.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ').strip()           
    data[num].append(term)
    
    
    #Obtains subclass references
    subClassReferences = {} 
    flag = False     
    for line in soup.findAll('b'):
        text = line.string
        if not text == None:
            if "SUBCLASS REFERENCES TO THE CURRENT CLASS" in text:
                line = line.findNext('tr')
                while line:
                    a = line.findNext('td')
                    key = a.findNext('a')
                    b = a.findNext('td')
                    value = b.findNext('font')
                    valueString = ""
                    while not value.name == 'tr' and not value.name == 'p':
                        if not value.string == None and not value.name == 'a':
                            valueString = valueString + " " + value.string
                        value = value.findNext()
                    valueString = valueString.replace('\n', ' ').replace('\r', ' ').replace(u'\xa0', '').replace('  ', ' ').strip()  
                    subClassReferences[key.string] = valueString
                    line = line.findNextSibling('tr')
                data[num].append(subClassReferences)
                flag = True
    if not flag:
        data[num].append(subClassReferences) 



    #Obtains class references   
    classReferences = {}   
    for line in soup.findAll('b'):
        text = line.string
        if not text == None:
            if "REFERENCES TO OTHER CLASSES" in text:
                line = line.findNext('tr')
                while line:
                    a = line.findNext('td')
                    key = a.findNext('a')

                    b = a.findNext('td')
                    value = b.findNext('font').findNext('font')
                    valueString = ""
                    while not value.name == 'tr' and not value.name == 'p':
                        if not value.string == None and not value.name == 'a':
                            valueString = valueString + " " + value.string
                        value = value.findNext()
                    valueString = valueString.replace('\n', ' ').replace('\r', ' ').replace(u'\xa0', '').replace('  ', ' ').strip()      
                    classReferences[key.string] = valueString
                    line = line.findNextSibling('tr')
#                 data[num].append(classReferences)
    if classReferences:
        data[num].append(classReferences) 
    else:
#         classReferences['empty']='terry2' 
        data[num].append(classReferences)
                
    #Obtains glossary   
    glossary = {}       
    for line in soup.findAll(['p','b']):
        text = line.string
        if not text == None:
            if text.startswith("SUBCLASSES"):
                parsing = False 
            if parsing:
                if not "GLOSSARY" in text:
                    if line.name == 'b' and line.findNext('p'):
                        z = line.findNext('p')
                        z = z.string
                        if z:
                            glossary[text] = z.replace("\n",' ').replace('\r','')
            if "GLOSSARY" in text:
                parsing = True
    data[num].append(glossary) 
    return data 

def getSubClassesMain(soup, data, classNum):    #Obtains all the subclass info for each class
    table = {}
    a = soup.findAll(lambda tag: tag.name == 'a' and tag.findParent('font') and tag.findParent('font').findParent('td') )
   
    for parent in a:
        if parent :  
            
            #Obtains the subClass Number, subClass Name, subClass Parent, and subClass Definition
            temp = parent.attrs['href']
            if '#' in temp and 'sched' not in temp and 'htm' not in temp:
                subClassTitle = parent.findPrevious('b')
                subClassNo = subClassTitle.findPrevious('a')
                if subClassNo.string == subClassTitle.string:
                    subClassNo = subClassNo.findPrevious('a')
                subClassDef = parent.findNext('font')
                subClassDefS = subClassDef.string
                if not subClassDefS == None:
                    subClassDefS = subClassDefS.replace("\n", " ").replace("\r", " ").replace("  "," ") 
                
                #Obtains any Notes that are present
                notes = []
                x = subClassDef.findNext()
                while x.name == 'table':
                    y = x.findNext('font')
                    while not y == None:
                        z = y.string
                        if z:
                            z= z.replace("\n"," ")
                            z= z.replace("\r"," ")
                            z = z.replace("  ", " ")
                            if not z.startswith('('):
                                notes.append(z)
                        y = y.findNextSibling('font')
                    if not x.findNextSibling():
                        break
                    else:
                        x = x.findNextSibling()
                           
                links = {}  
                subLinks = {}  
                subClasses = []
                if x.name == 'p':
                    #   obtains any links to subClasses within this class if available                 
                    if x.string == 'SEE OR SEARCH THIS CLASS, SUBCLASS:':
                        xx = x.findNext('tr')
                        while xx.name == 'tr':
                            if not xx.findNextSibling('tr'):
                                xxx= xx.findNext('a')
                                text = getLinks(xxx)
                                text = text.replace(' SEE OR SEARCH CLASS:', "")
                                subLinks[xxx.string] = text
                                break
                            else:
                                xxx= xx.findNext('a')
                                text = getLinks(xxx)
                                subLinks[xxx.string] = text
                                xx = xx.findNextSibling('tr')
                    
                    #   obtains any links to other classes if available  
                    if x.string == 'SEE OR SEARCH CLASS:':
                        xx = x.findNext('tr')
                        while xx.name == 'tr':
                            if not xx.findNextSibling('tr'):
                                xxx= xx.findNext('a')
                                text = getLinks(xxx)
                                links[xxx.string] = text
                                break
                            else:
                                xxx= xx.findNext('a')
                                text = getLinks(xxx)
                                links[xxx.string] = text
                                xx = xx.findNextSibling('tr')



                if x.findNextSibling('p'):
                    x =  x.findNextSibling('p')
                    if x.string == 'SEE OR SEARCH CLASS:':
                        xx = x.findNext('tr')
                        while xx.name == 'tr':
                            if not xx.findNextSibling('tr'):
                                xxx= xx.findNext('a')
                                text = getLinks(xxx)
                                links[xxx.string] = text
                                break
                            else:
                                xxx= xx.findNext('a')
                                text = getLinks(xxx)
                                links[xxx.string] = text
                                xx = xx.findNextSibling('tr')
               
                subClassTitleString = subClassTitle.string
                                
#  table.append({subClassNo.string: [parent.string, subClassTitleString , subClassDefS, notes, subLinks, links, subClasses]})
                table[subClassNo.string] = [parent.string, subClassTitleString , subClassDefS, notes, subLinks, links, subClasses]
    data[classNum].append(table)
    return data

def getLinks(tag):  #Helper function for getting subclass references
    text = ""
    tag = tag.findNext('td')
    while not tag.name == 'tr':
        if tag.name == 'font':
            if not tag.string == None:
                text = text + " " + tag.string
        tag = tag.findNext()
    text = text.strip()
    text = text.replace("\r"," ")
    text = text.replace('\xA0',"")
    text = text.replace("\n", " ")
    text = text.replace("  "," ")
    return text

# def restructure(data, num):
#     print data['379'][6]['1.01'][5]['324']
#     return data2

def getIPC8(soup, data, classNum):
    count = 0
    key = ""
    table = []
    temp = ""
    temp1 = ""
    for line in soup.findAll(['font']):
        text = line.string
        value1 = ''
        value2 = ''
       
        if not text == None:
            text = text.replace(u'\xa0', '').encode('utf-8')
            text = text.replace( "   ", " ")
            text = text.replace("  ", " ")
            count+=1   
            if count > 4:
                if contains_digits(text) :
                    if text[0].isdigit():
                        if not"/" in text:
                            key += " " + text
                        else:
                            value2 = text 
                            table.append([temp.strip(),temp1, value2]) 
                    else:
                        value1 = text
                        temp1 = value1
                        temp = key
                        key = ""
                       
    data[classNum].append(table) 
    return data

def initializeClassSet():    #obtain all the class numbers and places them in a set
    json_data=open('output/classes1.json')
    classSet= []
    data = json.load(json_data)
    for i in data:
        classSet.append( i['Class number'])
    json_data.close()
    return classSet



def main():
    classSet = initializeClassSet()
    data = {}
    
# for every class in the set, get the url and obtain all the info to place in JSON file     
    for i in classSet:
        print i
        if str(i) == '198':
            break
        url = 'http://www.uspto.gov/web/patents/classification/uspc' + str(i) + '/defs' + str(i) + '.htm'
        soup = getSoup(url)
        data, num = getClassNumberAndName(i, data, soup)
        data = getSections(soup, data, num)
        data = getSubClassesMain(soup, data, num)
    with open('bigData1.txt', 'w') as outfile:
        json.dump(data, outfile, indent = 3, sort_keys = True)  
    
    
#     json_data = open('bigData1.txt')
#     data = json.load(json_data)
#     start = False    
#     for i in classSet:
#         print i
#         if str(i) == '361':
#             break
#         if str(i) == '198':
#             start = True
#         if start:
#             url = 'http://www.uspto.gov/web/patents/classification/uspc' + str(i) + '/defs' + str(i) + '.htm'
#             soup = getSoup(url)
#             data, num = getClassNumberAndName(i, data, soup)
#             data = getSections(soup, data, num)
#             data = getSubClassesMain(soup, data, num)
#     with open('bigData1.txt', 'w') as outfile:
#         json.dump(data, outfile, indent = 3, sort_keys = True)  


#     json_data = open('bigData1.txt')
#     data = json.load(json_data)
#     start = False    
#     for i in classSet:
#         print i
#         if str(i) == '361':
#             start = True
#         if str(i) == '568':
#             break
#         if start:
#             url = 'http://www.uspto.gov/web/patents/classification/uspc' + str(i) + '/defs' + str(i) + '.htm'
#             soup = getSoup(url)
#             data, num = getClassNumberAndName(i, data, soup)
#             data = getSections(soup, data, num)
#             data = getSubClassesMain(soup, data, num)
#     with open('bigData1.txt', 'w') as outfile:
#         json.dump(data, outfile, indent = 3, sort_keys = True)  


#     json_data = open('bigData1.txt')
#     data = json.load(json_data)
#     start = False    
#     for i in classSet:
#         if str(i) == '568':
#             start = True
#         if start:
#             url = 'http://www.uspto.gov/web/patents/classification/uspc' + str(i).lower() + '/defs' + str(i).lower() + '.htm'
#             print i
#             soup = getSoup(url)
#             data, num = getClassNumberAndName(i, data, soup)
#             data = getSections(soup, data, num)
#             data = getSubClassesMain(soup, data, num)
#     with open('bigData1.txt', 'w') as outfile:
#         json.dump(data, outfile, indent = 3, sort_keys = True)  



             
if __name__ == "__main__":
    main()
    
    
    
    
    
