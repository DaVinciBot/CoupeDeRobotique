import point

def get_current_date():
    from datetime import datetime
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    return {
        "date": now,
        "date_timespamp": timestamp
    }

def is_list_of(list : list, type):
    test = True
    n=0
    while test and n<list.count():
        if not isinstance(list[n],type(type)):
            test = False
        n+=1
    return test



