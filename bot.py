import os,re,sys,asyncio,sqlite3,json,time,atexit
from discord import Game,Channel,Server,Emoji,Permissions
from discord.utils import get
from discord.ext.commands import Bot

try:
	config = json.load(open('config.json'))
	if config["prefix"]:
		client = Bot(command_prefix=config["prefix"])
	else:
		client = Bot(command_prefix=";")
except:
	config = None
conn = sqlite3.connect("tickets.db")
db = conn.cursor()

def info(infomsg):
	print("INFO: "+infomsg)

def error(errmsg, exit=False):
	if exit:
		print("ERROR: "+errmsg)
		sys.exit()
	else:
		print("WARNING: "+errmsg)

def exitfunc():
	client.logout()
	info("Shutting off...")

def clearterminal():
	os.system('cls' if os.name == 'nt' else 'clear')

def checkdb():
	info("Performing database check...")
	errors=0
	if not db.execute("SELECT name FROM sqlite_master WHERE type='table' and name='data';").fetchall() or not db.execute("SELECT name FROM sqlite_master WHERE type='table' and name='tickets';").fetchall():
		error("One or more databases are empty/corrupted! Recreating databases...")
		errors+=1
		db.execute("CREATE TABLE IF NOT EXISTS `tickets`(`id` int(11) NOT NULL, `timeopened` varchar(50) NOT NULL, `timeclosed` varchar(50) NULL, `opened` tinyint(1) NOT NULL DEFAULT 1, `opener` int(20) NOT NULL, `assigneddsupport` int(20) NOT NULL)")
		db.execute("CREATE TABLE IF NOT EXISTS `data`(`id` int(1) NOT NULL, `totaltickets` int(11) NOT NULL, `supportroleid` int(20) NULL, `admincmdrole` int(20) NULL)")
	if not db.execute("SELECT * FROM `data`").fetchall():
		error("Database `data` is empty or corrupted! Recreating...")
		errors+=1
		db.execute("DROP TABLE `data`")
		db.execute("CREATE TABLE IF NOT EXISTS `data`(`id` int(1) NOT NULL, `totaltickets` int(11) NOT NULL, `supportroleid` int(20) NULL, `admincmdrole` int(20) NULL)")
		db.execute("INSERT INTO `data` VALUES(1,0,NULL,NULL)")
	conn.commit()
	if errors>0:
		error("Database check complete! ({} error".format(errors)+("s" if errors>1 else "")+")")
		info("Re-Running check...")
		return False
	else:
		info("Database check complete, no errors found!")
		return True

def preparebotstart():
	clearterminal()
	info("TicketBot made by @Elipse458 in collaboration with @SyntheticBIT\nfor mc-market.org.")
	if not config:
		error("Config missing or corrupted! Please fix the config and start the application again.", True)
	if not config["token"]:
		error("Bot token not set in config! The application will now exit...", True)
	if not config["ownerid"]:
		error("Owner id not set! Owner commands will not be available to anyone.")
	if not config["prefix"]:
		error("Command prefix not set, using default ';' prefix...")
		config["prefix"]=";"
	checks=0
	while not checkdb():
		time.sleep(0.5)
		checks+=1
		if checks>=3:
			error("Error while writing to database!", True)
	startbot()

def startbot():
	info("Starting bot...")
	try:
		client.run(config["token"])
	except:
		error("Client failed to connect", True)

@client.event
async def on_ready():
	info("TicketBot v1.0 started")

preparebotstart()