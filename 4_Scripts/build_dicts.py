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

#import test descriptions

test_des = pd.read_csv(info_dir+'Test_Descriptions.csv',index_col = 'Test Name')

events_dict = {}
data_dict = {}

for test in test_des.index.values:
	print(test)
	# events_df = pd.read_csv(data_dir+test+'/'+test+'_Events.csv')
	data_df = TdmsFile(data_dir+test+'/'+test+'.tdms').as_dataframe()
	events_df = data_df.iloc[:,-2:].dropna()
	events_df.columns = ['Event','Time']
	# for j in events_df.index.values:
	# 	print(events_df['Event'][j])
	# 	if events_df['Event'][j] == test_des['Ignition Event'][test]:
	# 		i=j
	# 		break


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
	# print(events_df)
	# exit()
	#Read data dataframe 
	data_df.columns = [column[13:-1] for column in data_df.columns.values]




	#Make a list of elapsed time

	elapsed_time = []
	for t in data_df['Time']:

		# if np.isnan(t)==True:
		# 	continue
		# print(t)
		timestamp = t.split(' ')[-1]

		hh,mm,ss = timestamp.split(':')
		timestamp = 3600*int(hh)+60*int(mm)+int(ss)-int(ignition)
		elapsed_time.append(timestamp)
	# for i in range(len(elapsed_time)-1):
	# 	if i == 0:
	# 		pass
	# 	if elapsed_time[i] == elapsed_time[i+1]:
	# 		elapsed_time[i] = int((elapsed_time[i-1]+elapsed_time[i+1])/2)
	# print(elapsed_time)

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
	# print(test_df)
	# exit()
	data_dict[test] = test_df
pickle.dump(events_dict, open (data_dir+'events.dict','wb'))
pickle.dump(data_dict, open (data_dir+'metric_test_data.dict','wb'))






