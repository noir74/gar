import configparser
import zipfile
import re
import io
import codecs
import xml.sax
from multiprocessing import Process
import time


class XmlTypeProcessingParameters:

    def __init__(self, input_file, output_dir, xml_file_prefix, xml_file_suffix, field_separator, output_file_mode,
                 xml_file, xml_tag, xml_attributes):
        self.__input_file = input_file
        self.__output_dir = output_dir
        self.__xml_file_prefix = xml_file_prefix
        self.__xml_file_suffix = xml_file_suffix
        self.__field_separator = field_separator
        self.__output_file_mode = output_file_mode
        self.__xml_file = xml_file
        self.__xml_tag = xml_tag
        self.__xml_attributes = xml_attributes

    @property
    def input_file(self):
        return self.__input_file

    @property
    def output_dir(self):
        return self.__output_dir

    @property
    def xml_file_prefix(self):
        return self.__xml_file_prefix

    @property
    def xml_file_suffix(self):
        return self.__xml_file_suffix

    @property
    def field_separator(self):
        return self.__field_separator

    @property
    def output_file_mode(self):
        return self.__output_file_mode

    @property
    def xml_file(self):
        return self.__xml_file

    @property
    def xml_tag(self):
        return self.__xml_tag

    @property
    def xml_attributes(self):
        return self.__xml_attributes


def process_xml_type(proc_params):
    def process_xml_file():
        class MovieHandler(xml.sax.ContentHandler):

            # Call when an element starts
            def startElement(self, source_xml_tag, source_xml_attributes):
                if source_xml_tag == proc_params.xml_tag:
                    output_string = ''
                    for xml_attribute in proc_params.xml_attributes:

                        if source_xml_attributes.get(xml_attribute) is not None:
                            attribute_value = source_xml_attributes.getValue(xml_attribute)
                        else:
                            attribute_value = ''

                        output_string = output_string + attribute_value + proc_params.field_separator

                    output_plain_stream.writelines(output_string + '\n')

        parser_instance = xml.sax.make_parser()
        parser_instance.setContentHandler(MovieHandler())
        parser_instance.parse(input_xml_stream)

    output_file_name = proc_params.output_dir + '/' + proc_params.xml_file + '.out'
    output_plain_stream = codecs.open(output_file_name, mode=proc_params.output_file_mode, buffering=8192,
                                      encoding='utf-8')

    zip_data = zipfile.ZipFile(proc_params.input_file, 'r')
    archive_file_list = zip_data.filelist

    for FileRecord in archive_file_list:
        match = re.match(
            proc_params.xml_file_prefix + proc_params.xml_file + proc_params.xml_file_suffix,
            FileRecord.filename)
        if match:
            input_xml_stream = io.BytesIO(zip_data.read(FileRecord.filename))
            process_xml_file()

    output_plain_stream.close()
    zip_data.close()


def process_config_file(config_file):
    def get_config_parameter(section, parameter_name):
        try:
            parameter_value = gar_config_file.get(section, parameter_name)
        except configparser.NoOptionError:
            parameter_value = gar_config_file.get('Common', parameter_name)
        return parameter_value

    def if_xml_type_enabled(section):
        try:
            parameter_value = gar_config_file.getboolean(section, 'enabled')
        except configparser.NoOptionError:
            parameter_value = gar_config_file.getboolean('Common', 'enabled')
        return parameter_value

    procs = []

    gar_config_file = configparser.ConfigParser()
    gar_config_file.readfp(codecs.open(config_file, encoding='utf-8'))

    for gar_config_section in gar_config_file.sections():
        if gar_config_section != 'Common' and if_xml_type_enabled(gar_config_section):
            input_file = get_config_parameter(gar_config_section, "input_file")
            output_dir = get_config_parameter(gar_config_section, "output_dir")
            xml_file_prefix = get_config_parameter(gar_config_section, "xml_file_prefix")
            xml_file_suffix = get_config_parameter(gar_config_section, "xml_file_suffix")
            field_separator = get_config_parameter(gar_config_section, "field_separator")
            output_file_mode = get_config_parameter(gar_config_section, "output_file_mode")
            xml_file = get_config_parameter(gar_config_section, "xml_file")
            xml_tag = get_config_parameter(gar_config_section, "xml_tag")
            xml_attributes = get_config_parameter(gar_config_section, "xml_attributes").split(',')

            processing_parameters = XmlTypeProcessingParameters(input_file, output_dir, xml_file_prefix,
                                                                xml_file_suffix,
                                                                field_separator, output_file_mode,
                                                                xml_file, xml_tag, xml_attributes)

            #process_xml_type(processing_parameters)
            proc = Process(target=process_xml_type, args=(processing_parameters,))
            procs.append(proc)

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()


if __name__ == '__main__':
    start = time.time()
    process_config_file('Z:/garbage/tmp/gar/util/gar2.config')
    # process_config_file(sys.argv[1])
    end = time.time()
    print('Time taken in seconds: ', end - start)
