str = 'http://hns-cff.hr/files/documents/11815/01. Parova,sudaca,delegata 14. kolo.pdf'
res = ''

for char in str:
    if char == ' ':
        char = '%20'
    res += char

print res
