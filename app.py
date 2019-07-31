# import Python Library
from flask import Flask, session, escape, render_template, request,redirect, url_for
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
import mysql.connector
#import speech_recognition as sr
import requests
import re
import webbrowser
import os


#-------Flask App -------
app = Flask(__name__)

userInputs = [None]


#============= Fuctions for Various of Query =========

def u():
    return userInputs[len(userInputs)-2 ]


""" def voice(value):
    import pyttsx3

    def speak(value):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate-30)
        engine.say(value)
        engine.runAndWait()

    speak(value) """

""" def myCommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio).lower()

    #loop back to continue to listen for commands if unrecognizable speech is received
    except sr.UnknownValueError:
        command = myCommand()

    return command """

#-------------- Google API ------------

def call(user):
    try:
        list_data = []

        query = user

        list_data.append(query)

        from googleapiclient.discovery import build

        # Google API Key
        my_api_key = "your-google-API-key"
        # Custome Search Engine Key
        my_cse_id = "your-cse-id"

        def google_search(search_term, api_key, cse_id, **kwargs):

            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()

            return res

        re = google_search(query, my_api_key, my_cse_id)

        ans = []

        for i in range(2):
            ans.append(f"Title : {re['items'][i]['title']}<br>Url : <a href='{re['items'][i]['link']}' target='_blank' style='color:black'>{re['items'][i]['link']}</a><br>Description : {re['items'][i]['snippet']}<br><br>")

        ans = ''.join(ans)

        list_data.append(ans)

        trBot = ChatBot("Erica")

        trBot.set_trainer(ListTrainer)
        trBot.train(list_data)

        return ans
        
    except:
        return "Nework not found!"


#------------Image Result ----------------------
def imgSearch(user):
    import requests, json 

    query = user.replace(' ','+')

    response = requests.get(f"https://www.googleapis.com/customsearch/v1?key=<google-image-api>&cx=cse-id&q={user}") 
        
    x = response.json()

    a = (x['items'][0]['pagemap']['cse_image'][0]['src'])

    return f"<img src={a} height='300' width='400'>"

#------------ Weather API (openweathermap.org) -------------
def weather(user):
    import requests, json 
    import place

    try:
        def getWeather(city_name="Delhi"):

            response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?appid=<openweatherAPI>&q={city_name}") 
            
            x = response.json()
            
            if x["cod"] != "404":
                return (f"City : {city_name}<br>Temp : {(x['main']['temp'])-273.15}°C<br>Pressure : {x['main']['pressure']}<br>Humidity : {x['main']['humidity']}%<br>weather : {x['weather'][0]['description']}")
            else: 
                return (" City Not Found ")


        return getWeather((place.place(user))[0])

    except:
        return "Network not Found!!"
    

