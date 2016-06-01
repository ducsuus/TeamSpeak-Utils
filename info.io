# info.io - Information about the TeamSpeak Channel Sorter

# Direction

As of writing, TCS has basic functionality to sort channels on a timely basis as specified by a given variable, the following changes should be made/implemented.

    - Checking how many subchannels each channel on the server has.
        Currently someone could have an infinite number of subchannels to there channel, and still be voted to the top. The average user for a channel should be produced by the equation: (sum of users in channels and all subchannels) / (number of subchannels + 1). (+1 in order to account for the top level channel itself). 

        In order to implement this, a channel tree will need to be produced, as each subchannel and have additional subchannels.

        A channel tree being produced will also allow for the amount of users in each subchannel to be added on to the total number of users in the top level channel.

    - Whitelisting and blacklisting of channels.
        Some channels (eg the lobby, spacers) should not be moved at all, and as such a system to not-use these channels should be implemented.

        Perhaps an opt-in system would be best:

            Opt-in:
                Users manually opt in to channels, perhaps by registering their channel online? There isn't really a good place to do this from within TeamSpeak that won't effect operation of TeamSpeak itself (eg the channel description needs to be used for stuff other than channel tags).

            Automatic:
                All channels but those specified will need to be organised. The problem with this method is that if new channels are added at a later date that represent structure to the server, they are going to be moved about. As such a system to clearly define structure channels and user channels will need to be implemented, perhaps by increasing the needed permissions to modify the channel to something higher than the ServerQuery bot has.

    - Stopping people from duping the system.
        Users have already logged in multiple times from the same computer using the same identity to push their channel up to the top, obviously this is not good.

        A good system to use may be to only accept one user per IP address, meaning that music bots should not count. This should not be released to the general public, such that people do not try to get around this as easily.

        Users will still bbe able to get around this IP feature by using a VPN. If it reaches the point where users are doing this, only a person would realistically (and fairly) be able to assume if the person is trying to get around the system or not. If we decide we even want to prevent this from happening (or provide a paid alternative), we could put in place a bias against users who do this. This would likely result in people getting not understanding why there channel is lower, especially if they stop doing this and obtain real people to join there channel.

    - A better way of organising threaded functions.
        It'd be nicer to have a more predictable time at which channel sorting begins. As such, at the end of each function call when the next function is scheduled, the next function should be scheduled based on how long the current function took to complete (ie look at the time which the next function should be completed at).

    - Potentially a random distance between checking users in channels.
        This could be useful to try and stop people "channel hopping" every 5 minutes, but if enough users want to push up a channel it might as well be at the top anyway.


# Implementation plan - Checking how many subchannels each channel on the server has.

    As channel order is not guranteed by ServerQuery, and such information may be used later on, a list of all channels should be generated. At some point it may be a good idea to build a channel tree, but the process of building a channel tree would be more intensive than just counting the subchannels and users in them, and is therefore not worth doing.

    Each channel recorded in TS should be placed into a list containing all information. Then each toplevel channel (channels with parent id 0 (PID=0) should have its subchannels and usercounts collected by finding all channels with its PID, and then all channels with those PIDs and so on, until no channels remain. This could easily be an intensive process, but as the server will only be doing this every 5 minutes or a similar time frame, this should not be too bad.

    This is being implemented in channelinfoscraper.py