import time
import functions

if __name__ == '__main__':
    start = time.time()
    functions.process_config_file('Z:/garbage/tmp/gar/util/gar2.config')
    # process_config_file(sys.argv[1])
    end = time.time()
    print('Time taken in seconds: ', end - start)
