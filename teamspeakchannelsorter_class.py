
class channelsorter_teamspeak_instance:

    from threading import Timer
    import telnetlib


    # TODO: fix this and remove all timers when the flooding is removed from the server
    import time

    # Dictonary to keep track of each channel's score
    channel_scores = {}

    query_welcome_message = "TS3\n\rWelcome to the TeamSpeak 3 ServerQuery interface, type \"help\" for a list of commands and \"help <command>\" for information on a specific command.\n\r".encode()
    query_generic_success_message = "error id=0 msg=ok\n\r".encode()

    query_command_timeout = 1

    def __init__(self, server_address, server_port, server_username, server_password, server_id, channel_poll_time = 300, channel_update_time = 3600, channel_poll_backlog = 10):

        # Server details
        self.server_address = server_address
        self.server_port = server_port
        self.server_username = server_username
        self.server_password = server_password
        self.server_id = server_id

        self.channel_poll_time = channel_poll_time # Default 5 minutes
        self.channel_update_time = channel_update_time # Default 60 minutes
        self.channel_poll_backlog = channel_poll_backlog # Default 10 scores

        check_login_result = self.check_login()

        if check_login_result:

            self.details_compatible = True

            self.running = True

            print("Details worked")

        else:

            self.details_compatible = False

            self.running = False

            print("Details did not work; failed on: " )

            return None

        # Setup threading

        # Channel polling
        self.poll_channels_timer = self.Timer(self.channel_poll_time, self.poll_channels_thread)
        self.poll_channels_timer.start()

        # Channel sorting (3 sec delay to avoid potential flooding)
        self.order_channels_timer = self.Timer(self.channel_update_time + 3, self.order_channels_thread)
        self.order_channels_timer.start()

    def check_login(self):

        try:

            command_list = ["login " + self.server_username + " " + self.server_password,
                            "use " + str(self.server_id),
                            "channellist"]

            t = self.telnetlib.Telnet(self.server_address, str(self.server_port))

            welcome_response = t.read_until(self.query_welcome_message, timeout=self.query_command_timeout)

            if welcome_response != self.query_welcome_message:

                return "command: connecting to server response: " + welcome_response.decode()

            for command in command_list:

                t.write((command + "\n").encode())

                command_response = t.read_until(self.query_generic_success_message, timeout=self.query_command_timeout)

                # If this is command was not successful then return False; it failed
                if command_response != self.query_generic_success_message:

                    t.write(("quit\n").encode())

                    error_message = "command: " + command + " response: " + command_response.decode()

                    return error_message

            t.write(("quit\n").encode())

        except Exception as e:

            print("An error occured in check_login() while trying to check the login details: " + str(e))

            return False

        # All details supplied work, the program can continue
        return True

    def poll_channels_thread(self):

        if self.running:

            try:

                status, response = self.poll_channels()

                if status:

                    print("Successfully polled channels.")

                else:

                    print("A command didn't get the expected response in the poll_channels_thread; the server responded: " + response)

                self.poll_channels_timer = self.Timer(self.channel_poll_time, self.poll_channels_thread)
                self.poll_channels_timer.start()

            except Exception as e:

                print("An error occured in the poll_channels_thread. This needs attention!: " + str(e))

                return False

    def order_channels_thread(self):

        if self.running:

            try:

                status, response = self.order_channels()

                if status:

                    print("Successfully ordered channels.")

                else:

                    print("A command didn't get the expected response in the order_channels_thread; the server responded: " + response)

                self.order_channels_timer = self.Timer(self.channel_update_time, self.order_channels_thread)
                self.order_channels_timer.start()

            except Exception as e:

                print("An error occured in the order_channels_thread. This needs attention!: " + str(e))

                return False

    def poll_channels(self):

        # Count all of the subchannels, and the number of clients in those channels, based on a channel (and its channel id)
        # Needs access to the channel_list variable, specific to this function
        def count_channel(target_channel_id):

            channel_client_count = channel_list[target_channel_id][2]
            channel_subchannel_count = 0

            for channel_id in channel_list:

                if channel_list[channel_id][1] == target_channel_id:

                    # Python does not allow multiple values to be added to multiple variables returned from a function,
                    # so they have to be assigned to a new variable first, then added onto the "target" variables.
                    new_channel_client_count, new_channel_subchannel_count = count_channel(channel_id)

                    channel_client_count += new_channel_client_count
                    channel_subchannel_count += new_channel_subchannel_count
            
            return channel_client_count, channel_subchannel_count

        try:

            t = self.telnetlib.Telnet(self.server_address, str(self.server_port))

            command_response = t.read_until(self.query_welcome_message, timeout=self.query_command_timeout)

            if command_response != self.query_welcome_message:

                return False, command_response.decode()

            t.write(("login " + self.server_username + " " + self.server_password + "\n").encode())

            command_response = t.read_until(self.query_generic_success_message, timeout=self.query_command_timeout)

            if command_response != self.query_generic_success_message:

                return False, command_response.decode()

            t.write(("use " + str(self.server_id) + "\n").encode())

            command_response = t.read_until(self.query_generic_success_message, timeout=self.query_command_timeout)

            if command_response != self.query_generic_success_message:

                return False, command_response.decode()

            t.write(("channellist" + "\n").encode())

            # No "no-error" message for this one, read until the server sends a new line and return, then remove those two characters
            channellist_response = t.read_until("\n\r".encode(), timeout=self.query_command_timeout).decode()[:-2]

            t.write(("quit\n").encode())

        except Exception as e:

            print("An error occured in poll_channels() while attempting to retrieve information about the server channels: " + str(e))

            return False

        # A place to store all the channel information received from the server
        # channel_list[channel_id] = [channel_name, channel_pid, channel_clients]
        channel_list = {}

        for channel in channellist_response.split("|"):

            channel_tags = channel.split(" ")

            channel_id = -1
            channel_name = ""
            channel_pid = -1
            channel_clients = -1

            for tag in channel_tags:

                key_name, key_value = self.get_value(tag)

                if key_name == "cid":

                    channel_id = int(key_value)

                elif key_name == "channel_name":

                    channel_name = key_value

                elif key_name == "pid":

                    channel_pid = int(key_value)

                elif key_name == "total_clients":

                    channel_clients = int(key_value)

            if channel_id >= 0 and channel_name != "" and channel_pid >= 0 and channel_clients >= 0:

                channel_list[channel_id] = [channel_name, channel_pid, channel_clients]

        for channel_id in channel_list:

            # If it's a top level channel       and       a beta-participating channel (temp)
            if channel_list[channel_id][1] == 0 and channel_list[channel_id][0][0:3] == "[b]":

                channel_client_count, channel_subchannel_count = count_channel(channel_id)

                # Get the score; the average client per chanel (hence the add one to the subchannel count, so that the parent channel is included)
                channel_score = channel_client_count / (channel_subchannel_count + 1)

                if channel_id in self.channel_scores:

                    self.channel_scores[channel_id].append(channel_score)

                    while len(self.channel_scores[channel_id]) > self.channel_poll_backlog:

                        self.channel_scores[channel_id].pop(0)

                else:

                    self.channel_scores[channel_id] = [0.0] * int(self.channel_poll_backlog - 1) + [channel_score]

        return True, "None: Success!"

    def order_channels(self):

        def average_clientcount(index):
            return sum(self.channel_scores[index]) / len(self.channel_scores[index])

        channel_score_average_list = sorted(self.channel_scores, key=average_clientcount)

        try:

            t = self.telnetlib.Telnet(self.server_address, str(self.server_port))

            command_response = t.read_until(self.query_welcome_message, timeout=self.query_command_timeout)

            if command_response != self.query_welcome_message:

                return False, command_response.decode()

            t.write(("login " + self.server_username + " " + str(self.server_password) + "\n").encode())

            command_response = t.read_until(self.query_generic_success_message, timeout=self.query_command_timeout)

            if command_response != self.query_generic_success_message:

                return False, command_response.decode()

            t.write(("use " + str(self.server_id) + "\n").encode())

            command_response = t.read_until(self.query_generic_success_message, timeout=self.query_command_timeout)

            if command_response != self.query_generic_success_message:

                return False, command_response.decode()

            # channel_score_average_list sorted backwards so lowest channels can be updated first
            for channel_id in channel_score_average_list:

                t.write(("channeledit cid=" + str(channel_id) + " channel_order=1727" + "\n").encode())

                # Channels which the bot does not have permission to move will give an error, and as this is a low-priority task, errors for this shouldn't matter
                command_response = t.read_until("\n\r".encode(), timeout=self.query_command_timeout)

                # Temp: should be removed once the anti-flood part of the server is removed (TODO)
                self.time.sleep(0.31)

            t.write(("quit\n").encode())

        except Exception as e:

            error_message = "An error occured in order_channels() while trying to move channels about: " + str(e)

            return False, error_message

        return True, ""

    # Get a key and its value from a string in the form "key=value"
    def get_value(self, string):

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

#server_address, server_port, server_username, server_password, server_id, channel_poll_time = 300, channel_update_time = 3600, channel_poll_backlog = 10

server_address = "ducsuus.com"
server_port = 10011
server_username = "serveradmin"
server_password = "1jDWe8sF"
server_id = 1
channel_poll_time = 60 * 5
channel_update_time = 60 * 60
channel_poll_backlog = int(channel_update_time / channel_poll_time) * 24)

ducsuus_teamspeak = channelsorter_teamspeak_instance(server_address,
                                                    server_port,
                                                    server_username,
                                                    server_password,
                                                    server_id,
                                                    channel_poll_time,
                                                    channel_update_time,
                                                    channel_poll_time)

if ducsuus_teamspeak.details_compatible:

    print("Success!")

    input("press enter to stop running")

    ducsuus_teamspeak.running = False

    exit()

else:

    print("Didn't work :(")