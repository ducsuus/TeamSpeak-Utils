
# To go at top of file etc
import telnetlib
import time

host = "ducsuus.com"
port = "10011"

password = "yHYtaVwx"

# To go at bottom-ish of file etc

def get_channel_info():

    try:

        t = telnetlib.Telnet(host, port)

        t.write(("login serveradmin " + password + "\n").encode())
        t.write(("use 1\n").encode())

        time.sleep(1)

        t.read_very_eager()

        t.write(("channellist" + "\n").encode())

        time.sleep(1)

        channellist_response = t.read_very_eager().decode()

        t.write(("quit\n").encode())

        return channellist_response

    except Exception as e:

        print("An error occured;" + str(e))

        return False
    

def sort_channels(channel_name_list):

    try:

        t = telnetlib.Telnet(host, port)

        t.write(("login serveradmin " + password + "\n").encode())
        t.write(("use 1\n").encode())

        # Note how this list is sorted lowest-highest so that we can easily loop backwards here: we move the lowest applicable channel to the top first, so that the "higher" channels are pushed down 
        for channel_name in channel_name_list:

            t.write(("channeledit cid=" + str(channel_name) + " channel_order=1719" + "\n").encode())

            time.sleep(1)

        t.write(("quit\n").encode())

        return True

    except Exception as e:

        print("An error occured;" + str(e))

        return False