# ----------- Places(Hosoital, Restaurant, Temple etc.) in google map API -------------
def getPlace(user):
    import requests, json 

    query = user.replace(' ','+')

    def rest(query):
        a = []

        response = requests.get(f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key=<google map api key>") 
        
        x = response.json()
        
        if len(x['results']) < 5:
            for i in range(len(x['results'])):
                b = {'Name' : f"{x['results'][i]['name']}",
                'Address' : f"{x['results'][i]['formatted_address']}<br>"}
                a.append(b)
        else:
            for i in range(5):
                b = {'Name' : f"{x['results'][i]['name']}",
                'Address' : f"{x['results'][i]['formatted_address']}<br>"}
                a.append(b)
				
        return a
    
    return rest(query)


#------------- Google Map Direction Matrix API ------
def Dir(user):
    import requests, json
    import place

    dirB = f"{place.place(user)[0]}/{place.place(user)[1]}"
    r = requests.get(f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={place.place(user)[0]}&destinations={place.place(user)[1]}&key=AIzaSyAfQeZUuGOH0_7YIzbmHX94aWVl4Xj363o")

    x = r.json()

    string = f"From : {''.join(x['origin_addresses'])}<br>To : {''.join(x['destination_addresses'])}<br>Distance : {x['rows'][0]['elements'][0]['distance']['text']}<br>Duration : {x['rows'][0]['elements'][0]['duration']['text']}<br><a href='https://www.google.com/maps/dir/{dirB}' target='_blank' style='color:black'>Click to see in Google Map</a>"

    return string
    
# ------------ Open a Software that installed in 'C - Drive' by user command------
def openFile(user):
    import subprocess
    import os, fnmatch
    
    d = user.split(' ')
    c = d[len(d)-1]
    # This is to get the directory that the program  
    # is currently running in. 
    path = 'C:\Program Files (x86)'

    def find(pattern, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result

    try:
        subprocess.call(find(f'{c}.exe', path))
        return "<font color='green'>Your file is opend Successfully.</font>"
    except:
        return "<font color='red'>File not found!.</font>"

# ============== End of Functions =========


# ============= Database Connection =============
mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    database = 'rist'
)

# -------- Object declare of MySql Database --------
cur = mydb.cursor()


# =========== ChatterBot Object Creation =========
Bot = ChatBot(
    "Ericka",
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace',
        'chatterbot.preprocessors.unescape_html',
        'chatterbot.preprocessors.convert_to_ascii'
    ],
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    logic_adapters=[
        "chatterbot.logic.MathematicalEvaluation",
        'chatterbot.logic.BestMatch',
        {
            'import_path': 'chatterbot.logic.LowConfidenceAdapter',
            'threshold': 0.65,
            'default_response': "Sorry I have no idea. But I can try from another source. Can I? If I then reply `yes you can.`"
        }
    ]
)


# ============ Trainer ========================

"""for file in os.listdir('./data/'):
	Bot.set_trainer(ChatterBotCorpusTrainer)
	Bot.train('./data/'+file)
	print("Training completed")"""

	
# ============ Starting Main Web Application using Python Flask =============

# ---------- Redirect to main IP ----------
@app.route('/')
def Home(message=None):
    if message==None:
        return render_template('home.html')
    else:
        return render_template('register.html', message="signup succesfull")

@app.route('/logged_in')
def logged_in():
	if session['logged_in'] == False:
		return render_template('home.html')
	else:
		return render_template('index.html')

# ------------- Signup Page for new users ----------

@app.route('/signup')
def sign():
    return render_template('signup.html')

# -------------- Success Page ---------
@app.route('/success')
def success():
    return render_template('success.html', message = 'Signup Successful')


# ------------- Signup page with MySql ----------
# ------------- New user can register in Database -----

@app.route('/signup', methods=['POST'])
def signup():
	if request.form['name'] != '' and request.form['email'] != '' and request.form['dob'] != '' and request.form['Gender'] != '' and request.form['password'] != '':
		val = (request.form['name'], request.form['email'], request.form['dob'], request.form['Gender'], request.form['password'])
		sql = "INSERT INTO `rist`.`register` (`Name`, `Email id`, `Date of Birth`, `Gender`, `Password`) VALUES (%s, %s, %s, %s, %s)"

		cur.execute(sql, val)
		mydb.commit()
		
		return redirect(url_for('register'))
	else:
		return render_template('signup.html', message = 'Fill All Elements!')


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/register')
def register():
    return render_template('register.html')


# ------------ Main Bot Response Function ----------

@app.route("/get")
def get_bot_response():

	if session['logged_in'] == True:
		userText = request.args.get('msg')

		userInputs.append(userText)
		
		# use token values
		# Bot can give answer for GK or other questions That can't know bot
		if 'yes you can' in userText.lower() or 'yes u can' in userText.lower() or 'Yes' in userText.lower():
			return str(call(u()))

		# Bot Search restaurent near location via google map api
		elif 'restaurant' in userText.lower() or 'pizza hut' in userText.lower() or 'domino' in userText.lower() or 'kfc' in userText.lower() or 'McDonald' in userText.lower():
			c = []
			a = (getPlace(userText))
			for i in a:
				for j,k in i.items():
					c.append(f"{j} : {k}<br>")
			return str(''.join(c))
		
		# Bot Search Temple near location via google map api
		elif 'temple' in userText.lower() or 'mandir' in userText.lower() or 'mondir' in userText.lower():
			c = []
			a = (getPlace(userText))
			for i in a:
				for j,k in i.items():
					c.append(f"{j} : {k}<br>")
			return str(''.join(c))


		# Bot Search Shops near location via google map api
		elif 'shop' in userText.lower().lower() or 'shoping' in userText.lower():
			c = []
			a = (getPlace(userText))
			for i in a:
				for j,k in i.items():
					c.append(f"{j} : {k}<br>")
			return str(''.join(c))


		# Bot Search Hospitals near location via google map api
		elif 'hospital' in userText.lower():
			c = []
			a = (getPlace(userText))
			for i in a:
				for j,k in i.items():
					c.append(f"{j} : {k}<br>")
			return str(''.join(c))

		# Bot Search direction, Distance via google map api
		elif 'direction' in userText.lower() or 'distance' in userText.lower():
			return str(Dir(userText))


		# Weather Report API
		elif 'weather' in userText.lower() or 'temp' in userText.lower() or 'tempareture' in userText.lower():
			return str(weather(userText))

		elif 'image' in userText.lower() or 'img' in userText.lower() or 'photo' in userText.lower() or 'picture' in userText.lower() or 'pic' in userText.lower():
			return str(imgSearch(userText))

		elif 'today' in userText.lower():
			userText = userText.replace("today", f"{x.strftime('%A')}")
			return str(Bot.get_response(userText))

		elif 'open website' in userText.lower():
			reg_ex = re.search('open website (.+)', userText.lower())
			if reg_ex:
				domain = reg_ex.group(1)
				url = 'https://www.' + domain
				webbrowser.open(url)
				return "Done!"
			else:
				pass

		else:
			s = str(Bot.get_response(userText))
			return s
	else:
		return render_template('register.html', wid = '400px')
		

# ---------- Render Template (register.html) or Login Page ------
@app.route('/login', methods=['POST'])
def Login():
	val = (request.form['email'], request.form['password'])
	sql = "select count(*) FROM `rist`.`register` WHERE `Email id` = %s AND `Password` = %s"
    
	cur.execute(sql, val)
	res = cur.fetchone()

	if res[0] == 1:
		sql = "SELECT `Name`, `Email id`, `password` FROM `rist`.`register` WHERE `Email id` = %s AND `Password` = %s"
		cur.execute(sql, val)
		res = cur.fetchone()
        
		if request.form['email'] == res[1] and request.form['password'] == res[2]:
			session['logged_in'] = True
			session['username'] = res[0]
			return redirect(url_for('logged_in'))
		else:
		    return render_template('register.html', message = "Wroung user or Password")
	else:
		return render_template('register.html', message = 'Wroung user or Password')


@app.route('/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('logged_in'))
	

app.secret_key = 'rdj'


# End of Flask
if __name__ == "__main__":
    app.run()
