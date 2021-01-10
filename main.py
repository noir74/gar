import time
import functions
import re

if __name__ == '__main__':
    start = time.time()

    # config_file_full_path = sys.argv[1]
    # zip_region_folders_list = sys.argv[2]

    config_file_full_path = 'Z:/garbage/tmp/gar/util/gar2.config'
    zip_region_folders_list = ''

    functions.process_config_file(config_file_full_path, zip_region_folders_list)

    end = time.time()
    print('Time taken in seconds: ', end - start)
