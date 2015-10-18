"""
    dispatcher.py
    This process continuously checks whether there exist unjudged submissions.
"""

from dispatcherFunc import *
import time
import logging
import subprocess, sys
logging.basicConfig(filename = 'dispatcher.log', level = logging.INFO, format = '%(asctime)s ::%(message)s',datafmt = '%m/%d/%Y %I:%M:%S %p')
logging.info('==========Dispatcher Started==========')

machineInfo = getMachine()
if machineInfo != None:
    initMachine(machineInfo)
    logging.info('getMachine Success')
else:
    logging.info('getMachine Error')
    logging.info('Please check the file machineInfo.config to check the settings')
    logging.info('==========Dispatcher Finished==========')
    exit(0)

dbIP, dbUser, dbPasswd, dbName = getdbInfo()
if dbIP == None or dbUser == None or dbPasswd == None or dbName == None:
    logging.info('getdbInfo Error')
    logging.info('Please check the settings in ojdatabase.config')
    logging.info('==========Dispatcher Finished==========')
    exit(0)
logging.info('connect to database')

while True:
   
    DB = connectDB(dbIP, dbUser, dbPasswd, dbName)
    if DB == None:
        logging.info('connect database error')
        logging.info('Please check the settings in ojdatabase.config')
        logging.info('==========Dispatcher Finished==========')
        exit(0)
    cur = DB.cursor()
    cur.execute("USE nthuoj;")
    cur.execute("SELECT * FROM problem_submission WHERE status = 'WAIT' ORDER BY id ASC LIMIT 100;")
    sidQuery = cur.fetchone()
    sid = 1
    pid = 2
    judgeLanguage = 'cpp'
    judgeURL = 'judgeURL' 
    if sidQuery != None:
        sid = sidQuery[0]
        pid = sidQuery[1]
        logging.info('sidQuery Success!')
        logging.info('sid = %d, pid = %d' % (sid, pid))
        cur.execute("SELECT * FROM problem_problem where id = '%d';" % pid)
        pidQuery = cur.fetchone()
        judgeSource = pidQuery[11]
        judgeType = pidQuery[12]
        judgeLanguage = pidQuery[13]
        logging.info('pidQuery Success!')
        logging.info('judgeSource = %s, judgeType = %s, judgeLanguage = %s' % (judgeSource, judgeType, judgeLanguage))

        if judgeSource == "LOCAL":
            idleMachine = None
            logging.info('get idleMachine')
            while(idleMachine == None):
                idleMachine = getIdleMachine()
                time.sleep(1)
            logging.info('idleMachine = %s' % idleMachine)
            cur.execute("UPDATE problem_submission SET status = 'JUDGING' WHERE id = '%d';" % sid)
            DB.commit()
            judgeIP = machineInfo[idleMachine]
            judgeURL = judgeIP + "/interface.py"
            logging.info('get judgeURL = %s' % judgeURL)            
        else :
            cur.execute("UPDATE problem_submission SET status = 'JUDGING' WHERE id = '%d';" % sid)
            logging.info('send info to other judge')
            """
		to be continued
            """
    time.sleep(1)