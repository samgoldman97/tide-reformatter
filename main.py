"""main.py

Reformat a txt file of tide calendar

    Reformat file: 
        python main.py

"""
import argparse
import re
import arrow
import pandas as pd
from ics import Calendar, Event

def get_args(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--tides-file", 
                        help="Name and loc of tides file", 
                        type=str,
                        action="store",
                        default="tides.txt")
    parser.add_argument("--timezone", 
                        help="Timezone of dates in txt file", 
                        type=str,
                        action="store",
                        default="US/Eastern")
    return parser.parse_args()


def main(tides_file : str, timezone : str = "US/Eastern"): 
    """ main. """

    # Read in file
    with open(tides_file, "r") as fp: 
        lines = fp.readlines()

    # Parse file
    data_dict = {}
    headers = None
    stat_name = None
    df = []
    for line in lines: 
        line = line.strip()
        if "StationName" in line: 
            stat_name = line.split("StationName:")[1].strip()
            data_dict["loc_name"] = stat_name
        elif headers is not None: 
            entries = [i.strip() for i in line.split("\t") if len(i) > 0]
            if len(entries) != len(headers): 
                raise ValueError("Line has diff length than entries")
            df.append(dict(zip(headers, entries)))
        elif headers is None and "Date" == line.split("\t")[0].strip():
            line = line.replace("\t\t", "\t")
            headers = [i.strip() for i in line.split("\t")]
        else: 
            pass


    ## Now write out to a calendar
    c = Calendar()
    for row in df: 
        ### Crafting time
        date = row["Date"]
        time = row["Time"]
        feet = row["Pred(Ft)"]
        high_low = row["High/Low"]

        # Convert time
        yr, month, day = [int(i) for i in date.split("/")]
        am_pm = re.search("(AM|PM)", time).group()
        time = re.sub(am_pm, "",time).strip()
        hr, minutes = [int(i) for i in time.split(":")]
        # convert to 12 hour time
        if am_pm == "AM" and hr == 12: 
            hr -= 12
        elif am_pm == "PM" and hr >= 1 and hr <= 11:
            hr += 12
        else:
            pass

        time_str = f"{yr}-{month:02}-{day:02} {hr:02}:{minutes:02}:00 {timezone}"
        time_obj = arrow.get(time_str, 'YYYY-MM-DD HH:mm:ss ZZZ')

        # Get name
        if high_low == "H": 
            event_name = f"High Tide: {feet} ft"
        else:
            event_name = f"Low Tide: {feet} ft"

        #if month==1 and day == 1 and high_low == "H": 
        #    import pdb
        #    pdb.set_trace()

        # Make and add event
        e = Event(name=event_name, begin=str(time_obj), 
                  description=event_name, location=stat_name)

        c.events.add(e)

    # Export
    with open(f'{stat_name}_tides.ics', 'w') as f:
        f.write(str(c))

if __name__=="__main__": 
    args = get_args()
    arg_dict = args.__dict__
    main(**arg_dict)




