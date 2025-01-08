import time
import os
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import pandas_datareader as pdr
from bs4 import BeautifulSoup
import requests
import feedparser 

# 음성 인식 STT
def listen(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language='ko')
        print('[답변] '+ text)
        answer(text)
    except sr.UnknownValueError:
        print('인식 실패') # 음성 인식 실패한 경우
    except sr.RequestError:
        print('요청 실패 : {0}'.format(0)) # API Key 오류, 네트워크 단절 등

# 읽기 TTS
def speak(text):
    print('[인공지능] '+ text)
    file_name = 'voice.mp3'
    tts = gTTS(text=text, lang='ko')
    tts.save(file_name)
    playsound(file_name)
    if os.path.exists(file_name): # voice.mp3 파일 삭제
        os.remove(file_name)

# 환율
df = pdr.get_data_fred("DEXKOUS")
rate = df["DEXKOUS"][-1]

# 날씨 가져오기 함수
def get_weather(address):
    try:
        html = requests.get(f'https://search.naver.com/search.naver?query={address}+날씨')
        soup = BeautifulSoup(html.text, 'html.parser')
        
        # 주소
        address = soup.find('div', {'class':'title_area _area_panel'}).find('h2', {'class':'title'}).text
        
        # 날씨 데이터
        weather_data = soup.find('div', {'class':'weather_info'})
        # 날씨 정보
        temperature = weather_data.find('div', {'class':'temperature_text'}).text.strip()[5:]
        # 날씨 상태
        weatherStatus = weather_data.find('span',{'class':'weather before_slash'}).text
        # 공기 상태
        air = soup.find('ul', {'class':'today_chart_list'})
        
        result = f'{address}의 현재 온도는 {temperature}이며, 날씨 상태는 {weatherStatus}입니다. 또한 미세먼지는 {air.text.strip()[5:7]}입니다'
        speak(result)
    except Exception as e:
        speak("죄송합니다. 날씨 정보를 가져오는 중에 오류가 발생했습니다.")
        answer('날씨')

def my_news() :                                               
    url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    news_data = []                                            
    news_rss = feedparser.parse(url)                          
    for title in news_rss.entries :                           
        news_data.append(title.title)                         
    return news_data                                          

def get_stock(stock):
    try:
        html = requests.get(f'https://search.naver.com/search.naver?query={stock}+주가')
        soup = BeautifulSoup(html.text, 'html.parser')

        # 주소
        price = soup.find('span', {'class':'spt_con dw'}).text.strip()[2:9]

        speak(f'{stock}의 주가는 {price}원 입니다.')
    except Exception as e:
        speak("죄송합니다. 주식 정보를 가져오는 중에 오류가 발생했습니다.")
        answer('주가')


# 대답
def answer(input_text):
    if '안녕' in input_text:
        speak('안녕하세요? 반갑습니다.')
    elif '날씨' in input_text:
        speak('어느 지역의 날씨를 알려드릴까요?')
        # 사용자로부터 동네 입력 받기
        with sr.Microphone() as source:
            speak("동네를 말해주세요")
            audio = r.listen(source)            
        try:
            user_address = r.recognize_google(audio, language='ko')
            print('[답변] '+ user_address)
            get_weather(user_address)
        except sr.UnknownValueError:
            speak("죄송합니다. 음성을 인식하지 못했습니다.")
        except sr.RequestError:
            speak("죄송합니다. 음성을 처리하는 중에 오류가 발생했습니다.")
    elif '환율' in input_text:
        speak(f'원 달러 환율은 {rate}원입니다.')
    elif '뉴스' in input_text:
        texts = my_news()                                                          
        speak('오늘 주요 뉴스 세가지를 말씀해드리겠습니다.')                                             
        for text in texts[0:3] :                                                    
            speak(text)    
    elif '주가' or '주식 종목' in input_text:
        speak('어떤 주식의 주가를 알려드릴까요?')
        # 사용자로부터 동네 입력 받기
        with sr.Microphone() as source:
            speak("주식 종목을 말해주세요")
            audio = r.listen(source)            
        try:
            user_address = r.recognize_google(audio, language='ko')
            print('[답변] '+ user_address)
            get_stock(user_address)
        except sr.UnknownValueError:
            speak("죄송합니다. 음성을 인식하지 못했습니다.")
        except sr.RequestError:
            speak("죄송합니다. 음성을 처리하는 중에 오류가 발생했습니다.")
    elif '종료' in input_text:
        speak('다음에 또 만나요')
        stop_listening(wait_for_stop=False) # 더 이상 듣지 않음
    else:
        speak('다시 한번 말씀해주세요')

# 음성 인식 준비
r = sr.Recognizer()
m = sr.Microphone()

# 음성 안내
speak('무엇을 도와드릴까요?')
stop_listening =  r.listen_in_background(m, listen)

# 계속 실행
while True:
    time.sleep(0.1)
