from ftfcore import config
import mysql.connector

mydb = mysql.connector.connect(
  host=config.mysql_host,
  port=config.mysql_port,
  user=config.mysql_user,
  passwd=config.mysql_passwd,
  database="ftfbot"
)

mycursor = mydb.cursor()

mycursor.execute("INSERT INTO `tempdata`(`data`,`timestamp`) VALUES ('123','1578615639')")
mycursor.close()
mydb.commit()
mydb.close()