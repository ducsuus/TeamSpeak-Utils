# To go at top of file etc
import telnetlib
import time
from threading import Timer

host = "ducsuus.com"
port = "10011"

password = "yHYtaVwx"

channel_poll_interval = 60 * 5
sort_channel_interval = 60 * 60
client_average_count = int((sort_channel_interval * 3) / channel_poll_interval)

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

            t.write(("channeledit cid=" + str(channel_name) + " channel_order=1727" + "\n").encode())

            time.sleep(1)

        t.write(("quit\n").encode())

        return True

    except Exception as e:

        print("An error occured;" + str(e))

        return False

# Split up a key name and value; "joe=value" returns (joe, value)
def get_value(string):

    key_name = ""
    key_value = ""
    found_seperator = False
    for character in string:
        if not found_seperator:
            if character == "=":
                found_seperator = True
            else:
                key_name += character
        else:
            key_value += character
    return(key_name, key_value)

def update_channel_clientcount_dict(channellist_response):

    for channel_info in channellist_response.split("|"):

        channel_tags = channel_info.split(" ")

        try:

            channel_name = ""
            channel_id = ""
            channel_clients = 0

            channel_applicable = False

            for tag in channel_tags:

                key_name, key_value = get_value(tag)

                if key_name == "channel_name":

                    channel_name = key_value

                    if channel_name[0:3] == "[b]":

                        channel_applicable = True

                elif key_name == "cid":

                    channel_id = key_value

                elif key_name == "total_clients":

                    channel_clients = int(key_value)

            if channel_applicable and not channel_id == "":

                if channel_id in channel_clientcount_dict:

                    channel_clientcount_dict[channel_id].append(channel_clients)

                else:

                    channel_clientcount_dict[channel_id] = [0] * 9 + [channel_clients]

        except Exception as e:

            print("An error occured; " + str(e))

def sort_average_clientcount(channel_clientcount_dict):

    channel_clientcount_average_dict = {}

    for channel_id in channel_clientcount_dict:

        channel_clientcount_average_dict[channel_id] = sum(channel_clientcount_dict[channel_id]) / len(channel_clientcount_dict[channel_id])

    channel_clientcount_sorted_list = sorted(channel_clientcount_average_dict, key=channel_clientcount_average_dict.get)

    return channel_clientcount_sorted_list

## Begin actual program

channel_clientcount_dict = {}

def poll_channels_thread():

    update_channel_clientcount_dict(get_channel_info())

    for channel_id in channel_clientcount_dict:

        while len(channel_clientcount_dict[channel_id]) > 10:

            channel_clientcount_dict[channel_id].pop(0)

    poll_channels_timer = Timer(channel_poll_interval, poll_channels_thread)
    poll_channels_timer.start()

    print(str(channel_clientcount_dict))
    
def sort_channels_thread():

    sort_channels(sort_average_clientcount(channel_clientcount_dict))

    sort_channels_timer = Timer(sort_channel_interval, sort_channels_thread)
    sort_channels_timer.start()

    print("Debug: sorted channels")
    
poll_channels_timer = Timer(channel_poll_interval, poll_channels_thread)
poll_channels_timer.start()

sort_channels_timer = Timer(sort_channel_interval, sort_channels_thread)
sort_channels_timer.start()


print("        Done?")
