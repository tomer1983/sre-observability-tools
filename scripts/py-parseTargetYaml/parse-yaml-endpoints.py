import yaml
import csv
import glob
from pathlib import Path
from jproperties import Properties

def isFileExist(file):
    if file.is_file():
        return True
    else:
        return False

def validatePathToProccess(path):
    if len(glob.glob(path)) > 0 :
        print(f"{len(glob.glob(path))} files found in {path}")
        return True
    else:
        print(f"** error ** {len(glob.glob(path))} files found in {path}")
        return False

def getListOfFilesToParse(dirPath):
    if len(glob.glob(dirPath)) > 0 :
        print(f"getListOfFilesToParse : {len(glob.glob(dirPath))} files found in {dirPath}")
        return glob.glob(dirPath)
    else:
        print(f"getListOfFilesToParse : error {len(glob.glob(dirPath))} files found in {dirPath}")
        return False

def insert_to_csv(data):
    print(f"*** {data}write to file")
    with open(resultCsv, 'a') as f_result:
        writer = csv.writer(f_result)
        writer.writerow(data)
        f_result.close()


def get_source(ruleName,f_read_data,name,port):
    # print(f_read_data)
    print (f"## port {port} -- name {name}")
    dataToCsv=[]
    dataToCsv.append(ruleName)
    if("ip" in f_read_data):
        ip = f_read_data['ip']
        dataToCsv.append(ip)
    if ("nodeName" in f_read_data):
        nodename = f_read_data['nodeName']
        dataToCsv.append(nodename)
        dataToCsv.append(name)
        dataToCsv.append(port)
    print(f"dataTocsv DEBUG {dataToCsv}")
    return(dataToCsv)




# print(yaml.dump(read_data['items'][i]['subsets']))


## main
# PREPARE
resultCsv = Path('result.csv')
propertiesFile = Path('./main.properties')
if(isFileExist(propertiesFile)):
    configs = Properties()
    # load the properties file into our Properties object
    with open(propertiesFile, 'rb') as config_file:
        configs.load(config_file)
        # print(configs['FILES_LOCATION'].data)

    with open(resultCsv, 'r+') as file:
        file.truncate(0)

# PROCCESS FILES
    filesLocation = configs['FILES_LOCATION'].data
    if(validatePathToProccess(filesLocation)):
        for filename in glob.glob(filesLocation):
            print(f" running on {filename}")
            with open(filename, 'r') as stream:
                # Load YAML data from the file
                read_data = yaml.safe_load(stream)



            for i in range (len(read_data['items'])):
                # ignore blocks without subsets
                if ("subsets" in read_data['items'][i]):
                    print(f"### {read_data['items'][i]['metadata']['name']}")
                    if ("addresses" in read_data['items'][i]['subsets'][0]):
                        ruleName = read_data['items'][i]['metadata']['name']
                        portName = read_data['items'][i]['subsets'][0]['ports'][0]['name']
                        portNum = read_data['items'][i]['subsets'][0]['ports'][0]['port']
                        numOfAdd = len(read_data['items'][i]['subsets'][0]['addresses'])
                        print(f"{i} block has {numOfAdd} address")
                        for address in range (numOfAdd):
                            insert_to_csv(get_source(ruleName,read_data['items'][i]['subsets'][0]['addresses'][address],portName,portNum))
                else:
                    print(f"****WARN 0 subsets record found in {read_data['items'][i]['metadata']['name']}")
else:
    print(f"** error ** file {propertiesFile} not found")







