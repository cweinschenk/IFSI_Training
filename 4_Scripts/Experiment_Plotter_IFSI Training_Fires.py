# Experiment Plotter IFSI Training Fires

from nptdms import TdmsFile
import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from datetime import datetime, timedelta
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
from itertools import cycle
from bokeh.charts import Scatter, output_file, show
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure, output_file, show, save,ColumnDataSource,reset_output, vplot
from bokeh.models import HoverTool, Range1d, Span, LinearAxis, NumeralTickFormatter
from bokeh.resources import CDN
from scipy.signal import butter, filtfilt

# Define filter for low pass filtering of pressure/temperature for BDP
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filtfilt(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# tdms_file = TdmsFile("Experiment_1.tdms")

data_location = '../2_Data/'

channel_location = '../1_Info/'

chart_location = '../1_Info/'

info_file = '../3_Info/Description_of_Experiments.csv'

#Set Tools for Bokeh Plots
TOOLS = 'box_zoom,reset,hover,pan,wheel_zoom'

# experiments=[2]
# prop = ['C']
experiments = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
prop = ['C','C','C','B','B','B','A','A','A','A','A','A','B','B','B','C','C','C']


experiment_info = pd.DataFrame({'Experiment':experiments,'Prop':prop})
experiment_info = experiment_info.set_index('Experiment')

for experiment in experiment_info.index:

	print ('Plotting Experiment ' + str(experiment))
	tdms_file = TdmsFile(data_location + 'Experiment_' + str(experiment) + '/Experiment_' + str(experiment) + '.tdms')

	# Read in channel list
	if experiment_info['Prop'][experiment] is 'A':
		channel_list = pd.read_csv(channel_location+'Channels_A.csv')
	if experiment_info['Prop'][experiment] is 'B':
		if experiment == 14 or 15:
			print ('Using alternate Channel List')
			channel_list = pd.read_csv(channel_location+'Channels_B_alt.csv')
		else:
			channel_list = pd.read_csv(channel_location+'Channels_B.csv')
	if experiment_info['Prop'][experiment] is 'C':
		if experiment==18:
			print ('Using alternate Channel List')
			channel_list = pd.read_csv(channel_location+'Channels_C_alt.csv')
		else:
			channel_list = pd.read_csv(channel_location+'Channels_C.csv')


	#Sort by Channel Name
	channel_list = channel_list.sort_values('Channel_Name', ascending=False)

	# Set index value for channels as 'Channel'
	channel_list = channel_list.set_index('Channel_Name')

	# Create groups data by grouping channels for 'Chart' and Sort Channel Groups so 7' is first plotted.
	channel_groups = channel_list.groupby('Chart', sort=False)

	#Read in Chart File
	charts_data = pd.read_csv(channel_location + 'Charts.csv')

	charts_data = charts_data.set_index('Chart')

	output_location = '../3_charts/Experiment_' + str(experiment) + '/'

	# If the folder doesn't exist create it.
	if not os.path.exists(output_location):
		os.makedirs(output_location)

	#Get Time from TDMS File
	Time = tdms_file.object('Channels', 'Time').data
	Time = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S') for t in Time]
	Start_Time = Time[0]
	End_Time = Time[-1]

	# #Pull Marked Events From TDMS
	# events = tdms_file.object('Events','Event').data
	# event_times = tdms_file.object('Events', 'Time').data
	# event_times = [datetime.strptime(t, '%Y-%m-%d-%H:%M:%S') for t in event_times]

	# event_data = pd.DataFrame({'Events':events,'Times':event_times})

	#Pull Events from csv File
	event_data = pd.read_csv(data_location + 'Experiment_' + str(experiment) + '/Experiment_' + str(experiment) + '_Events.csv')

	for chart in channel_groups.groups:
		print ("----- Plotting " + chart + " a " + charts_data['Units'][chart] + " Chart -----")

		# Create figure with set x-axis, set size, and available tools in bokeh package
		output_file(output_location + chart + '.html',mode='cdn')
		x_label = 'Time (min) ' + str(Time[0].hour) + ':00 hour'
		range_y = Range1d(charts_data['Y_Min'][chart],charts_data['Y_Max'][chart])
		range_x = Range1d(Start_Time,End_Time)
		y_label = charts_data['Y_Label'][chart]
		p = figure( x_axis_label=x_label, y_axis_label=y_label, x_axis_type='datetime',  height=700, width=1200, title=charts_data['Label'][chart],x_range = range_x, y_range=range_y, tools=TOOLS)

		# Define 20 color pallet using RGB values. 
		# Must be done under chart loop so each chart starts with the same colors
		tableau20 = cycle([(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
					(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
					(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
					(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
					(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)])
		color=tableau20

		for channel in channel_groups.get_group(chart).index.values:

			print(channel)
			data = tdms_file.object('Channels', channel).data * channel_list['Scale_Factor'][channel] + channel_list['Offset'][channel]
			cutoff = 50
			fs = 700	
			data = butter_lowpass_filtfilt(data, cutoff, fs)
			#Source for time display on hover tool
			#source = ColumnDataSource({'time':lambda x: Time.strftime('%H:%M:%s')})
			channel_label = np.tile(channel_list['Channel_Label'][channel],[len(data),1])
			Time_label = [datetime.strftime(t, '%H:%M:%S') for t in Time]
			source = ColumnDataSource({'channels':channel_label, 'Time':Time_label})
			p.line(Time,data, legend=channel_list['Channel_Label'][channel], line_width=2, color=next(color), source=source)
			hover=p.select(dict(type=HoverTool))
			hover.tooltips = [('Channel','@channels'),('Time','@Time'),(charts_data['Units'][chart],'$y{0.0}')]

		for event in event_data.index:
			event_time = datetime.strptime(event_data['Time'][event], '%m/%d/%y %H:%M:%S')
			event_line = Span(location=(event_time-timedelta(hours=4)).timestamp()*1000, dimension = 'height', line_color = 'black', line_width=3)
			p.add_layout(event_line)
			p.text((event_time-timedelta(hours=4)).timestamp()*1000, charts_data['Y_Max'][chart]*.95, text=[event_data['Event'][event]], angle=1.57, text_align='right')

		p.legend.location = charts_data['Legend_Location'][chart]
		if charts_data['2ndY'][chart] is not nan:
			p.extra_y_ranges={charts_data['2ndY'][chart]:Range1d(charts_data['2ndY_Min'][chart],charts_data['2ndY_Max'][chart])}
			p.add_layout(LinearAxis(y_range_name=charts_data['2ndY'][chart], axis_label=charts_data['2ndY'][chart]), 'right')
		
		#Add Grey Data box over bad data.
		if chart in ['Gas_B','Carbon_Monoxide_B']:
			print ('This is a Gas_B or Carbon_Monxide_B chart.')
			if experiment == 4:
				print ('adding patch')
				p.patch([Start_Time, Start_Time, Start_Time+timedelta(minutes=15, seconds=33), Start_Time+timedelta(minutes=15, seconds=33)], 
					[charts_data['Y_Min'][chart], charts_data['Y_Max'][chart],  charts_data['Y_Max'][chart], charts_data['Y_Min'][chart]], color="grey", alpha=0.5, line_width=1)	

		save(p)	
		reset_output()

		# print (chart)
		# print (charts_data['Exp_Note'][chart])
		# exit()
		#Add Notes to html files as needed
		
		#Check to see if thre is a note
		if not pd.isnull(charts_data['Exp_Note'][chart]):
			
			#Read in the notes
			exp_note = charts_data['Notes'][chart]
			
			#Seperate if more than 1 note
			exp_note = exp_note.split('|',1)
			
			#Seperate if more than one experiment
			exp_exp = np.fromstring(charts_data['Exp_Note'][chart], sep='|')
			
			#check to see if seperator existed. If not replace with original value
			if len(exp_exp) == 1:
				exp_exp = float(charts_data['Exp_Note'][chart])
			else:
				contintue

			chart_notes = pd.DataFrame({'Exp':exp_exp, 'Note':exp_note})
			chart_notes = chart_notes.set_index('Exp')

			if float(experiment) in chart_notes.index.values:
				f = open(output_location + chart + '.html', 'r')
				contents = f.readlines()
				f.close

				note = '<p><b>Note: ' + chart_notes['Note'][float(experiment)] + '</b></p>'
				contents.insert(-2,note)

				f = open(output_location + chart + '.html', 'w')
				contents = "".join(contents)
				f.write(contents)
				f.close

