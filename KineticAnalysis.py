'''
Developer: Daniel Hull dhull@baebies.com
Plese reach out with any questions or points of improvement
Copyright Baebies 2018
See Readme for additional details
'''

class KineticAnalysis:
    def __init__(self, af_file, ff_file, af_ff_save_location, drop_numbers, base_time_labels, base_fluor_labels):
        # import relevant modules
        import numpy as np
        import csv, os, logging
        from statsmodels.nonparametric.smoothers_lowess import lowess
        import matplotlib.pyplot as plt
        global plt, np, csv, os, lowess

        self.ff_file = ff_file
        self.af_file = af_file
        self.af_ff_save_location = af_ff_save_location
        self.drop_numbers = drop_numbers
        self.time_labels = [label+str(i) for label in base_time_labels for i in drop_numbers]
        self.assay_labels = [label+str(i) for label in base_fluor_labels for i in drop_numbers]
        self.label_bases = base_time_labels + base_fluor_labels
        logging.info('Kinetic Analysis Begun')

    def get_timestamp_file(self, results_directory):
        """
        Adapted from tech_dev_python_analytics_tools.py
        Assumes sorted data folders based on date

        Inputs:
        results_directory - (str) that houses the log file
        """

        import os, logging
        from time import strftime, localtime
        try:
            os.chdir(results_directory)
        except WindowsError:
            logging.info('ERROR: Failed to Grab Time File, directory doesn''t exist')
        current_directory_contents = os.listdir(os.getcwd())
        most_recent_date = current_directory_contents[-1]
        # changes directory, grabs most recent file
        os.chdir(results_directory+'\\'+most_recent_date)
        files = os.listdir(os.getcwd())
        results_file_csv = files[-1]
        self.tf = results_file_csv
        self.tf_loc = os.getcwd()
        logging.info('Successfully got timestamp file')
        logging.info('Timestamp file is ' + str(results_file_csv))

    def data_extraction_ff(self):
        """
        Maps fluorescent data from known columns of labels and values
        Assumes you are looking down a column, a fair assumption
        Raises error if your fluorimeter stopped working at any point

        Inputs: self.af_ff_save_location
        Outputs: self.fluor_dict
        """
        import csv, os, time, logging
        from KineticAssayTools import create_size_dictionary
        os.chdir(self.af_ff_save_location)
        label_col = 0
        data_col = 8
        self.fluor_dict = {key:[] for key in self.assay_labels}
        with open(self.ff_file, 'rb') as csvfile:
            myread = csv.reader(csvfile)
            for row in myread:
                if row[label_col] in self.fluor_dict.keys():
                    self.fluor_dict[row[label_col]].append(float(row[data_col]))
        #handles failed detections
        error_check_dictionary = create_size_dictionary(self.fluor_dict)
        failed_drops = {key:val for key, val in error_check_dictionary.iteritems() if val is False}
        if not not failed_drops:
            logging.error('ERROR: Fluor Drop det != to blank det at drops ' + str(failed_drops.keys()))
            raise ValueError('ERROR: Failed Detection or uneven blank/drop combinations at Drops ' + str(failed_drops.keys()))

        #notifies user successful completion
        logging.info('Successfully extracted ff data')

    def data_extraction_log(self):
        """
        Maps fluorescent data from a csv file to a dictionary with
        Assumes you are looking down a column, a fair assumption for STS and fluorimeter firmware outputs

        Adds to self:
        log_dict: a key-value pair of labels and all corresponding data of interest, will convert to float, must be numerical data
        """
        import csv, os, logging
        label_col = 0
        data_col = 3
        self.log_dict = {key:[] for key in self.time_labels}
        with open(self.tf, 'rb') as csvfile:
            myread = csv.reader(csvfile)
            for row in myread:
                if row[label_col] in self.log_dict.keys():
                    self.log_dict[row[label_col]].append(float(row[data_col]))
        logging.info('Extracted time data')

    def functional_assay_data_organization(self):
        """
        Performs all relevant calculations including background subtraction and time conversion to seconds differentials
        For all - there is a single merge time that needs to be subtracted
        Handles two frequent user errors

        Inputs: self log_dict, fluor_dict

        Outputs: drop_dictionary
        """
        from KineticAssayTools import get_sec, create_size_dictionary
        import logging

        #handles cases where there are dual experiments, or no time file mapped or not enough or no time labels
        #filters out merge keys because those will be length one, it's always the first key in the list
        without_merge = list(filter(lambda x: self.label_bases[0] not in x, self.log_dict.keys()))
        with_merge = list(filter(lambda x: self.label_bases[0] in x, self.log_dict.keys()))
        for key in with_merge:
            if len(self.log_dict[key])!=1:
                logging.error('ERROR: Some merges are not found in the time file')
                raise ValueError('ERROR: Some merges are not found in the time file' )
        temp_dict = {k: self.log_dict[k] for k in without_merge}
        temp_dict.update(self.fluor_dict)
        error_check_dictionary = create_size_dictionary(temp_dict)
        failed_drops = {key:val for key, val in error_check_dictionary.iteritems() if val is False}
        if not not failed_drops:
            logging.info('ERROR: Diff # of det labels and actual det at Drops' + str(failed_drops.keys()))
            raise ValueError('ERROR: Different Number of Detection labels and actual detections at Drop ' + str(failed_drops.keys()))

        self.drop_dictionary = {}
        for i in self.drop_numbers:
            try:
                self.drop_dictionary['Droplet_Detect_Time_From_Merge_'+str(i)]  = [get_sec(val, self.log_dict[self.label_bases[0] + str(i)][0]) for val in self.log_dict[self.label_bases[2] + str(i)]]
                self.drop_dictionary['Blank_Detect_Time_From_Merge_'+str(i)]  = [get_sec(val, self.log_dict[self.label_bases[0] + str(i)][0]) for val in self.log_dict[self.label_bases[2] + str(i)]]
                self.drop_dictionary['DropSub_'+str(i)] = [a_i - b_i for a_i, b_i in zip(self.fluor_dict[self.label_bases[4]+str(i)], self.fluor_dict[self.label_bases[3]+str(i)])]
            except KeyError:
                logging.error('ERROR: Drop # in time file or fluor file do not line up with the labels on UI')
                raise KeyError('')
        self.drop_dictionary.update(self.fluor_dict)
        logging.info('successfully blank subtracted, calculated det times relative to merge')

    def oil_blue_spectrum_analysis(self, dark_ref_blue_list):
        """
        Oil Blue Spectrum Analysis, adaptation from the TechDevPythonAnalyticsTools
        Adapts key_word_search, path_length_estimation, & basic_plot

        Inputs:
        csv_sort_names: names of the reference, dark, and  (list, len == 3)

        Self Outputs:
        path_length - the path length of the cartridge
        """

        from KineticAssayTools import calculate_OD
        import numpy as np
        import logging

        # reads in absorbance csv
        self.csv_lol = []
        with open(self.af_file, 'rb') as csvfile:
            myread = csv.reader(csvfile)
            for row in myread:
                self.csv_lol.append(row)
        self.csv_lol = np.array(self.csv_lol)
        # identifies the locations of the key words of dark, ref, & blue
        dark_ref_blue_dict = {key : np.where(self.csv_lol == key) for key in dark_ref_blue_list}

        sample_row = np.array(self.csv_lol[0])
        # grabs the wavelength outputs from the
        spectrophotometer_wavelengths = []
        wavelengths_begin = [index+1 for index, val in enumerate(sample_row) if val == 'wavelengths']
        spectrophotometer_wavelengths = sample_row[wavelengths_begin[0]:wavelengths_begin[0]+1024]
        self.spectrophotometer_wavelengths = spectrophotometer_wavelengths.astype(np.float)

        # extracts a matrix of the counts and puts them in each dictionary, assumes the counts begin after the second firmware output of the word with spectrum
        counts_begin = [index for index, val in enumerate(sample_row) if 'spectrum' in val.split('_')]
        self.counts_begin = counts_begin[1]+1

        dark_counts_lol = [self.csv_lol[i][self.counts_begin:] for i in dark_ref_blue_dict[dark_ref_blue_list[0]][0]]
        ref_counts_lol = [self.csv_lol[i][self.counts_begin:] for i in dark_ref_blue_dict[dark_ref_blue_list[2]][0]]
        blue_counts_lol = [self.csv_lol[i][self.counts_begin:] for i in dark_ref_blue_dict[dark_ref_blue_list[1]][0]]

        # converts to numpy array
        dark_counts_lol = np.array(dark_counts_lol).astype(np.int)
        ref_counts_lol = np.array(ref_counts_lol).astype(np.int)
        blue_counts = np.array(blue_counts_lol).astype(np.int)

        # takes average of ref and dark
        self.dark_counts = np.mean(dark_counts_lol, axis=0)
        self.ref_counts = np.mean(ref_counts_lol, axis=0)
        # calculates OD of blue oil absorbance, multiple reads made
        OD = calculate_OD(self.dark_counts, self.ref_counts, blue_counts, True, self.spectrophotometer_wavelengths)
        #self.blue_counts = lowess(OD, self.spectrophotometer_wavelengths, frac=0.02, return_sorted=False)
        self.path_length = 10000*max(OD[647:668]-np.median(OD[813:833]))/1.51

        # plots oil blue spectrum
        plt.clf()
        plt.plot(self.spectrophotometer_wavelengths, OD)
        plt.xlim([500, 700])
        plt.xlabel('wavelengths (nm)')
        plt.ylim([0,0.1])
        plt.ylabel('OD')
        path_length = '%s' %float('%g6' %self.path_length)
        plt.text(600, 0.075, 'pathlength is ' + path_length)
        plt.title('Blue Oil Absorbance')
        plt.savefig('OilBlue.png')
        logging.info('calculated OD and created Oil Blue plot')

    def kinetic_analysis(self, offset_bounds, normalization_factor):
        """
        Kinetic analysis by running a linear regression on the RFUs of assays over time
        Assumptions:
            each set is row wise not column wise, so whatever you want analyzed, make it a row

        Self:
        slopes - numpy array of slopes for each data set organized by rows
        """

        from sklearn import linear_model
        import logging
        import numpy as np
        regr = linear_model.LinearRegression()
        self.slopes = {}
        self.adjusted_slopes = {}
        self.intercept = {}
        for drop_number in self.drop_numbers:
            if not offset_bounds:
                background_sub_lol = np.array(self.drop_dictionary['DropSub_'+str(drop_number)][:])
                drop_time_lol = np.array(self.drop_dictionary['Droplet_Detect_Time_From_Merge_'+str(drop_number)][:])
            else:
                background_sub_lol = np.array(self.drop_dictionary['DropSub_'+str(drop_number)][offset_bounds[0]-1:offset_bounds[1]])
                drop_time_lol = np.array(self.drop_dictionary['Droplet_Detect_Time_From_Merge_'+str(drop_number)][offset_bounds[0]-1:offset_bounds[1]])
            elements_to_delete = [col for col, val in enumerate(background_sub_lol) if (abs(val) > 999000) or (val ==0)]
            background_sub_lol = np.delete(background_sub_lol, elements_to_delete, None)
            drop_time_lol =  np.delete(drop_time_lol, elements_to_delete, None)
            if background_sub_lol.size != 0:
                self.slopes['Drop Number '+ str(drop_number)] = np.array([])
                self.intercept['Drop Number '+ str(drop_number)] = np.array([])
                regr.fit(drop_time_lol.reshape(len(drop_time_lol),1), background_sub_lol.reshape(len(drop_time_lol),1))
                self.slopes['Drop Number '+ str(drop_number)] =  [regr.coef_[0][0]]
                self.slopes['Inst Factor Slope of Drop Number '+ str(drop_number)] = [normalization_factor*regr.coef_[0][0]]
                self.intercept['Drop Number '+ str(drop_number)] = [regr.intercept_[0]]
                if self.af_file:
                    self.adjusted_slopes['Drop Number '+ str(drop_number)] = [(self.slopes['Drop Number '+ str(drop_number)][0])*(10000.0/self.path_length)]
                    self.adjusted_slopes['Normalized by OD & Inst Slope of Drop Number '+ str(drop_number)] =  [normalization_factor*(self.slopes['Drop Number '+ str(drop_number)][0])*(10000.0/self.path_length)]
            else:
                pass
        logging.info('completed kinetic analysis')

    def plot_drops_blanks_background(self):
        """
        Adapted from single plex script

        Inputs:

        Returns: None
        """

        import matplotlib.pyplot as plt
        import numpy as np

        if len(self.drop_numbers) > 1:
            fig, axs = plt.subplots(1,len(self.drop_numbers))
            axs = axs.reshape(-1)
        else:
            fig, axs = plt.subplots(1,len(self.drop_numbers)+1)
            axs = axs.reshape(-1)
        for pos, drop_number in enumerate(self.drop_numbers):
            try:
                self.slopes['Drop Number '+ str(drop_number)] = np.around(self.slopes['Drop Number '+ str(drop_number)], decimals=3)
                self.intercept['Drop Number '+ str(drop_number)] = np.around(self.intercept['Drop Number '+ str(drop_number)], decimals=3)
                my_text = 'y='+str(self.slopes['Drop Number '+ str(drop_number)][0])+'x+'+str(self.intercept['Drop Number '+ str(drop_number)][0])
                filtered_output_drops = list(filter(lambda x: (x>0 and x!=1000000), self.drop_dictionary['Drop_' + str(drop_number)]))
                filtered_output_blanks = list(filter(lambda x: (x>0 and x!=1000000), self.drop_dictionary['Blank_' + str(drop_number)]))
                filtered_output_back_sub =  list(filter(lambda x: (x>-300 and x<3000), self.drop_dictionary['DropSub_'+str(drop_number)]))
                filtered_list = filtered_output_drops + filtered_output_blanks + filtered_output_back_sub
                (y_max, y_min) = (max(filtered_list), min(filtered_list))
                axs[pos].scatter(self.drop_dictionary['Blank_Detect_Time_From_Merge_'+str(drop_number)], self.drop_dictionary['Blank_'+str(drop_number)], c='b')
                axs[pos].scatter(self.drop_dictionary['Droplet_Detect_Time_From_Merge_'+str(drop_number)], self.drop_dictionary['Drop_' + str(drop_number)], c='g')
                axs[pos].scatter(self.drop_dictionary['Droplet_Detect_Time_From_Merge_'+str(drop_number)], self.drop_dictionary['DropSub_'+str(drop_number)], c='r')
                axs[pos].set_xlabel('seconds post merge')
                axs[pos].set_ylabel('RFUs')
                axs[pos].set_title('Drop ' + str(drop_number))
                axs[pos].set_ylim(top = y_max+10, bottom=y_min-10)
                axs[pos].text(0.5, 0.3, my_text, horizontalalignment='center', verticalalignment='center', transform = axs[pos].transAxes)
            except:
                pass
        length = 6*len(self.drop_numbers)
        fig.set_size_inches(length, 7.5)
        plt.savefig('Droplet_RFU_Figure.png')
