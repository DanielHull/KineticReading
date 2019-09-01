
'''
Developer: Daniel Hull dhull@baebies.com
Plese reach out with any questions or points of improvement
Copyright Baebies 2018
See Readme for additional details
'''

def calculate_OD(dark_counts, ref_counts, count_matrix, average_matrix, spectrophotometer_wavelengths):
    """
    calculates the OD absorbance level of the count matrix which is a general matrix

    Inputs: dark_counts - (numpy matrix) average of the dark count matrix numpy array with only length
    ref_counts - (numpy matrix) average of the reference count matrix, numpy array, with only length to it
    count_matrix - (numpy matrix) of multiple rows and columns to calculate OD of
    average - (bool) true or false on whether to normalize the count matrix down the column
    spectrophotometer_wavelengths - (numpy array) used for loess filter if needed, calculates

    Returns:
    smoothed OD - if averaged over, smoothed OD is returned as the lowessed filtered 1D numpy array
    OD - if it needs to remain a matrix with no inherent smoothing
    """

    import numpy as np
    from statsmodels.nonparametric.smoothers_lowess import lowess
    OD = (count_matrix-dark_counts)/(ref_counts-dark_counts)
    OD = -np.log10(OD)
    if average_matrix is True:
        OD = np.mean(OD, axis=0)
        smoothed_OD = lowess(OD, spectrophotometer_wavelengths, frac=0.02, return_sorted=False)
        return smoothed_OD
    return OD

def get_sec(val1, val2):
    """
    Conversion of ADE timestamp to seconds

    Inputs:
    val1, val2 - large number of milliseconds that can be converted to seconds by the following equation

    Returns:
    floating point value - time in seconds
    """
    return 60*(float(val1)-float(val2))/(60000)

def write_excel_file(workbook_object, dataset, worksheet_name):
    """
    Somewhat generalizable way to write to a preset workbook object excel file

    Inputs:
    workbook_object - object instance of the Workbook class
    dataset - list of variables that you'd like to write to a specific worksheet, at this point not generalizable to multiple worksheets (future change)
        data types handled:
            - dict: keys written at the top of a column, values written underneath
            - str: at this point strings correspond to inserting an image, handles 'png', 'jpg, and 'svg' types
            - numpy: can write multiple numpy arrays to the same worksheet, will write them in the order you present the data
    worksheet name - name you'd like to create for worksheet object

    Outputs:
    N/A
    """
    worksheet = workbook_object.add_worksheet(worksheet_name)
    starting_row = 0
    starting_col = 0
    for dataset_i in dataset:
        if type(dataset_i) is dict:
            key_line = workbook_object.add_format({'bold': True})
            key_line.set_align('center')
            key_line.set_align('vcenter')
            key_line.set_text_wrap()
            other_lines = workbook_object.add_format()
            other_lines.set_align('center')
            for col_n, key in enumerate(sorted(dataset_i.keys())):
                worksheet.write(0, col_n, key, key_line)
                for row_n, val in enumerate(dataset_i[key]):
                    worksheet.write(row_n+1, col_n, val, other_lines)
        if type(dataset_i) is str:
            if dataset_i.split('.')[1] in ['png', 'jpg', 'svg']:
                worksheet.insert_image(10,0,dataset_i)
        if type(dataset_i).__module__ == 'numpy':
            try:
                (n_rows, n_cols) = dataset_i.shape
                for col_n in range(n_cols):
                    for row_n in range(n_rows):
                        worksheet.write(starting_row+row_n, starting_col+col_n, dataset_i[row_n, col_n])
                starting_row = n_rows+starting_row
            except ValueError:
                n_cols = len(dataset_i)
                for col_n in range(n_cols):
                    worksheet.write(starting_row, starting_col+col_n, dataset_i[col_n])
                starting_row = starting_row+1

