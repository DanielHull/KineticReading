from KineticAssayTools import *
import os

def test_create_size_dictionary():
    dictionary = {'Hello 1': [3,4,5],'Droplet 1': [4,5,6,7], 'Background 1': [6,7,8,9], 'Hello 2':[5,6,7], 'Hello 3':[9,10,11,12]}
    output_dictionary = create_size_dictionary(dictionary)
    print output_dictionary
    assert output_dictionary['1'] == False
    assert output_dictionary['2'] == True
    assert output_dictionary['3'] == True
    print "Testing Creating dictionary sizing passes"

def test_return_key_labels():
    output,numbers = return_key_labels('OutputSaveFilew_label.csv', 'C:\Users\dhull\Documents\code_directory\KineticReading\\test\\testing')
    assert output == ['Drop_', 'Blank_']
    output, numbers = return_key_labels('OutputSaveFilewo_label.csv', 'C:\Users\dhull\Documents\code_directory\KineticReading\\test\\testing')
    assert output == ['Drop_', 'Blank_']
    output, numbers = return_key_labels('OutputSaveFilemislabeled.csv', 'C:\Users\dhull\Documents\code_directory\KineticReading\\test\\testing')
    assert len(output) == 3
    assert numbers == range(1,7)
    os.chdir('C:\Users\dhull\Documents\code_directory\KineticReading')
    print "Returning Key Labels Passes"


def test_get_sec():
    one_sec = get_sec(401000,400000)
    assert one_sec == 1.0
    twenty_sec = get_sec(420000,400000)
    assert twenty_sec == 20.0
    print "Getting Seconds Passes"


def test_name_data_file():

    '''# should rename file
    name_data_file('kinetic.log', os.getcwd())
    # should move file to new folder and rename flag as true
    name_data_file('kinetic.log', os.getcwd(), new_path_location=os.getcwd(), rename_flag=False)
    # should move file to a new folder with old name
    name_data_file('kinetic.log', os.getcwd(), new_path_location=os.getcwd(), rename_flag=True)
    '''
    pass

def test_calculate_OD():
    import numpy as np
    dark = np.array([0,0,0,0,0])
    ref = np.array([1,1,1,1,1])
    samp = np.array([[0.1,0.1,0.1,0.1,0.1],[0.01, 0.01, 0.01, 0.01, 0.01]])
    wavelengths = np.array([100, 200, 300, 400, 500])
    numpy_out = calculate_OD(dark, ref, samp, False, wavelengths)
    output = [[1,1,1,1,1],[2,2,2,2,2]]
    np.testing.assert_array_almost_equal(numpy_out,output)
    print "Calculate OD Passes"


def test_data_extraction():
    from KineticAnalysis import KineticAnalysis
    time_labels = ['Merge Drop ', 'Background Detect Time ', 'Droplet Detect Time ']
    fluor_labels = ['Blank_', 'Drop_']
    drop_numbers = range(1,8)
    KA_object = KineticAnalysis('AbsorbanceSaveFile.csv', 'OutputSaveFile.csv', 'C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder', drop_numbers, time_labels, fluor_labels)
    KA_object.data_extraction_ff()
    assert len(KA_object.fluor_dict.keys()) == 14
    for key in KA_object.fluor_dict.keys():
        assert len(KA_object.fluor_dict[key]) == 10
    assert KA_object.fluor_dict['Drop_1'] == [104.377, 103.049,	1000000,	102.699,	1000000,	101.884,	1000000,	100.309,	101.318,	100.154]
    print "Data Extraction Passes"

def test_get_timestamp_file():
    from KineticAnalysis import KineticAnalysis
    time_labels = ['Merge Drop ', 'Background Detect Time ', 'Droplet Detect Time ']
    fluor_labels = ['Blank_', 'Drop_']
    drop_numbers = range(1,8)
    KA_object = KineticAnalysis('AbsorbanceSaveFile.csv', 'OutputSaveFile.csv', 'C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder', drop_numbers, time_labels, fluor_labels)
    KA_object.get_timestamp_file('C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder\\results')
    assert KA_object.tf == '13-19-08.csv'
    assert KA_object.tf_loc == 'C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder\\results\\031418'
    print 'Get Timestamp File Passes'


def main():
    test_get_sec()
    test_name_data_file()
    test_return_key_labels()
    test_create_size_dictionary()
    test_calculate_OD()
    test_data_extraction()
    test_get_timestamp_file()

main()
