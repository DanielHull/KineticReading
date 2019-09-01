'''
Developer: Daniel Hull dhull@baebies.com
Plese reach out with any questions or points of improvement
Copyright Baebies 2017
See Readme for additional details
'''

# import necessary modules
import argparse, sys, xlsxwriter
import numpy as np
sys.dont_write_bytecode = True
from KineticAnalysis import *
from KineticAssayTools import write_excel_file

# Future CLI tool development
DESC = 'CLI tool for saving data file to a local copy'
USAGE = '''
Basic Usage:
    --af absorbance file to find oil blue information (can be a string or not will convert) (requried)
    ff fluorescence file to find oil blue information (can be a string or not, will convert) (required)
    --af_ff_save_location pathway to access absorbance file fluoresence file location, deault is firmware location universally accepted
    --tf_save_location where the tf file is located (should be used in tandem with --tf)
    --offset ability to change how many initial samples not to analyze in kinetic analysis
    --absorbance_file_labels labels of Dark, Blue and Reference Absorbance
    --drop_label (str) label used in fluorescence file for identifying drop labels, appends to this label numbers 1 to drop number
    --blank_label (str) label used in fluorescence file for identifying blank labels, appends to this label numbers 1 to drop number
    e.g.
'''

parser = argparse.ArgumentParser(description=DESC, usage=USAGE)
parser.add_argument('ff', type=str)
parser.add_argument('--af', type=str)
parser.add_argument('--af_ff_save_location', default='C:\src\python', type=str)
parser.add_argument('--tf_save_location', default = "C:\Program Files (x86)\Application Development Environment\\results", type=str)
parser.add_argument('--offset', nargs='+', default=[], help= '(O,int) selection of which droplets you want to grab"')
parser.add_argument('--absorbance_file_labels', nargs='+', default = ['Dark_Abs', 'Blue_Abs', 'Ref_Abs'], help='list out labels, no particular order, does require, dark, blue, and ref in words')
parser.add_argument('--time_stamp_events_list', nargs='+', default = ['Merge Drop ', 'Background Detect Time ', 'Droplet Detect Time '], help='list out Merging and Background/droplet labels, please use background, droplet, and merge')
parser.add_argument('--blank_label', type=str, default='Blank_')
parser.add_argument('--drop_label', type=str, default='Drop_')
parser.add_argument('--start_number', type=int, default=1)
parser.add_argument('--normalization_factor', type=float, default=1.0)
parser.add_argument('--filename', type=str, default='KineticOverview.xlsx')
parser.add_argument('--end_number', type=int, default=7)
args = parser.parse_args()

if not args.offset:
    offset_bounds = []
else:
    try:
        offset_bounds = [int(i) for i in args.offset[0].split(',')]
        offset_bounds = sorted(offset_bounds)
    except ValueError:
        raise ValueError('you did not type in the offset integers separated by a comma or there is a space that python can''t handle')
drop_numbers = range(args.start_number, args.end_number+1)

# best we can do to be generalizable in a cli script
drop_label = [label for label in args.time_stamp_events_list if 'drop' in label.lower() and 'merge' not in label.lower()]
background_label = [label for label in args.time_stamp_events_list if 'back' in label.lower()]
merge_label = [label for label in args.time_stamp_events_list if 'merge' in label.lower()]
time_bases = [merge_label[0], background_label[0], drop_label[0]]

KA_object = KineticAnalysis(args.af, args.ff, args.af_ff_save_location, drop_numbers, time_bases, [args.blank_label, args.drop_label])
KA_object.get_timestamp_file(args.tf_save_location)
KA_object.data_extraction_log()
KA_object.data_extraction_ff()
if args.af:
    KA_object.oil_blue_spectrum_analysis(args.absorbance_file_labels)
KA_object.functional_assay_data_organization()
KA_object.kinetic_analysis(offset_bounds, args.normalization_factor)
KA_object.plot_drops_blanks_background()

workbook_object = xlsxwriter.Workbook(args.filename)
write_excel_file(workbook_object, [KA_object.drop_dictionary], 'Times and RFU Counts')
write_excel_file(workbook_object, [KA_object.slopes], 'Slope data')
if args.af:
    write_excel_file(workbook_object, [KA_object.adjusted_slopes], 'Adjusted Slopes')
    write_excel_file(workbook_object, [np.array([KA_object.path_length]), 'OilBlue.png'], 'OilBlueImage')
write_excel_file(workbook_object, ['Droplet_RFU_Figure.png'], 'Droplet RFU Figure')
workbook_object.close()
