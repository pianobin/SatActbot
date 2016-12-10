import praw
import sqlite3
import bot
import time

SUMMONS = ['!SATACT', '!ACTSAT']
REPLY_TEMP = "beep boop\n\nThe equivalent " #ACT/SAT
REPLY_TEMP2 = " score to your " #ACT/SAT
REPLY_TEMP3 = " score is " #score
REPLY_TEMP4 = ".\n\n***\n\n^Data ^was ^provided ^by ^Collegeboard's ^Concordance ^tables ^last ^updated ^May ^9, ^2016 ^| ^Created ^by ^/u/Pianobin"

ACTscores = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]

SATscores = [560, 630, 720, 760, 810, 860, 900, 940, 980, 1020, 1060, 1110, 1130, 1160, 1200, 1240, 1280, 1310, 1350, 1390, 1420, 1450, 1490, 1520, 1560, 1600]

login_us = os.environ['REDDIT_USERNAME']
login_pass = os.environ['REDDIT_PASSWORD']

def main():
	reddit = praw.Reddit(user_agent='SatActBot (by /u/Pianobin)', username = login_us, password = login_pass, client_id= bot.idS, client_secret = bot.idSec)
	subreddit = reddit.subreddit('SatActbot')
	openDB()
	while True:
		for submission in subreddit.new(limit=10):
			print(submission.title)
			print(submission.url)
			process_sub(submission)
		time.sleep(30)	
	closeDB()

def openDB():
	global db
	global cursor
	db = sqlite3.connect("Comment.db")
	cursor = db.cursor()

def closeDB():
	db.close()

def process_sub(submission):
	submission.comments.replace_more(limit=0)
	for comment in submission.comments.list():
		foundLink = False
		cursor.execute("""SELECT link FROM comments WHERE link=?""", (comment.permalink(),))
		for row in cursor:
			if comment.permalink() == row[0]:
				foundLink = True
				break	
		if foundLink:
			pass
		else:
			for summon in SUMMONS:
				if summon in comment.body:
					commStr = str(comment.body)
					print(commStr)
					for num in commStr.split():
						if num.isdigit():
							theNum = int(num)
							print(theNum)
							if theNum >= 10 and theNum < 36: #ACT score provided
								theIndex = ACTscores.index(theNum)
								lowNum = SATscores[theIndex]
								highNum = SATscores[theIndex + 1] - 10		
								theType = "ACT"
								notTheType = "SAT"
								response = "between " + str(lowNum) + " and " + str(highNum)
								print(response)
							elif theNum == 36: #PERFECT ACT
								theType = "ACT"
								notTheType = "SAT"
								response = "1600"
							elif theNum == 1600: #PERFECT SAT
								theType = "SAT"
								notTheType = "ACT"
								response = "36"
							elif theNum >= 560 and theNum < 1600: #SAT provided
								nearScore = min(SATscores, key=lambda x:abs(x - theNum))
								print(nearScore)
								theIndex = SATscores.index(nearScore)
								if nearScore > theNum:
									theIndex = theIndex - 1
								ACT = ACTscores[theIndex]	
								theType = "SAT"
								notTheType = "ACT"
								response = str(ACT)
								print(response)
							else: 
								print("Invalid number provided")
								theType = "invalid"
								notTheType = "invalid"
								response = "invalid"
								print(response)
							reply_text = REPLY_TEMP + theType + REPLY_TEMP2 + notTheType + REPLY_TEMP3 + response + REPLY_TEMP4
							print(reply_text)
							comment.reply(reply_text)
							print(comment.permalink())
							cursor.execute("""INSERT INTO comments
									(link)VALUES(?)""", (comment.permalink(),))
							db.commit()
							break


if __name__ == '__main__':
	main()