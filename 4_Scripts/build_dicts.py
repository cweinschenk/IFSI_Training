from __future__ import division
import numpy as np
import os as os
import numpy.ma as ma
import pandas as pd
import itertools
from pylab import *
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import pickle
from nptdms import TdmsFile

##Build dictionary of events for each experimetns named events_dict

#Define directories for the info files, data files, and events files
info_dir = '../1_Info/'
data_dir = '../2_Data/'
# events_dir = info_dir+'Events/'

#import channel list

channels = pd.read_csv(info_dir+'Channels.csv', index_col = 'Channel')

helmet_channels = pd.read_csv(info_dir+'Helmet_Channels.csv', index_col = 'Channel')

#import test descriptions

test_des = pd.read_csv(info_dir+'Test_Descriptions.csv',index_col = 'Test Name')

events_dict = {}
data_dict = {}

for test in test_des.index.values:
	print(test)
	data_df = TdmsFile(data_dir+test+'/'+test+'.tdms').as_dataframe()
	events_df = data_df.iloc[:,-2:].dropna()
	events_df.columns = ['Event','Time']



	#Ignition is taken as the first event followin background
	ignition = events_df['Time'][int(test_des['Ignition Event Index'][test])].split('-')[-1]
	hh,mm,ss = ignition.split(':')
	ignition = 3600*int(hh) + 60*int(mm) + int(ss)
	event_times = []
	for time in events_df['Time']:
		timestamp = time.split('-')[-1]
		hh,mm,ss = timestamp.split(':')
		timestamp = 3600*int(hh)+60*int(mm)+int(ss)-int(ignition)
		event_times.append(timestamp)

	events_df['Time Elapsed']=event_times
	events_df = events_df.set_index('Event')
	for event in events_df:
		event.split('-')
	events_dict[test] = events_df
	# exit()
	#Read data dataframe 
	data_df.columns = [column[13:-1] for column in data_df.columns.values]


	#Make a list of elapsed time
	elapsed_time = []
	for t in data_df['Time']:
		timestamp = t.split(' ')[-1]
		hh,mm,ss = timestamp.split(':')
		timestamp = 3600*int(hh)+60*int(mm)+int(ss)-int(ignition)
		elapsed_time.append(timestamp)

	#Set index as elapsed time
	data_df['Elapsed Time'] = elapsed_time
	data_df = data_df.set_index('Elapsed Time')


	#Divide data datafrane into
	pre_exp_data = data_df.loc[:-1,:]
	exp_data = data_df.loc[0:,:]

	test_df = pd.DataFrame(data={'Elapsed Time':data_df.index.values,'Time':data_df['Time']})
	test_df = test_df.set_index('Elapsed Time')

	for channel in channels.index.values:
		#If channel not in df, continue
		if not channel in data_df.columns:
			continue
		print(channel)

		scale_factor = channels['Scale Factor'][channel]
		offset = channels['Offset'][channel]	
		if channels['Type'][channel] == 'Temperature':
			scaled_data = data_df[channel].round(1)

		elif channels['Type'][channel] == 'HeatFlux':
			zero_data = data_df[channel] - np.average(pre_exp_data[channel])
			scaled_data = zero_data * scale_factor + offset
			scaled_data = scaled_data.round(2)

		elif channels['Type'][channel] == 'Gas':
			transport_time = channels['Transport'][channel]
			scaled_data = data_df[channel].iloc[int(transport_time):]*scale_factor+offset
			scaled_data = scaled_data.round(2)
			nan_array = np.empty(len(data_df.index.values)-len(scaled_data.index.values))
			nan_array[:] =  np.NaN
			scaled_data = pd.Series(np.concatenate([scaled_data.tolist(),nan_array]), index = test_df.index.values)

		elif channels['Type'][channel] == 'Gas (PPM)':
			# zero_data = data_df[channel] - np.average(pre_exp_data[channel])
			transport_time = channels['Transport'][channel]
			# scaled_data = zero_data.iloc[int(transport_time):]*scale_factor+offset
			scaled_data = data_df[channel].iloc[int(transport_time):]*scale_factor+offset
			scaled_data = scaled_data.round(2)
			nan_array = np.empty(len(data_df.index.values)-len(scaled_data.index.values))
			nan_array[:] =  np.NaN
			scaled_data = pd.Series(np.concatenate([scaled_data.tolist(),nan_array]), index = test_df.index.values)
		elif channels['Type'][channel] == 'Pressure':
			scaled_data = data_df[channel] * scale_factor + offset
			scaled_data =scaled_data - np.average(scaled_data.loc[:-1])
			scaled_data = scaled_data.round(1)
		test_df[channel] = scaled_data

	if not os.path.exists(data_dir+test+'/HeatFlux_Helmet/'):
		pass
	else:
	#loop thru csv helmet files in directory
		for f in os.listdir(data_dir+test+'/HeatFlux_Helmet/'):
			if f.endswith('.csv'):
				pass
			else: 
				continue
			helmet = f[:-4]
			wireless_df = pd.read_csv(data_dir + test + '/HeatFlux_Helmet/' + f)
			elapsed_time = []
			for t in wireless_df['Time']:
				timestamp = t.split('_')[-1]
				hh,mm,ss = timestamp.split(':')
				timestamp = 3600*int(hh)+60*int(mm)+int(ss)-int(ignition)
				elapsed_time.append(timestamp)
			#find if 0 is in index, otherwise find next greatest value to serve as igntion
			if 0 in elapsed_time:
				ign = 0
			else:
				for i in range(len(elapsed_time)):
					if elapsed_time[i] > 0:
						ign = elapsed_time[i]
						print('different')
						break

			wireless_df['Elapsed Time'] = elapsed_time
			wireless_df = wireless_df.set_index('Elapsed Time')
			wireless_df = wireless_df[~wireless_df.index.duplicated(keep='first')]
			#if data ends before ignition, continue 
			if wireless_df.index[-1] < 0:
				continue

			
			#Divide data datafrane into
			pre_exp_data = wireless_df.loc[:ign,:]
			exp_data = wireless_df.loc[ign:,:]
			for column in wireless_df.columns:
				if column =='Time' or column == 'TC2':
					continue
				print(column)
				if helmet_channels['Type'][column.replace(' ','').replace(' ','')] == 'Temperature':
					scaled_data = wireless_df[column].round(1)

				elif helmet_channels['Type'][column.replace(' ','')] == 'HeatFlux':
					zero_data = wireless_df[column] - np.average(pre_exp_data[column])
					if helmet == 'Attack_Firefighter':
						scale_factor = helmet_channels['Scale Factor 1'][column.replace(' ','')]
						offset = helmet_channels['Offset 1'][column.replace(' ','')]
					elif helmet == 'Ignition_Instructor':
						scale_factor = helmet_channels['Scale Factor 2'][column.replace(' ','')]
						offset = helmet_channels['Offset 2'][column.replace(' ','')]
					scaled_data = zero_data * scale_factor + offset
					scaled_data = scaled_data.round(2)
				test_df[helmet+'_'+column.replace(' ','')] = scaled_data
	print(test_df)
	# exit()
	data_dict[test] = test_df
pickle.dump(events_dict, open (data_dir+'events.dict','wb'))
pickle.dump(data_dict, open (data_dir+'metric_test_data.dict','wb'))






