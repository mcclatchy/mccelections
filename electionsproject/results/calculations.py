## calculate percent: part divided by whole times 100
def calculated_percent(subset, total):
    if subset != None and total != None:
        percent_raw = subset / total
        percent_calculated = percent_raw * 100
        return percent_calculated
    else:
        print 'No values present to calculate' 
