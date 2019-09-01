REM this is a standard test
python kinetic_assay_cli.py OutputSaveFile.csv --af "AbsorbanceSaveFile.csv" --af_ff_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder\results"
REM this test should fail with a failed detection
python kinetic_assay_cli.py OutputSaveFile.csv --af "AbsorbanceSaveFile.csv" --af_ff_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\failed_detection_results" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\failed_detection_results\results"
REM this test should fail with double experiments
python kinetic_assay_cli.py OutputSaveFile.csv --af  "AbsorbanceSaveFile.csv" --af_ff_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\double_detection_results" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\double_detection_results\results"
REM this test demonstrates the user can remove the quotes
python kinetic_assay_cli.py OutputSaveFile.csv --af  AbsorbanceSaveFile.csv  --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder\results"
REM This test demonstrates the usage of using a smaller end number on accident and that it works with just less drops
python kinetic_assay_cli.py OutputSaveFile.csv --af  AbsorbanceSaveFile.csv  --start_number=1 --end_number=6 --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder\results"
REM this test demonstrates the user can analyze a subset of the slope data
python kinetic_assay_cli.py OutputSaveFile.csv --af AbsorbanceSaveFile.csv  --offset 2,5 --start_number=1 --end_number=7 --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder\results"
REM this demonstrates the user can type in the values in the wrong order
python kinetic_assay_cli.py OutputSaveFile.csv --af AbsorbanceSaveFile.csv  --offset 5,2 --start_number=1 --end_number=7 --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder\results"
REM this demonstrates that the offset feature can also work between 2 and a number larger than the number of detections there even are
python kinetic_assay_cli.py OutputSaveFile.csv --af  AbsorbanceSaveFile.csv  --offset 2,15 --start_number=1 --end_number=7 --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder\results"
REM this demonstrates that the an absorbance save file isn't necessary
python kinetic_assay_cli.py OutputSaveFile.csv --offset 2,15 --start_number=1 --end_number=7 --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\sample_data_folder\results"
REM this demonstrates that if the user forgot to add labels it will fail
python kinetic_assay_cli.py OutputSaveFile.csv --offset 2,15 --start_number=1 --end_number=7 --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\forgot_to_add_labels" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\forgot_to_add_labels\results"
REM this demonstrates that if merge labels are gone it will fail
python kinetic_assay_cli.py OutputSaveFile.csv --offset 2,15 --start_number=1 --end_number=7 --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\without_merge" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\without_merge\results"
REM this demonstrates that one can have different numbers of detections for different drops
python kinetic_assay_cli.py OutputSaveFile.csv --af "AbsorbanceSaveFile.csv" --offset 2,15 --start_number=1 --end_number=7 --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\different_num_det" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\different_num_det\results"
REM this demonstrates that one can analyze only one drop
python kinetic_assay_cli.py OutputSaveFile.csv --af "AbsorbanceSaveFile.csv" --offset 1,100 --start_number=0 --end_number=0 --af_ff_save_location="C:\Users\dhull\Documents\code_directory\KineticReading\\test\single_drop_det" --tf_save_location "C:\Users\dhull\Documents\code_directory\KineticReading\\test\single_drop_det\results"
