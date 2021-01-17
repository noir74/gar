import time
import functions

if __name__ == '__main__':
    start = time.time()

    # config_file_full_path = sys.argv[1]
    # data_type_to_process = sys.argv[2]
    # zip_region_folders_list = sys.argv[3]

    config_file_full_path = 'Z:/garbage/tmp/gar/util/tmp_gar.config'
    type_to_proceed = 'data'
    zip_region_folders_list = ''

    functions.process_config_file(config_file_full_path, type_to_proceed, zip_region_folders_list)

    end = time.time()
    print('Time taken in seconds: ', end - start)
