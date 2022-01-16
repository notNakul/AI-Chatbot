from tkinter import *
import os
import datetime
import webbrowser
import pywhatkit as kt
import pyttsx3
import random
import json
from keras.models import load_model
import re
import speech_recognition as sr
import wikipedia as wk
import numpy as np
import pickle
import nltk
from nltk.stem import WordNetLemmatizer
# import smtplib
lemmatizer = WordNetLemmatizer()
model = load_model('chatbot_model.h5')

intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

engine = pyttsx3.init()


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return(np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag'] == tag):
            result = random.choice(i['responses'])
            break

    return result


def wikipedia_data(input):
    reg_ex = re.search('wikipedia (.*)', input)
    try:
        if reg_ex:
            topic = reg_ex.group(1)
            wiki = wk.summary(topic, sentences=2)
            return wiki
    except Exception as e:
        return("No content has been found")


def chatbot_response(msg):
    msg = msg.lower()
    # if re.search("A\jess",msg):
    # msg=msg.replace("jess","")
    if("wikipedia " in msg):
        if msg:
            wiki_response = wikipedia_data(msg)
            result = wiki_response
    elif "time in india" in msg:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        result = f"The time is {strTime}"
    elif "open youtube" in msg:
        webbrowser.open("youtube.com")
        result = "Opening youtube"
    elif "open google" in msg:
        webbrowser.open("google.com")
        result = "Opening google"
    elif "open stack overflow" in msg:
        webbrowser.open("stackoverflow.com")
        result = "Opening stackoverflow"
    elif "google" in msg:
        target = msg
        tr = target.lower()
        tr2 = tr.replace("google ", "")
        # print(tr)
        # print(tr2)
        result = f"showing desired result for {tr2}"
        kt.search(tr2)
    elif "open epic games" in msg:
        file_dir = "C:\\Program Files (x86)\\Epic Games\\Launcher\\Portal\\Binaries\\Win32\\EpicGamesLauncher.exe"
        os.startfile(file_dir)
        result = "Opening epic games"
    elif "open teams" in msg:
        file_dir = "C:\\Users\\nakul\\AppData\\Local\\Microsoft\\Teams\\current\\Teams.exe"
        os.startfile(file_dir)
        result = "Opening ms teams"
    elif "open spotify" in msg:
        music_dir = "C:\\Users\\nakul\\AppData\\Roaming\\Spotify\\Spotify.exe"
        os.startfile(music_dir)
        result = "Opening spotify"
    elif "play some music" in msg:
        music_dir = "C:\\Users\\nakul\\AppData\\Roaming\\Spotify\\Spotify.exe"
        os.startfile(music_dir)
        result = "Opening spotify"
    elif "play a local song" in msg:
        music_dir = "C:\\Users\\nakul\\Downloads\\son.mp4"
        os.startfile(music_dir)
        result = "Playing song"    
    elif "exit" in msg:
        root.destroy()
    elif "quit" in msg:
        root.destroy()
    else:
        ints = predict_class(msg, model)
        result = getResponse(ints, intents)
    return result


# changing accent
voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0"
engine.setProperty("voice", voice_id)

# creating GUI


def takeCommand():
    # It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)
        print("Say that again please...")
        return "None"
    return query


def listen():
    msg = takeCommand()
    # msg = entrybox.get("1.0",'end-1c').strip()
    # entrybox.delete("0.0",END)
    # lemmatizer.lemmatize(msg.lower())
    if msg != '':
        chatlog.config(state=NORMAL)
        chatlog.insert(END, "You: " + msg + '\n\n')
        # chatlog.config(foreground="#442265", font=("Verdana", 12))

        res = chatbot_response(msg.lower())
        chatlog.insert(END, "Bot: " + res + '\n\n')

        chatlog.config(state=DISABLED)
        chatlog.yview(END)
    engine.setProperty('rate', 170)
    engine.say(res)
    engine.runAndWait()


def send():

    msg = entrybox.get("1.0", 'end-1c').strip()
    entrybox.delete("0.0", END)

    if msg != '':
        chatlog.config(state=NORMAL)
        chatlog.insert(END, "You: " + msg + '\n\n')
        # chatlog.config(foreground="#442265", font=("Verdana", 12))

        res = chatbot_response(msg)
        chatlog.insert(END, "Bot: " + res + '\n\n')

        chatlog.config(state=DISABLED)
        chatlog.yview(END)
    engine.setProperty('rate', 170)
    engine.say(res)
    engine.runAndWait()


BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

root = Tk()
root.title("Chatbot")
root.configure(width=470, height=550, bg=BG_COLOR)
root.resizable(width=False, height=False)

chatlog = Text(root, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR,
               font=FONT, padx=5, pady=5)
chatlog.config(cursor="arrow", state=DISABLED)

entrybox = Text(root, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
entrybox.bind("<Return>", send)

sendbutton = Button(root, text="Send", font=FONT_BOLD,
                    width=20, bg=BG_GRAY, command=send)
listenbutton = Button(root, text="Listen",  font=FONT_BOLD,
                      width=20, bg=BG_GRAY, command=listen)

chatlog.place(relheight=0.75, relwidth=1, rely=0.08)
entrybox.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
sendbutton.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
listenbutton.place(relx=0, rely=0.9, relheight=0.1, relwidth=1)

root.mainloop()


# def sendEmail(to, content):
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.ehlo()
#     server.starttls()
#     server.login('dummyg20201@gmail.com', 'rU6:!9cN-Cv3JTG')
#     server.sendmail('dummyg20201@gmail.com', to, content)
#     server.close()

# else:
#     result="Please call me by my name"
#     return result
# elif "send an email" in msg:
#     try:
#         engine.say("What should I say?")
#         content = takeCommand()
#         to = "dummyg20201@gmail.com"
#         sendEmail(to, content)
#         result = "Email has been sent"
#     except Exception as e:
#         print(e)
#         result = "Sorry, I am not able to send this email"


# root = Tk()
# root.title("Chatbot")
# root.geometry('500x500')
# root.resizable(width=TRUE, height=TRUE)

# chatlog = Text(root, bg="#ffc787", fg="#e3be18")
# chatlog.config(state=DISABLED)

# entrybox = Text(root, bg="#f2a750")
# entrybox.bind("<Return>", send)

# sendbutton = Button(root, text="Send", bg="#ab7409", activebackground="#634508",
#                     activeforeground="#fffdfa", fg="#290000", command=send)
# listenbutton = Button(root, text="Listen", bg="#ab7409", activebackground="#634508",
#                       activeforeground="#fffdfa", fg="#290000", command=listen)

# chatlog.grid(row=0, column=0, sticky="nsew")
# entrybox.grid(row=1, column=0, sticky="nsew")
# sendbutton.grid(row=1, column=0, sticky="ns", ipadx=30)

# listenbutton.grid(row=1, column=0, sticky="nse", ipadx=80)

# Grid.columnconfigure(root, 0, weight=2)
# Grid.rowconfigure(root, 0, weight=10)
# Grid.rowconfigure(root, 1, weight=7000)


# root.mainloop()


# Creating GUI with tkinter
# import tkinter
# from tkinter import *


# def send():
#     msg = EntryBox.get("1.0",'end-1c').strip()
#     EntryBox.delete("0.0",END)

#     if msg != '':
#         ChatLog.config(state=NORMAL)
#         ChatLog.insert(END, "You: " + msg + '\n\n')
#         ChatLog.config(foreground="#442265", font=("Verdana", 12 ))

#         res = chatbot_response(msg)
#         ChatLog.insert(END, "Bot: " + res + '\n\n')


#         ChatLog.config(state=DISABLED)
#         ChatLog.yview(END)
#     engine.setProperty('rate', 150)
#     engine.say(chatbot_response(msg))
#     engine.runAndWait()

# base = Tk()
# base.title("Not so subtle Chatbot")
# base.geometry("50x50")
# base.resizable(width=TRUE, height=TRUE)

# #Create Chat window


# ChatLog = Text(base, bd=0, bg="red",  font="Arial")
# # ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial")

# ChatLog.config(state=DISABLED)

# #Bind scrollbar to Chat window
# scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
# ChatLog['yscrollcommand'] = scrollbar.set

# #Create Button to send message
# SendButton = Button(base, font=("Verdana",12,'bold'), text="Send",
#                     bd=0, bg="#6a04b8", activebackground="#490180", activeforeground="#490180" ,fg='#ffffff',
#                     command= send )
# # SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
# #                     bd=0, bg="#6a04b8", activebackground="#490180", activeforeground="#490180" ,fg='#ffffff',
# #                     command= send )

# #Create the box to enter message
# EntryBox = Text(base, bd=0, bg="white", font="comicsansms")
# # EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="comicsansms")
# EntryBox.bind("<Return>", send)


# #Place all components on the screen

# ChatLog.grid(row=0 ,sticky="ew")
# # scrollbar.grid(row=0,column=0 ,sticky="nsew")
# EntryBox.grid(row=1,column=0 ,sticky="nsw")
# SendButton.grid(row=1,column=1 ,sticky="nse")


# # scrollbar.place(x=376,y=6, height=386)
# # ChatLog.place(x=6,y=6, height=386, width=370)
# # EntryBox.place(x=128, y=401, height=90, width=265)
# # SendButton.place(x=6, y=401, height=90)


# # Grid.columnconfigure(base, 0,weight=1)
# # Grid.columnconfigure(base, 1,weight=100)
# # Grid.rowconfigure(base, 0,weight=1)
# # Grid.rowconfigure(base, 1,weight=600)
# # ChatLog.pack(fill="y")

# base.mainloop()
