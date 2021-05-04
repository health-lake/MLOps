import requests 

res = requests.get("http://b85027be74b9.ngrok.io/")
print(res.content)