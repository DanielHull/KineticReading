import sys, os, csv, logging
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QFont
from PyQt5 import QtCore

import sys, xlsxwriter
import numpy as np
sys.dont_write_bytecode = True
from KineticAnalysis import *
from KineticAssayTools import write_excel_file, name_data_file, return_key_labels, update_log

base_dir = os.getcwd()
Ui_MainWindow, QtBaseClass = uic.loadUiType("KineticReadingUI.ui")

class KRApp(QMainWindow):
    def __init__(self):
        super(KRApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.clicked_run = 0
        self.ui.RunQpb.clicked.connect(self.run_experiments)
        self.ui.ResToDefQpb.clicked.connect(self.reset_defaults)
        self.ui.ResToLasExpQpb.clicked.connect(self.reset_recent_exp)
        self.ui.GetAbs.clicked.connect(self.getAbs)
        self.ui.GetFlu.clicked.connect(self.getFluor)
        self.ui.GetSavLoc.clicked.connect(self.getPath)
        self.ui_list = [self.ui.FluFilQte, self.ui.AbsFilQte, self.ui.AbsFilFluSavLocQte, self.ui.TimFilSavLocQte, self.ui.StaDroQte, self.ui.EndDroQte, self.ui.BlaLabQte, self.ui.DroLabQte,\
        self.ui.DarAbsLabQte, self.ui.BluAbsLabQte, self.ui.RefAbsLabQte, self.ui.MerDroLabQte, self.ui.BacDetLabQte, self.ui.DroDetLabQte, self.ui.Offset1, self.ui.Offset2, self.ui.SavQte, \
        self.ui.NorFacQte, self.ui.KinFilQte]

    def reset_defaults(self):
        """
        Grabs default csv which should be underneath temptext (hardcoded)
        repopulates UI with this information
        """
        os.chdir(base_dir)
        with open('defaults.csv') as csvfile:
            reader_object = csv.reader(csvfile)
            row_1 = reader_object.next()
            for index ,ui_element in enumerate(self.ui_list):
                ui_element.setText(row_1[index])

    def reset_recent_exp(self):
        """
        Grabs reset file and populates all ui Qte objects with previous
        experimental info
        """
        os.chdir(base_dir)
        with open('recent_exp.csv') as csvfile:
            reader_object = csv.reader(csvfile)
            row_1 = reader_object.next()
            for index ,ui_element in enumerate(self.ui_list):
                ui_element.setText(row_1[index])

    def getAbs(self):
        """
        Utilizes QFileDialog for finding and getting abs file
        """
        fname = QFileDialog.getOpenFileName(self, 'Open file',
         base_dir,"CSV files (*.csv)")
        split_by_path = fname[0].split('/')
        file = split_by_path[-1]
        split_by_path.pop()
        full_path = '\\'.join(split_by_path)
        self.ui.AbsFilQte.setText(file)
        self.ui.AbsFilFluSavLocQte.setText(full_path)
        all_labels, numbers = return_key_labels(file, full_path)
        list_labels = ','.join(all_labels)
        self.ui.DarAbsLabQte.setText(list_labels)
        self.ui.BluAbsLabQte.setText(list_labels)
        self.ui.RefAbsLabQte.setText(list_labels)

    def getFluor(self):
        """
        Utilizes QFileDialog to grab the fluor file
        """
        fname = QFileDialog.getOpenFileName(self, 'Open file',
         base_dir,"CSV files (*.csv)")
        split_by_path = fname[0].split('/')
        file = split_by_path[-1]
        split_by_path.pop()
        full_path = '\\'.join(split_by_path)
        self.ui.FluFilQte.setText(file)
        self.ui.AbsFilFluSavLocQte.setText(full_path)
        all_labels, numbers = return_key_labels(file, full_path)
        list_labels = ','.join(all_labels)
        self.ui.BlaLabQte.setText(list_labels)
        self.ui.DroLabQte.setText(list_labels)
        self.ui.StaDroQte.setText(str(min(numbers)))
        self.ui.EndDroQte.setText(str(max(numbers)))

    def getPath(self):
        """
        Gets path of the directory the user selects
        """
        fname = QFileDialog.getExistingDirectory(self, 'Select Directory', base_dir)
        self.ui.SavQte.setText(fname)

    def run_experiments(self):
        """
        Performs a number of tasks in order as described by the comments
        """
        os.chdir(base_dir)
        # writes data to the local csv file for feature "reset last experiment"
        # for next time if user wants to repopulate
        my_row = []
        for index ,ui_element in enumerate(self.ui_list):
            my_row.append(ui_element.toPlainText())
        with open('recent_exp.csv', 'wb') as csvfile:
            csvwriter_object = csv.writer(csvfile)
            csvwriter_object.writerow(my_row)
        # logs from parent directory
        logging.basicConfig(format='%(asctime)s %(message)s',\
        filename='kinetic.log',level=logging.DEBUG, datefmt= '%I:%M:%S %p')
        font = QFont()
        font.setPointSize(8)
        self.ui.LogLabQl.setFont(font)

        try:
            # populates relevant, frequently used variables for analysis from GUI
            drop_numbers = range(int(self.ui.StaDroQte.toPlainText()), int(self.ui.EndDroQte.toPlainText())+1)
            blank_drop_labels = [self.ui.BlaLabQte.toPlainText(), self.ui.DroLabQte.toPlainText()]
            time_stamp_events_list = [self.ui.MerDroLabQte.toPlainText(), self.ui.BacDetLabQte.toPlainText(), self.ui.DroDetLabQte.toPlainText()]
            absorbance_file_labels = [self.ui.DarAbsLabQte.toPlainText(), self.ui.BluAbsLabQte.toPlainText(), self.ui.RefAbsLabQte.toPlainText()]
            offset_bounds = [int(self.ui.Offset1.toPlainText()), int(self.ui.Offset2.toPlainText())]
            loop_labels = [blank_drop_labels, time_stamp_events_list, absorbance_file_labels]
            labels_w_spaces = [item for list_one in loop_labels for item in list_one if len(item.split(' ')) > 1]
            filename = self.ui.KinFilQte.toPlainText()
            normalization_factor = np.float64(self.ui.NorFacQte.toPlainText())

            # handles user incorrectly typing in information
            if not drop_numbers:
                logging.error('ERROR: Start Drop > End Drop')
                raise ValueError('ERROR: Start Drop > End Drop')
            try:
                directory_list = os.listdir(self.ui.AbsFilFluSavLocQte.toPlainText())
            except WindowsError:
                logging.error('ERROR: Could not find absorbance fluorescence file location')
                raise WindowsError('ERROR: Could not find absorbance fluorescence file location')
            if self.ui.AbsFilQte.toPlainText() not in directory_list:
                logging.debug('DEBUG: No abs file in supplied directory')
            if self.ui.FluFilQte.toPlainText() not in directory_list:
                logging.error('ERROR: Could not identify fluor file in supplied directory')
                raise WindowsError('Please check to make sure the path is correct for the fluor file')

            # Performs needed calculations
            KA_object = KineticAnalysis(self.ui.AbsFilQte.toPlainText(), self.ui.FluFilQte.toPlainText(), self.ui.AbsFilFluSavLocQte.toPlainText(), drop_numbers, time_stamp_events_list, blank_drop_labels)
            KA_object.get_timestamp_file(self.ui.TimFilSavLocQte.toPlainText())
            KA_object.data_extraction_log()
            KA_object.data_extraction_ff()
            if self.ui.AbsFilQte.toPlainText():
                KA_object.oil_blue_spectrum_analysis(absorbance_file_labels)
            KA_object.functional_assay_data_organization()
            KA_object.kinetic_analysis(offset_bounds, normalization_factor)
            KA_object.plot_drops_blanks_background()

            output_file = filename.split('.')[0] + '.xlsx'
            workbook_object = xlsxwriter.Workbook(output_file)
            KA_object.slopes['T 0 Slope Detection'] = str(offset_bounds[0])
            KA_object.slopes['T End Slope Detection'] = str(offset_bounds[1])

            # creates excel file and needed tabs
            write_excel_file(workbook_object, [KA_object.drop_dictionary], 'Times and RFU Counts')
            write_excel_file(workbook_object, [KA_object.slopes], 'Slope data')
            if self.ui.AbsFilQte.toPlainText():
                KA_object.adjusted_slopes['T 0 Slope Detection'] = str(offset_bounds[0])
                KA_object.adjusted_slopes['T End Slope Detection'] = str(offset_bounds[1])
                write_excel_file(workbook_object, [KA_object.adjusted_slopes], 'Adjusted Slopes')
                write_excel_file(workbook_object, [np.array([KA_object.path_length]), 'OilBlue.png'], 'OilBlueImage')
            write_excel_file(workbook_object, ['Droplet_RFU_Figure.png'], 'Droplet RFU Figure')
            workbook_object.close()

            # moves data
            os.chdir(base_dir)
            if self.ui.SavQte.toPlainText():
                name_data_file(KA_object.tf, KA_object.tf_loc,new_path_location=self.ui.SavQte.toPlainText(), rename_flag=False)
                name_data_file(self.ui.FluFilQte.toPlainText(), self.ui.AbsFilFluSavLocQte.toPlainText(), new_path_location=self.ui.SavQte.toPlainText(), rename_flag=True)
                if self.ui.AbsFilQte.toPlainText():
                    name_data_file(self.ui.AbsFilQte.toPlainText(), self.ui.AbsFilFluSavLocQte.toPlainText(), new_path_location=self.ui.SavQte.toPlainText(), rename_flag=True)
                name_data_file(output_file, self.ui.AbsFilFluSavLocQte.toPlainText(), new_path_location=self.ui.SavQte.toPlainText(), rename_flag=True)

            font = QFont()
            font.setPointSize(24)
            self.ui.LogLabQl.setFont(font)
            self.ui.LogLabQl.setText('Success!')
        except:
            logging.error('ERROR: AN ERROR HAS OCCURRED')
            update_log(self.ui, base_dir, os.getcwd())

        # truncates the log with each new run
        os.chdir(base_dir)
        with open('kinetic.log', 'w'):
            pass

from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)
window = KRApp()
window.show()
sys.exit(app.exec_())
