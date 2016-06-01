

channel_clientcount_dict = {"1" : [0, 2, 4, 2, 5, 7, 8, 9, 7],
                            "2" : [6, 4, 3, 8, 7, 5, 2, 3, 6],
                            "3" : [5, 6, 8, 777, 777, 777, 777, 6, 1],
                            "4" : [0],
                            "5" : [8, 9, 5, 2, 4, 8, 2, 5, 666]}

channel_clientcount_average_dict = {}

for channel_id in channel_clientcount_dict:

    channel_clientcount_average_dict[channel_id] = sum(channel_clientcount_dict[channel_id]) / len(channel_clientcount_dict[channel_id])

channel_clientcount_sorted_list = sorted(channel_clientcount_average_dict, key=channel_clientcount_average_dict.get)

print(str(channel_clientcount_sorted_list))