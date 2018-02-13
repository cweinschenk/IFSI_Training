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

channels = pd.read_csv(info_dir+'Helmet_Channels.csv', index_col = 'Channel')

#import test descriptions

test_des = pd.read_csv(info_dir+'Test_Descriptions.csv',index_col = 'Test Name')

events_dict = pickle.load(open(data_dir + 'events.dict', 'rb'))
data_dict = {}

for test in test_des.index.values:
	print(test)
	#if directory exists, read file, else continue
	if not os.path.exists(data_dir+test+'/HeatFlux_Helmet/'):
		continue
	#loop thru csv helmet files in directory
	for f in os.listdir(data_dir+test+'/HeatFlux_Helmet/'):
		if f.endswith('.csv'):
			pass
		else: 
			continue
		helmet = f[:-4]
		data_df = pd.read_csv(data_dir + test + '/HeatFlux_Helmet/' + f)
		events_df = events_dict[test]
		ignition = events_df['Time'][int(test_des['Ignition Event Index'][test])].split('-')[-1]
		hh,mm,ss = ignition.split(':')
		ignition = 3600*int(hh) + 60*int(mm) + int(ss)
		elapsed_time = []
		for t in data_df['Time']:
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

		data_df['Elapsed Time'] = elapsed_time
		data_df = data_df.set_index('Elapsed Time')
		#if data ends before ignition, continue 
		if data_df.index[-1] < 0:
			continue

		
		#Divide data datafrane into
		pre_exp_data = data_df.loc[:ign,:]
		exp_data = data_df.loc[ign:,:]

		test_df = pd.DataFrame(data={'Elapsed Time':data_df.index.values,'Time':data_df['Time']})
		test_df = test_df.set_index('Elapsed Time')
		for column in data_df.columns:
			if column =='Time':
				continue
			print(column)
			if channels['Type'][column.replace(' ','').replace(' ','')] == 'Temperature':
				scaled_data = data_df[column].round(1)

			elif channels['Type'][column.replace(' ','')] == 'HeatFlux':
				zero_data = data_df[column] - np.average(pre_exp_data[column])
				if helmet == 'Attack_Firefighter':
					scale_factor = channels['Scale Factor 1'][column.replace(' ','')]
					offset = channels['Offset 1'][column.replace(' ','')]
				elif helmet == 'Ignition_Instructor':
					scale_factor = channels['Scale Factor 2'][column.replace(' ','')]
					offset = channels['Offset 2'][column.replace(' ','')]
				scaled_data = zero_data * scale_factor + offset
				scaled_data = scaled_data.round(2)
			test_df[helmet+'_'+column.replace(' ','')] = scaled_data
	data_dict[test] = test_df
	# print(test_df)
pickle.dump(data_dict, open (data_dir+'metric_wireless_test_data.dict','wb'))		


