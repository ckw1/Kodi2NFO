import os, sqlite3, re, configparser
from xml.dom import minidom

# Kodi DB file
config = configparser.ConfigParser()
config.read('config.ini')
Kodi_UserData = config['DEFAULT']['UserData']
Kodi_db_name = [x for x in os.listdir(Kodi_UserData + os.sep + 'Database') if x.startswith('MyVideo')]
if Kodi_db_name[0]:
    Kodi_db_path = Kodi_UserData + os.sep + 'Database' + os.sep + Kodi_db_name[0]
else:
    print('Error in locate db file')
    exit()

# Initializing
sth_changed = False

# sqlite file retrieve Movie userrating
conn = sqlite3.connect('file:' + Kodi_db_path + '?mode=ro', uri=True)
c = conn.cursor()
c.execute('Select c22, userrating from movie where userrating IS NOT NULL')
files = c.fetchall() 

# parse original xml/nfo file
for file in files:
    # Escape stack file and return the raw file path
    if r'stack://' in file[0]:
        rawfileS = re.sub('(stack:\/\/)|(\.cd1)|(\.cd2)','', file[0])
        rawfile = [x.strip() for x in rawfileS.split(',')][0]
    else:
        rawfile = file[0]

    filename = os.path.basename(rawfile)
    dirname = os.path.dirname(rawfile)
    videoname = os.path.splitext(filename)[0]
    nfo_file = videoname + '.nfo'
    doc = minidom.parse(dirname + os.sep + nfo_file)
    x = doc.getElementsByTagName('userrating')
    if x:
        rating = x[0].firstChild.data
        existrating = True
    else:
        rating is None
        existrating = False

    if existrating == True and int(rating) == file[1]:
        continue
    else:
        sth_changed = True
        print(videoname, 'is different')
        if existrating == True:
            oldrating = rating                                
            x[0].firstChild.data = file[1]
        else:
            oldrating = 'null'
            UR = doc.createElement('userrating')
            UR_int = doc.createTextNode(str(file[1]))
            UR.appendChild(UR_int)
            doc.childNodes[0].appendChild(UR)

        with open(dirname + os.sep + nfo_file,'w') as fh:
            doc.writexml(fh)
            print(videoname, 'is adjusted from', oldrating, 'to', file[1] )

if sth_changed == False:
    print('No difference was found')