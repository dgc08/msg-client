import requests
import sys

pas = ""
server = "http://192.168.178.90:5000/api"
#uns = "http://192.168.178.90:5000/api/uns"
uns = "http://192.168.178.90:69/openuns"

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def getlines():
    inp = [""]
    while inp[-1] != "\\":
        inp.append( input() )
    print("Sending message...")
    ret = "\n".join(inp[:-1])
    return ret.replace("\\\\", "\\").strip()

def simple_getter(route, args, json=False, custom_server = None):
    if custom_server is None:
        custom_server = server
    x = requests.get(custom_server+route, params=args)
    if x.status_code == 200 and json:
        return x.json()
    elif x.status_code == 200:
        return x.text
    return None

def uns_resolve (name: str):
    ret = simple_getter("/get/name", {"name": name}, False, uns)
    if ret is None:
        return None

    if ret.strip() == "":
        ret = None
    return ret

def uns_send(args):
    name = args[1]
    args[1] = uns_resolve(args[1])
    if args[1] == None:
        print("User not found. check spelling and uns server")
        return
    else:
        print("Found address on", name)
    hash_send(args)

def hash_send(args):
    if not query_yes_no("Sending to the hash address " + args[1] + ", is this correct?"):
        print("Ok, no problem")
        return True
    print("Please put in your message:")
    msg = getlines()
    res = simple_getter("/send", {"password" : pas, "msg" : msg.strip("\n"), "recipient": args[1]})
    if res != "0":
        print("Could not send Message, api returned", res)
    else:
        print("Message sended.")

    return True

def recive(args):
    print("Pulling new messages...\n")
    msgs = simple_getter("/check", {"password" : pas}, True)
    if msgs is None:
        print("Fetching messages failed.")
        return True
    counter = 1
    print("You gotta", len(msgs), "messages!")
    for i in msgs:
        print("You gotta message from", i["from"], ":\n")
        print(i["content"])
        print("\nMessage", counter,"end.")
    print("Messages end.")
    return True

def command_processor():
    try:
        inp = input("> ")
    except KeyboardInterrupt:
        print()
        return True

    if inp == "exit" or inp == "e":
        return False

    args = inp.split(" ")
    args.append("")
    if args[0] == "hash.send":
        return hash_send(args)
    if args[0] == "hs":
        return hash_send(args)
    if args[0] == "fetch":
        return recive(args)
    if args[0] == "f":
        return recive(args)
    if args[0] == "logout":
        global pas
        pas = input("Welcome to the client. Please authenticate: ")
        print("Logged in as", simple_getter("/getusr", {"password": pas}))
    if args[0] == "us" or args[0] == "uns.send":
        uns_send(args)
    if args[0] == "server":
        global server
        server = args[1]
    if args[0] == "uns_server":
        global uns
        uns = args[1]
    if args[0] == "test":
        pass
        exec (input())


    return True


pas = input("Welcome to the client. Please authenticate: ")
print("Logged in as", simple_getter("/getusr", {"password": pas}))

while command_processor():
    pass
