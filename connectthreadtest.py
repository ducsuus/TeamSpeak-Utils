def check_login():

    import telnetlib
    import time

    server_address = "ducsuus.com"
    server_port = 10011
    server_id = "1"
    server_password = "1jDWe8sF"


    try:

        command_list = ["login serveradmin " + server_password,
                        "use " + str(server_id),
                        "channellist"]

        t = telnetlib.Telnet(server_address, str(server_port))

        print("Details (in check_login()): " + str(server_address) + " " + str(server_port))

        # Clear the console
        t.read_very_eager()

        for command in command_list:

            t.write((command + "\n").encode())

            time.sleep(1)

            command_response = t.read_very_eager().decode()

            # If this is command was not successful then return False, it failed
            if command_response != "error id=0 msg=ok":

                error_message = "command: " + command + " response: " + command_response

                t.write(("quit\n").encode())

                return error_message

        t.write(("quit\n").encode())

    except Exception as e:

        print("An error occured in check_login() while trying to check the login details: " + str(e))

        return False

    # All details supplied work, the program can continue
    return True

print(str(check_login()))