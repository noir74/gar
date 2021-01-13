import configparser
import zipfile
import re
import io
import codecs
import xml.sax
from datetime import datetime, date
from multiprocessing import Pool


class XmlTypeProcessingParameters:

    def __init__(self, input_zip_file, zip_region_folders_list, output_dir, xml_file_search_prefix,
                 xml_file_search_suffix, field_separator, output_file_mode,
                 xml_file, xml_file_type, xml_tag, xml_attributes, xml_data_check_if_actual, xml_data_check_if_active,
                 xml_data_check_for_date):
        self.__input_zip_file = input_zip_file
        self.__zip_region_folders_list = zip_region_folders_list
        self.__output_dir = output_dir
        self.__xml_file_search_prefix = xml_file_search_prefix
        self.__xml_file_search_suffix = xml_file_search_suffix
        self.__field_separator = field_separator
        self.__output_file_mode = output_file_mode
        self.__xml_file = xml_file
        self.__xml_file_type = xml_file_type
        self.__xml_tag = xml_tag
        self.__xml_attributes = xml_attributes
        self.__xml_data_check_if_actual = xml_data_check_if_actual
        self.__xml_data_check_if_active = xml_data_check_if_active
        self.__xml_data_check_for_date = xml_data_check_for_date

    @property
    def input_zip_file(self):
        return self.__input_zip_file

    @property
    def zip_region_folders_list(self):
        return self.__zip_region_folders_list

    @property
    def output_dir(self):
        return self.__output_dir

    @property
    def xml_file_search_prefix(self):
        return self.__xml_file_search_prefix

    @property
    def xml_file_search_suffix(self):
        return self.__xml_file_search_suffix

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
    def xml_file_type(self):
        return self.__xml_file_type

    @property
    def xml_tag(self):
        return self.__xml_tag

    @property
    def xml_attributes(self):
        return self.__xml_attributes

    @property
    def xml_data_check_if_actual(self):
        return self.__xml_data_check_if_actual

    @property
    def xml_data_check_if_active(self):
        return self.__xml_data_check_if_active

    @property
    def xml_data_check_for_date(self):
        return self.__xml_data_check_for_date


def process_xml_type(proc_params):
    def process_xml_file():
        class MovieHandler(xml.sax.ContentHandler):

            # Call when an element starts
            def startElement(self, source_xml_tag, source_xml_attributes):
                if source_xml_tag == proc_params.xml_tag:
                    if proc_params.xml_data_check_if_actual and source_xml_attributes.get('ISACTUAL') != 1:
                        return

                    if proc_params.xml_data_check_if_active and source_xml_attributes.get('ISACTIVE') != 1:
                        return

                    if proc_params.xml_data_check_for_date:
                        start_date = datetime.strptime(source_xml_attributes.get('STARTDATE'),'%Y-%m-%d')
                        end_date = datetime.strptime(source_xml_attributes.get('ENDDATE'), '%Y-%m-%d')
                        if not (start_date < datetime.now() < end_date):
                            return

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

    output_file_name = proc_params.output_dir + '/' + proc_params.xml_file + '.txt'
    output_plain_stream = codecs.open(output_file_name, mode=proc_params.output_file_mode, buffering=8192,
                                      encoding='utf-8')

    zip_data = zipfile.ZipFile(proc_params.input_zip_file, 'r')
    archive_file_list = zip_data.filelist

    if proc_params.xml_file_type == 'data' and proc_params.zip_region_folders_list != '':
        xml_file_search_prefix_final = '(' + proc_params.zip_region_folders_list.replace(',', '|') + ')/'
    else:
        xml_file_search_prefix_final = proc_params.xml_file_search_prefix

    search_pattern = xml_file_search_prefix_final + proc_params.xml_file + proc_params.xml_file_search_suffix

    for FileRecord in archive_file_list:
        match = re.match(search_pattern, FileRecord.filename)
        if match:
            input_xml_stream = io.BytesIO(zip_data.read(FileRecord.filename))
            process_xml_file()

    output_plain_stream.close()
    zip_data.close()


def process_config_file(config_file, data_type_to_process, zip_region_folders_list):
    def get_config_parameter(section, parameter_name):
        try:
            parameter_value = gar_config_file.get(section, parameter_name)
        except configparser.NoOptionError:
            parameter_value = gar_config_file.get('Common', parameter_name)
        return parameter_value

    def check_boolean_config_parameter(section, parameter_name):
        try:
            parameter_value = gar_config_file.getboolean(section, parameter_name)
        except configparser.NoOptionError:
            parameter_value = gar_config_file.getboolean('Common', parameter_name)
        return parameter_value

    gar_config_file = configparser.ConfigParser()
    gar_config_file.readfp(codecs.open(config_file, encoding='utf-8'))

    args = []

    for gar_config_section in gar_config_file.sections():
        if gar_config_section != 'Common' and check_boolean_config_parameter(gar_config_section, 'enabled'):
            xml_file_type = gar_config_file.get(gar_config_section, "xml_file_type")
            if xml_file_type == data_type_to_process:
                input_zip_file = get_config_parameter(gar_config_section, "input_zip_file")
                output_dir = get_config_parameter(gar_config_section, "output_dir")
                xml_file_search_prefix = get_config_parameter(gar_config_section, "xml_file_search_prefix")
                xml_file_search_suffix = get_config_parameter(gar_config_section, "xml_file_search_suffix")
                field_separator = get_config_parameter(gar_config_section, "field_separator")
                output_file_mode = get_config_parameter(gar_config_section, "output_file_mode")
                xml_file = get_config_parameter(gar_config_section, "xml_file")
                xml_tag = get_config_parameter(gar_config_section, "xml_tag")
                xml_attributes = get_config_parameter(gar_config_section, "xml_attributes").split(',')
                xml_data_check_if_actual = check_boolean_config_parameter(gar_config_section,
                                                                          'xml_data_check_if_actual')
                xml_data_check_if_active = check_boolean_config_parameter(gar_config_section,
                                                                          'xml_data_check_if_active')
                xml_data_check_for_date = check_boolean_config_parameter(gar_config_section,
                                                                         'xml_data_check_for_date')

                processing_parameters = XmlTypeProcessingParameters(input_zip_file, zip_region_folders_list, output_dir,
                                                                    xml_file_search_prefix,
                                                                    xml_file_search_suffix,
                                                                    field_separator, output_file_mode,
                                                                    xml_file, xml_file_type, xml_tag, xml_attributes,
                                                                    xml_data_check_if_actual, xml_data_check_if_active,
                                                                    xml_data_check_for_date)

                # process_xml_type(processing_parameters)
                args.append(processing_parameters)

    processes_pool = Pool(gar_config_file.getint('Common', 'processes'))
    processes_pool.map(process_xml_type, args)
