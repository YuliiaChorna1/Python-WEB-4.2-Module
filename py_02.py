import urllib.request

with urllib.request.urlopen("https://www.python.org/") as f:
    print(f.read(300))

# перші 300 байт HTML документа на головній сторінці https://www.python.org/