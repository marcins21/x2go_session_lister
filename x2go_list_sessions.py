#!/usr/bin/env python3
import subprocess as sp
from datetime import datetime
from sys import argv
import argparse

USER_NAME_ID = 11
USER_SESSION_ID = 1
USER_STATUS_ID = 4
START_SESSION_TIMESTAMP_ID = 5
END_SESSION_TIMESTAMP_ID = 10
USERS_IP_ID = 7


class DataObject:
    def __init__(self,data:list):
        self.data = data
        self.x2go_users = []
        self.users_status = []
        self.users_id = []
        self.users_session_time = []
        self.last_active = []
        self.users_ip = []
        count = 0
        for record in data:
            records = record.split("|")
            if records[USER_NAME_ID] in self.x2go_users:
                count +=1
                self.x2go_users.append(records[USER_NAME_ID]+"_"*count)
            else:
                self.x2go_users.append(records[USER_NAME_ID])
                 
            self.users_status.append(records[USER_STATUS_ID])
            self.users_id.append(records[USER_SESSION_ID])
            start_time = datetime.strptime(records[START_SESSION_TIMESTAMP_ID],"%Y-%m-%dT%H:%M:%S")
            end_time = datetime.strptime(records[END_SESSION_TIMESTAMP_ID],"%Y-%m-%dT%H:%M:%S")
            delta = end_time - start_time
            self.users_session_time.append(str(delta.days))
            self.last_active.append(records[END_SESSION_TIMESTAMP_ID])
            self.users_ip.append(records[USERS_IP_ID])
    
            
    def get_user_names(self):
        return self.x2go_users
    
    def get_user_status(self):
        return self.users_status
    
    def get_users_id(self):
        return self.users_id
    def get_users_session_time(self):
        return self.users_session_time
    
    def get_last_active(self):
        return self.last_active  
    
    def get_data_tab(self):
        return self.data
    
    def get_users_ip(self):
        return self.users_ip


def map_users_with_status(users:list, users_status:list) -> dict:
    result_dict = dict(zip(users,users_status))
    return result_dict

def get_users_id(users:list, users_id:list) -> dict:
    result_dict = dict(zip(users,users_id))
    return result_dict

def get_session_time(users:list, users_session_time:list,last_active:list) :
    results_dict_sessions = dict(zip(users,users_session_time))
    result_dict_activity = dict(zip(users,last_active))
    return results_dict_sessions,result_dict_activity

def get_users_ip(users:list, users_ip:list) -> dict:
    result_dict_ip = dict(zip(users,users_ip))
    return result_dict_ip

def manual():
    parser = argparse.ArgumentParser(description="Help with X2go users")
    parser.add_argument("-l","--last",help="Get sessions that are lasting loneger than [LAST] DAYS",type=int)
    parser.add_argument("-s","--status",help="Print Sessions with given status R - Running S - Suspended F - Failed",type=str)
    parser.add_argument("-v","--verbose",help="Print Sessions in better format showing only important sections",action='store_true',default=False)
    args = parser.parse_args()
    
    return args 
   
#Merging Function
def main(argv):
    #Bash Commands
    x2go_list_all_sessions = """sudo x2golistsessions_root"""
    #x2go_list_user_names = """sudo x2golistsessions_root | awk -F "|" '{print$12}' | cut -c 1-6"""

    substring = "\n"
    data_from_bash_command = sp.getoutput(x2go_list_all_sessions)
    data_arr = data_from_bash_command.split(substring)
    result_dict = {}
    
    #Data
    data_object = DataObject(data_arr)

    users = data_object.get_user_names()
    data_arr = data_object.get_data_tab()
    users_status = map_users_with_status(users,data_object.get_user_status())
    users_session_id = get_users_id(users,data_object.get_users_id())
    users_session_time,users_last_active = get_session_time(users,data_object.get_users_session_time(),data_object.get_last_active())
    users_ip  = get_users_ip(users,data_object.get_users_ip())

    namespace_args = manual()
    
    #Counting Sessions that are lasting longer than given number 
    if argv[0] == "-l" or argv[0] == "--last":
        lasting_more_than = argv[1]        
        try:
            count = 0
            if int(lasting_more_than) >= 0:
                for values in users_session_time.values():
                    if int(values) >= int(lasting_more_than):
                        count+=1
                print(count)
            else:
                print("Wrong number of days, give INTEGER >= 0")
            
        except ValueError:
            print("Wrong number of days, give INTEGER >= 0")
    
    #Counting Sessions that have given status
    elif argv[0] == "-s" or argv[0] == "--status":
        status = str(argv[1])
        status = status.lower()
        count = 0
        if not ((status == 'r') or (status == 's') or (status == 'f')):
            return 0
        else:
            status = status.capitalize()
            for value in users_status.values():
                if value == status:
                    count += 1    
            print(count)
    
    #Showing verbose content
    elif argv[0] == "-v" or argv[0] == "--verbose":  
        #Mergin Values for Key
        for user in users:
            user_info = ' '.join(["|  "+users_session_id[user]+"  |  "+users_status[user]+"  |  "+users_session_time[user]+"  |  "+users_last_active[user]+"  |  "+users_ip[user]])
            result_dict[user] = user_info
            
        #Pretty Console Output
        print("\nUSER"+" "*22+"  ID SESJI"+" "*21+"STAUS"+"  DNI"+" "*5+"OSTATNIA AKTYWNKOSC"+"      IP"+"\n")
        for k,v in result_dict.items():
            print(k,' '*10,v)   
   
        #print(result_dict)
             
if __name__ == "__main__":
    if len(argv) < 2:
        main(['-v'])
        print("\nType 'python3 x2go_python_script.py --help' to show parameters")
    else:
        main(argv[1:])