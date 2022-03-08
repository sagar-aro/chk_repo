maria_connection_string = 'mysql+mysqlconnector://CMaaS_so:zVfMt8uFqDpDv6d@maria4134-lb-fm-in.iglb.intel.com:3307/CMaaS'

import mysql.connector as mdb

conn = mdb.connect(user="CMaaS_so", password="zVfMt8uFqDpDv6d", host="maria4134-lb-fm-in.iglb.intel.com", port="3307",
                   database='CMaaS')

query = """INSERT INTO sut(sut_nm,ip_addr_txt,mac_addr_txt,uuid,brd_sr_nbr,info_cre_dtm_txt,act_ind,cre_agt_id) 
VALUES(%s,%s,%s,%s,%s,%s,%s,%s) """
cursor = conn.cursor()
ip_addr_text = "123.456"
mac_addr_txt = "00:234:798"
_values = ("VISH-1", ip_addr_text, mac_addr_txt, "TEST", "TEST", "TEST", "TEST", "TEST")
cursor.execute(query, _values)
conn.commit()
cursor.close()
conn.close()
