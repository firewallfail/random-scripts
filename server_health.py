import subprocess, time, sys, getopt, logging
from urllib import request


def send_ntfy(ntfy, auth, msg):
    try:
        data = msg.encode('utf-8')
        req = request.Request(ntfy, data=data)
        req.add_header('Authorization', f"Bearer {auth}")
        with request.urlopen("https://ntfy.barba.link/cghmn_status") as resp:
            return
    except Exception as e:
        logging.exception(e)


def help():
   print("is_server_up.sh: server status change notification script")
   print("\t-h|--help: display this message")
   print("\t-s|--server: required - server to check ping")
   print("\t-n|--ntfy: required - ntfy server to send message to")
   print("\t-t|--token: required - token for ntfy server")
   print("\t-i|--interval: optional - check frequency in minutes, default 5 minutes")
   print("Example: $ python3 server_health.py -s example.com -n https://ntfy.example.com/subscription -t secret_token")


def main(host, ntfy, auth, interval):
    if not host or not ntfy or not auth:
        print("Missing required arg")
        help()
        sys.exit()
    STATUS = True
    UP = 'up'
    DOWN = 'down'
    MESSAGES = {
        'up': 'Server appears to be back up',
        'down': 'Server appears to be down'
    }

    while True:
        message = None
        time.sleep(5)

        # setup ping
        ping = subprocess.Popen(
            ["ping", "-c", "4", host],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )

        out, error = ping.communicate()
        is_bad = '0 received' in out.decode('utf-8')

        if (error or is_bad) and STATUS:
            STATUS = False
            message = MESSAGES[DOWN]
        elif not STATUS and not is_bad:
            STATUS = True
            message = MESSAGES[UP]
        
        if message:
            send_ntfy(ntfy, auth, message)


if __name__ == "__main__":
    FIVE_MINUTES = 5 * 60

    host, ntfy, auth, interval = None, None, None, FIVE_MINUTES

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"hs:n:t:i:", ["help","server=","ntfy=","token=","interval="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()
        elif opt in ('-s', '--server'):
            host = arg
        elif opt in ('-n', '--ntfy'):
            ntfy = arg
        elif opt in ('-t', '--token'):
            auth = arg
        elif opt in ('-i', '--interval'):
            interval = int(arg) * 60
    main(host, ntfy, auth, interval)
