#Build Event tables for Website
import pandas as pd 
from datetime import datetime, timedelta

experiments = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]

file = open("../1_Info/ExperimentTables.html","w")

begin_col = '\t\t<tr>\n'
end_col = '\t\t</tr>\n'

for experiment in experiments:

	event_data = pd.read_csv('../2_Data/Experiment_' + str(experiment) + '/Experiment_' + str(experiment) + '_Events.csv')

	event_data = event_data.set_index('Time')

	file.write('Experiment ' + str(experiment) + ' Table \n\n')
	file.write('<p></p>\n\n')
	file.write('<div class="container">\n')
	file.write('\t<div class="table-div">\n')
	file.write('\t<table border="1" style="width:25%">\n')
	file.write('\t\t<col align="center">\n')
	file.write('\t\t<col align="left">\n')
	file.write(begin_col)
	file.write('\t\t\t<td><b>Time</b></td>\n')
	file.write('\t\t\t<td><b>Event</b></td>\n')
	file.write(end_col)

	for event in event_data.index:
		time = datetime.strptime(event, '%m/%d/%y %H:%M:%S')
		time = datetime.strftime(time, '%H:%M:%S')
		file.write(begin_col)
		file.write('\t\t\t\t<td>' + time + '</td>\n')
		file.write('\t\t\t\t<td>' + event_data['Event'][event] + '</td>\n')
		file.write(end_col)
	
	file.write('\t</table>\n')
	file.write('\t</div>\n')
	file.write('</div>\n\n')
	file.write('<p></p>\n\n')