def create_size_dictionary(drop_dictionary):
    """
    checks to make sure every drop # lines up in size
    input: (dict) of key value pairs of keys as strings, values as list/arrays
    output: (dict) of key, value pairs where keys are the drop numbers and bool values indicate whether drops and blanks map together
    """
    import re, logging
    local_dict = {}
    # goes through dictionary keys - identifies and sorts #s
    for key, value in drop_dictionary.iteritems():
        all_digits = re.findall(r'\d', key)
        if all_digits[-1] not in local_dict:
            local_dict[all_digits[-1]] = [len(drop_dictionary[key])]
        else:
            local_dict[all_digits[-1]].append(len(drop_dictionary[key]))
    # makes sure all numbers are the same at the end
    error_dict = {}
    for key in local_dict.keys():
        error_dict[key] = all(local_dict[key][0]==x for x in local_dict[key])
    return error_dict

def return_key_labels(csvfilename, location):
    """
    input: csvfilename
    output: all_labels returns a set of labels that could be in the fluorimeter
    Assumes built on fluor_cli.py/abs_cli.py where every row written begins with label or the label itself
    """

    all_labels = []
    import csv, os, re
    os.chdir(location)
    sig_row = 0
    with open(csvfilename) as csvfile:
        reader = csv.reader(csvfile)
        # identifies whether omit label header was used or not
        row_1 = reader.next()
        sig_col = 0
        numbers = []
        if row_1[0]=='label':
            sig_col = 1
        for irow, row in enumerate(reader):
            # finds numbers for returning
            num = re.findall('[0-9]', row[sig_col])
            if len(num) == 1 and int(num[0]) not in numbers:
                numbers.append(int(num[0]))
            #removes numbers
            lab_wo_num = re.sub('[0-9]','',row[sig_col])
            if lab_wo_num not in all_labels:
                all_labels.append(lab_wo_num)
    return all_labels, sorted(numbers)

def name_data_file(old_file_name, old_file_location, **kwargs):

    """
    Copied from heavily tested name_data_file script for the purposes of integrating into KineticAnalysis
    old_file_name - old file name ('string')
    old_file_location - path where old file is located (str)

    **kwargs
    new_path_location - path location of the new file
    rename_flag : (boolean)
    """
    from time import localtime, strftime
    import argparse, os, shutil, logging

    time_appendage = strftime('%Y-%m-%d-%H_%M_%S', localtime())
    filename = time_appendage + '_' + old_file_name

    #identifies path location
    directory_list = os.listdir(old_file_location)
    logging.info('directory supplied ' + old_file_location)
    new_name = os.path.join(old_file_location, filename)
    if old_file_name not in directory_list:
        logging.error('ERROR: you did not insert a filename in the working directory')
        raise ValueError()
    if 'new_path_location' in kwargs:
        # new path location has been specified
        if 'rename_flag' not in kwargs or kwargs['rename_flag'] is True:
            os.rename(os.path.join(old_file_location, old_file_name),new_name)
        else:
            new_name = os.path.join(old_file_location, old_file_name)
        if os.path.isdir(kwargs['new_path_location']):
            local_date = strftime('%m-%d-%y', localtime())
            local_directory = kwargs['new_path_location'] + '\\' + local_date
            if os.path.exists(local_directory):
                shutil.copy(new_name, local_directory)
                logging.info('path exists, written to location')
            else:
                os.makedirs(local_directory)
                shutil.copy(new_name, local_directory)
                logging.info('new folder made, written to location')
        else:
            logging.error('ERROR: provided save location path is not a directory')
            raise ValueError()
    else:
        # no key word arguments supplied, simply rename file
        os.rename(os.path.join(old_file_location, old_file_name),new_name)

def update_log(UI_object, log_dir, outer_dir):
    """
    no needed inputs, updates the log file
    """
    import logging, os
    os.chdir(log_dir)
    with open('kinetic.log', 'rb') as f:
        lines = f.readlines()
        lines = ' '.join(lines)
        UI_object.LogLabQl.setText(lines)
    os.chdir(outer_dir)
