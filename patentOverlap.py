import json,re,string,ast,time


def contains_digits(d):    #helper function
    _digits = re.compile('\d')
    return bool(_digits.search(d))
           
def getWords(data):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    words = {}
    
    for classID in data:
        classSet = {}
#         sys.stdout.write(classID+ " ")
        if False:
            pass
        else:
            for subClassID in data[classID][7]:
                subClassSet = {}
#                 sys.stdout.write(subClassID+ " ")
                subClassDefString = data[classID][7][subClassID][2]
                if subClassDefString:
                    a = regex.sub('',subClassDefString).lower()
                subClassDefList = a.split()
                for word in subClassDefList:
                    if not word in subClassSet:
                        subClassSet[word] = 1
                    else:
                        subClassSet[word]+=1
                    classSet[subClassID]= subClassSet
        words[classID] = classSet

#     for i,j in words.iteritems():
#         print i,j
    with open('words.txt', 'w') as outfile:
        json.dump(words, outfile, indent = 5, sort_keys = True) 
#     
    
def main():
#     testPatent = ["dog","visual","chicken","visual","subject", "visual", "chicken"]
    json_data = open('bigData1.txt')
    data = json.load(json_data)
#     getWords(data)
    words = open('wordsHash.txt')
    words = json.load(words)
          
    classID = '455'

    stopWords = open('stopWords.txt')
    stopWordsList = []
    for i in stopWords:
        stopWordsList.append(i.strip())
    superSet = {}
    yearSet = {}
    wordSet = {}
    subClassList = open('subclasses455.txt')
    subClassList = json.load(subClassList)
    
    start = time.clock()
    for x in subClassList:
        subClasses = [x]
        fileLocation = 'C:\Users\Terry\workspace2\patentClasses\FilesAfterQueryModification\\'+x+'\All1.json'
        print fileLocation
        patentList = open(fileLocation)
        print x
        count = 1
        masterSet = {}
        yearCount = {}
        wordCount = {}
#         if not (float(x) > 67.7 and float(x) < 100):
        if (float(x) >= 414.1 and float(x) < 418) or (float(x) >= 456.1 and float(x) <= 457)or (float(x) == 67.7) or (float(x) == 554.2):
            pass
        else: 
            for i in patentList:
                patentLength = 0
                i = unicode(i, errors='ignore')
                if not'Claims' in i:
                    pass
                else:
                    overlappingWords = {}
                    nonOverlappingWords = {}    #words in patent that are not in definitions        
                    i = ast.literal_eval(i)
                    patent = i['Claims'].lower().strip().split()
                    patentLength = len(patent)
                    year = i['Year']
                    if not year in yearCount:
                        yearCount[year]=1
                    else:
                        yearCount[year]+=1
                    if not year in wordCount:
                        wordCount[year]=patentLength
                    else:
                        wordCount[year]+=patentLength
                    if not year in masterSet:
                        masterSet[year]={}
                        masterSet[year]['overlap']={}
                        masterSet[year]['nonoverlap']={}
                    else:
                        pass
                    indexA=0
                    while not indexA == len(patent):
                        if patent[indexA] in stopWordsList:
                            patent.remove(patent[indexA])
                            indexA-=1
                        indexA+=1  
                    for subClassID in subClasses:
                        check = False
                        while not subClassID == "":
                            if check == False:
                                definition = data[classID][1].lower().split()
                                check = True
                            else:
                                definition = words[classID][subClassID]
                            index=0
                            while not index == len(patent):
                                word = patent[index]
                                   
                                if word in definition:
                                    patent.remove(word)
                                    if contains_digits(word) or "," in word or '#' in word or '$' in word or '(' in word or ')' in word or '+' in word or '.' in word or '/' in word or '%' in word or '[' in word or ']' in word or ';' in word or '?' in word or '{' in word or '}' in word or '&' in word or '*' in word or ':' in word or '=' in word or '<' in word or '>' in word or "'" in word or '_'in word or '^' in word or '|' in word:
                                        pass
                                    else:                        
                                        if not word in overlappingWords:
                                            overlappingWords[word]= 1
                                        else:
                                            overlappingWords[word]+= 1 
                                else:
                                    if 'the' in data[classID][7][subClassID][0]:
                                        if contains_digits(word) or "," in word or '#' in word or '$' in word or '(' in word or ')' in word or '+' in word or '.' in word or '/' in word or '%' in word or '[' in word or ']' in word or ';' in word or '?' in word or '{' in word or '}' in word or '&' in word or '*' in word or ':' in word or '=' in word or '<' in word or '>' in word or "'" in word or '_'in word or '^' in word or '|' in word:
                                            pass
                                        else:
                                            if not word in nonOverlappingWords:
                                                nonOverlappingWords[word]= 1
                                            else:
                                                nonOverlappingWords[word]+= 1
                                    index+=1
                            subClassID = data[classID][7][subClassID][0]
                             
                            temp = ""
                            for a in subClassID:
                                if not a.isalpha():
                                    temp = temp + a
                            temp = temp.strip()
                            subClassID = temp    
                        print count
                    count+=1  
                    for i in overlappingWords:
                        if not i in masterSet[year]['overlap']:
                            masterSet[year]['overlap'][i] = overlappingWords[i]
                        else:
                            masterSet[year]['overlap'][i]+= overlappingWords[i]
                    for i in nonOverlappingWords:
                        if not i in masterSet[year]['nonoverlap']:
                            masterSet[year]['nonoverlap'][i] = nonOverlappingWords[i]
                        else:
                            masterSet[year]['nonoverlap'][i]+= nonOverlappingWords[i]
                 
        superSet[x] = masterSet
        yearSet[x] = yearCount
        wordSet[x] = wordCount
     
     
     
                
    with open('superSet1.txt', 'w') as outfile:
        json.dump(superSet, outfile, indent = 3,sort_keys = True) 
    with open('yearSet1.txt', 'w') as outfile:
        json.dump(yearSet, outfile, indent = 3,sort_keys = True) 
    with open('wordSet1.txt', 'w') as outfile:
        json.dump(wordSet, outfile, indent = 3,sort_keys = True) 
  
     
    elapsed = (time.clock() - start)
    print elapsed,"@@@@@@@"
    
if __name__ == '__main__':
    main()
    
    
    