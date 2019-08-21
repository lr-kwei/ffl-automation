import glob
import subprocess
import os
import hashlib
import csv
import shutil
import shlex
import time
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

'''
changed datagatewayTE (https://taxonomy-endpoint.liveramp.net/2136/edit) to drop off TE in s3 bucket
    change rootpath to /mschf/get_property({da_id})
changed datagatewayEndpoint (https://endpoint.liveramp.net/26436#overview) to drop off data in s3 bucket
    no md5, changed packager path

'''



def main():

    # move/delete files from s3 accordingly.
    s3Mover()
    print("possibly moving files " + datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"))

    # get list of new data files/folders
    processing_list = getFolders()

    if (len(processing_list) > 0):
        print("processing new files" + datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"))
    else:
        print("no new files" + datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"))

    s3Cleaner()

    # loop through new data files/folders
    for da_id in processing_list:
        if isActiveRefresher(da_id):
            shutil.rmtree("/var/nfs/mounts/files/pprms/processing/"+str(da_id)+"/")
            print(str(da_id) + " is activerefresher -> removed from queue")
        else:
            # pull log info for the da_id in question
            row = statusPull(da_id)
            path = "/var/nfs/mounts/files/pprms/"+str(da_id)+"/"
            # if row == [] (completely new DA) -> create a new log row and move the entire folder from pprms/processing to pprms
            if row == []:
                # append a new log entry for the relevant da_id
                newLogLine(da_id)
                print(da_id + " first delivery logged")
                # move files from pprms/processing to pprms/ -> creates new folder since new da_id
                moveFiles(da_id)
                print(da_id + " first delivery moved")
                cleanFolder(path)
                print(da_id + " first delivery cleaned")
                if checkTaxoPids(path) == False:
                    errorLogger(da_id, "mismatched pid")
            # if there is new data for a DA that has not been sent to DG yet -> move the files and clean the destination folder
            elif row[3] == 'n':
                print(da_id + " additional delivery")
                # move files from pprms/processing to pprms/
                moveFiles(da_id)
                print(da_id + " additional delivery moved")
                # clean folder: if multiple taxonomies, only keep newest one. if there are multiple data files, append them and get rid of duplicates.
                cleanFolder(path)
                print(da_id + " additional delivery cleaned")

            # if there is new data for a DA that has already been sent to DG -> throw a shitfit
            elif row[3] != 'n':
                errorLogger(da_id, "new data for an already delivered campaign history")

    # loop through csv and see which ones are ready to send. keep a counter of the most recent sent and go to that line?
    needToSendList = logCheck()
    for row in needToSendList:
        da_id = row[0]
        path = "/var/nfs/mounts/files/pprms/"+str(da_id)+"/"
        if isActiveRefresher(da_id):
            shutil.rmtree(path)
            deleteLogRow(da_id)
            print(str(da_id) + " is activerefresher -> deleted")
        else:
            #gunzip the data file, md5 it, and send the trio to the sftp
            sendData(path, da_id)

    lastRanTime()

def s3Mover():
    '''
    Detects if anything new is in s3://com-liveramp-product/mschf/. Moves/Deletes files accordingly.
    Endpoint/TE will always populate the s3 folder when needed.

    Returns:
        False if nothing new in s3
        True if new things have been moved from s3

    useful s3 commands:
    list files: aws s3 ls s3://com-liveramp-product/mschf/
    copy sample file: aws s3 cp /home/kwei/mschf/daid_428936/75371336/1.txt s3://com-liveramp-product/mschf/test/
    download s3 files to nfs: aws s3 sync s3://com-liveramp-product/mschf/ /var/nfs/mounts/files/pprms/processing
    delete folder/files: aws s3 rm s3://com-liveramp-product/mschf/ --recursive"
    '''


    # download all files from the s3 folder
    syncS3Command = "aws s3 sync s3://com-liveramp-product/mschf/ /var/nfs/mounts/files/pprms/processing"
    subprocess.call(syncS3Command, shell=True)

    '''
    # old commmunication code
    proc1 = subprocess.Popen(syncS3Command.split(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    count = 0
    for chunk in iter(lambda: proc.stdout.read(100), b''):
        count += len(chunk)

    output1, error1 = proc1.communicate()


    # false/emptyoutputstring -> no new campaign history files -> stop script here
    if (output1 == "" and error1 == None):
        return False
    '''


def getFolders():
    '''
    Looks in '/var/nfs/mounts/files/pprms/processing' for new data
    Returns:
        List of strings (folder names which are the corresponding destination account id) that have new campaign history files
    '''
    root = '/var/nfs/mounts/files/pprms/processing'
    dirlist = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]
    return dirlist

def s3Cleaner():
    # removes all files in the s3 folder
    cleanS3Command = "aws s3 rm s3://com-liveramp-product/mschf/ --recursive"
    subprocess.call(cleanS3Command, shell=True)
    '''
    # old bad communicator
    proc2 = subprocess.Popen(cleanS3Command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output2, error2 = proc2.communicate()

    # true -> new campaign history files -> continue running the entire script
    return True
    '''

def statusPull(da_id):
    '''
    Params: da_id (int)
    Pulls log info for relevant da_id
    Returns:
        array of log data [da_id, datetime_created, datetime_tosend, sent?] (empty if da_id has not been seen before)
    '''
    row = []
    with open('/var/nfs/mounts/files/pprms/log.csv', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[0] == str(da_id):
                row = line
    return row


def newLogLine(da_id):
    '''
    Params: da_id (int)
    Appends a new log entry for the relevant da_id
    Returns: none
    '''
    with open('/var/nfs/mounts/files/pprms/log.csv', 'ab') as f:
        writer = csv.writer(f, delimiter = ',')
        future_time = datetime.now() + timedelta(hours=72)
        writer.writerow([da_id, datetime.now().strftime("%Y-%m-%d|%H:%M:%S.%f"), future_time.strftime("%Y-%m-%d|%H:%M:%S.%f"), 'n'])


def moveFiles(da_id):
    '''
    Params: da_id (int)
    Move files from pprms/processing to pprms/. creates new folder if new da_id
    Returns: none
    '''
    src = "/var/nfs/mounts/files/pprms/processing/"+str(da_id)
    dest = "/var/nfs/mounts/files/pprms/"+str(da_id)
    # if the folder already exists, just move all the files in there
    if os.path.exists(dest):
        files = os.listdir(src)
        for f in files:
            if f.endswith(('.gz', '.md5', '.csv')):
                shutil.move(src+"/"+f, dest)
        # delete folder from processing when you're done.
        shutil.rmtree(src)
    # if the folder doesn't already exist, just move the file
    else:
        shutil.move(src, "/var/nfs/mounts/files/pprms/")


def cleanFolder(path):
    '''
    params: path = "/var/nfs/mounts/files/pprms/"+str(da_id)+"/"
    clean folder: if multiple taxonomies, only keep newest one. if there are multiple data files, append them and get rid of duplicates.
    returns: none
    '''
    # if there are any gzipped files, we have to gunzip any gzipped files
    gzips = glob.glob(path+"*.gz")
    if len(gzips) > 0:
        for gzip in gzips:
            gunzip_command = "gunzip " + gzip
            gunzip_process = subprocess.Popen(gunzip_command.split(), stdout=subprocess.PIPE)
            gunzip_output, gunzip_error = gunzip_process.communicate()

    '''
    # append data files in a pythonic way without bash, but you ahve to be careful of duplicates
    datafiles = glob.glob(path+"*.txt")
    if len(datafiles) > 1:
        datafiles.sort(key = os.path.getctime)
        # oldest datafile, which is at the beginning of the list, is set as the master file
        masterfile_path = datafiles[0]
    with open(masterfile_path, "a") as masterfile:
        for addfile_path in datafiles[1:]:
            with open(addfile_path, "r") as addfile:
                masterfile.write(addfile.read())
            os.remove(addfile_path)
    '''
    # append all files and get rid of duplicates
    datafiles = glob.glob(path+"*.txt")
    if len(datafiles) > 1:
        datafiles.sort(key = os.path.getctime)
        # oldest datafile, which is at the beginning of the list, is set as the master file
        masterfile_path = datafiles[0]
        # append files and get rid of duplicates
        tempfile_path = path + "tempfile"
        dedupe_command1 = "cat " + path + "*.txt | sort | uniq > " + tempfile_path
        dedupe_command2 = "cat " + tempfile_path + " > " + masterfile_path
        subprocess.call(dedupe_command1, shell=True)
        subprocess.call(dedupe_command2, shell=True)
        os.remove(tempfile_path)
        for datafile_to_remove in datafiles[1:]:
            os.remove(datafile_to_remove)

    # delete all taxonomies except for the most recent one
    taxos = glob.glob(path+"*.csv")
    if len(taxos) > 1:
        taxos.sort(key=os.path.getctime)
        for taxo in taxos[:-1]:
            os.remove(taxo)


def isActiveRefresher(da_id):
    with open('/var/nfs/mounts/files/pprms/activerefreshers.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            for activerefresher in row:
                if str(activerefresher) == str(da_id):
                    return True
    return False

def errorLogger(da_id, issue):
    with open('/var/nfs/mounts/files/pprms/errorlog.csv', 'ab') as f:
        writer = csv.writer(f, delimiter = ',')
        writer.writerow([da_id, datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"), issue])
    sys.exit(1)


def logCheck():
    '''
    returns:
        needToSendList (list) -> list of log rows containing da's that need to be gzipped, md5'ed, and sent to sftp
    '''
    needToSendList = []

    with open('/var/nfs/mounts/files/pprms/log.csv', 'r') as f:
        reader = csv.reader(f, delimiter = ',')
        next(reader)
        for row in reader:
            if (datetime.strptime(row[2], "%Y-%m-%d|%H:%M:%S.%f") < datetime.now() and row[3] == 'n'):
                needToSendList.append(row)

    return needToSendList

def checkTaxoPids(path):
    # fix taxonomies if "None" or mismatched pid
    datafiles = glob.glob(path+"*.txt")

    if len(datafiles) > 0:

        data_string = os.path.basename(datafiles[0])
        true_pid = data_string[data_string.index("_")+1:data_string.index("_")+5]

        taxos = glob.glob(path+"*.csv")
        taxo_string = os.path.basename(taxos[0])
        taxo_pid = taxo_string[taxo_string.index("_")+1:taxo_string.index("_")+5]

        os.chdir(path)

        if taxo_pid == true_pid:
            return True
        elif taxo_pid == "None":
            # just rename the taxonomy
            renamed_taxo_string = taxo_string.replace(taxo_pid, true_pid)
            os.rename(taxo_string,renamed_taxo_string)
            return True
        elif taxo_pid != true_pid:
            return False

def sendData(path, da_id):
    cleanFolder(path)
    print(str(da_id) + " final check cleaned " + datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"))
    if checkTaxoPids(path) == False:
        errorLogger(da_id, " mismatched pid " + datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"))
    print(str(da_id) + " gzipping data " + datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"))
    gzipData(path)
    print(str(da_id) + " data gzipped " + datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"))
    print(str(da_id) + " generating md5 " + datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"))
    finalmd5(path)
    print(str(da_id) + " md5 generated " + datetime.now().strftime("%Y-%m-%d%H:%M:%S.%f"))
    sendsftp(path, da_id)

def gzipData(path):
    data = glob.glob(path+"*.txt")
    if len(data) == 1:
        gzip_command = "gzip " + data[0]
        gzip_process = subprocess.Popen(gzip_command.split(), stdout=subprocess.PIPE)
        gzip_output, gzip_error = gzip_process.communicate()


def finalmd5(path):
    prev_md5 = glob.glob(path+"*.md5")
    if prev_md5 == []:
        data = glob.glob(path+"*.gz")
        if len(data) == 1:
            master_file_path = data[0]
            md5filename = master_file_path + ".md5"
            md5er = "md5sum " + master_file_path + " > " + md5filename
            subprocess.call(md5er, shell=True)
            removeAbsolutePathFromMd5 = "sed -i -r \"s/ .*\\/(.+)/  \\1/g\" " + md5filename
            subprocess.call(removeAbsolutePathFromMd5, shell=True)

def sendsftp(path, da_id):
    files = os.listdir(path)
    if len(files) != 3:
        errorLogger(da_id, "folder has incorrect amount of ")
    filesToBeMoved = []
    for f in files:
        if f.endswith(('.gz', '.md5', '.csv')):
            filesToBeMoved.append(f)
    os.chdir(path)
    for f in filesToBeMoved:
        transferred = False
        while transferred == False:
            print ("trying to transfer " + path + f)
            string = os.popen('scp -q -oIdentityFile=/apps/file_deliverer/current/config/dist_id_rsa -l 16000 ' + f + ' 7898fxsv@sfgint.acxiom.net:/ && echo success!').read()
            print string
            if "success" in string:
                transferred = True
    updateSendLog(da_id)


def updateSendLog(da_id):
    logname = '/var/nfs/mounts/files/pprms/log.csv'
    tempfile = NamedTemporaryFile(delete=False)

    with open(logname, 'rb') as csvFile, tempfile:
        reader = csv.reader(csvFile, delimiter=',')
        writer = csv.writer(tempfile, delimiter=',')
        for row in reader:
            if row[0] == str(da_id):
                row[3] = datetime.now().strftime("%Y-%m-%d|%H:%M:%S.%f")
                writer.writerow(row)
            else:
                writer.writerow(row)

    shutil.move(tempfile.name, logname)


# USEFUL TESTING FUNCTIONS

def deleteLogRow(da_id):
    logname = '/var/nfs/mounts/files/pprms/log.csv'
    tempfile = NamedTemporaryFile(delete=False)

    with open(logname, 'rb') as csvFile, tempfile:
        reader = csv.reader(csvFile, delimiter=',')
        writer = csv.writer(tempfile, delimiter=',')
        for row in reader:
            if row[0] != str(da_id):
                writer.writerow(row)

    shutil.move(tempfile.name, logname)

# make sure to gzip and md5 data before!!!
def sendDataNOW(da_id):
    path = "/var/nfs/mounts/files/pprms/"+str(da_id)+"/"
    sendData(path, da_id)
    logname = '/var/nfs/mounts/files/pprms/log.csv'
    tempfile = NamedTemporaryFile(delete=False)
    with open(logname, 'rb') as csvFile, tempfile:
        reader = csv.reader(csvFile, delimiter=',')
        writer = csv.writer(tempfile, delimiter=',')
        for row in reader:
            if row[0] == str(da_id):
                row[2] = datetime.now().strftime("%Y-%m-%d|%H:%M:%S.%f")
                writer.writerow(row)
            else:
                writer.writerow(row)
    shutil.move(tempfile.name, logname)

def lastRanTime():
    with open('/var/nfs/mounts/files/pprms/lastrantime.csv', 'ab') as f:
        writer = csv.writer(f, delimiter = ',')
        writer.writerow([datetime.now().strftime("%Y-%m-%d|%H:%M:%S.%f")])

# if i have permissions:
# bash -c 'while [ 0 ]; do ./repeatscript.sh;sleep 14400; done'

if __name__ == "__main__":

    while 1:
        main()

        dt = datetime.now() + timedelta(hours=3)

        while datetime.now() < dt:
            time.sleep(3600)
