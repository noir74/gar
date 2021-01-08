import configparser
import zipfile
import re
import io
import codecs
import xml.sax
from multiprocessing import Process
import time


def process_xml_type(xml_file, xml_tag, xml_attributes, gar_config_section):
    def process_xml_file():
        class MovieHandler(xml.sax.ContentHandler):

            # Call when an element starts
            def startElement(self, source_xml_tag, source_xml_attributes):
                if source_xml_tag == xml_tag:
                    output_string = ''
                    for xml_attribute in xml_attributes:

                        if source_xml_attributes.get(xml_attribute) is not None:
                            attribute_value = source_xml_attributes.getValue(xml_attribute)
                        else:
                            attribute_value = ''

                        output_string = output_string + attribute_value + FieldSeparator

                    output_plain_stream.writelines(output_string + '\n')

        parser_instance = xml.sax.make_parser()
        parser_instance.setContentHandler(MovieHandler())
        parser_instance.parse(input_xml_stream)

    try:
        xml_type_enabled = GarConfig.getboolean(gar_config_section, "enabled")
    except configparser.NoOptionError:
        xml_type_enabled = XmlTypeEnabled

    if xml_type_enabled:
        try:
            xml_file_prefix = GarConfig.get(gar_config_section, "xml_file_prefix")
        except configparser.NoOptionError:
            xml_file_prefix = XmlFilePrefix

        try:
            xml_file_suffix = GarConfig.get(gar_config_section, "xml_file_suffix")
        except configparser.NoOptionError:
            xml_file_suffix = XmlFileSuffix

        try:
            output_file_mode = GarConfig.get(gar_config_section, "output_file_mode")
        except configparser.NoOptionError:
            output_file_mode = OutputFileMode

        if output_file_mode == 'append':
            output_file_mode = 'a'
        elif output_file_mode == 'overwrite':
            output_file_mode = 'w'

        output_file_name = OutputDir + '/' + xml_file + '.out'

        output_plain_stream = codecs.open(output_file_name, mode=output_file_mode, buffering=8192, encoding='utf-8')
        zip_data = zipfile.ZipFile(InputFile, 'r')

        for FileRecord in ArchiveFileList:
            match = re.match(xml_file_prefix + xml_file + xml_file_suffix, FileRecord.filename)

            if match:
                input_xml_stream = io.BytesIO(zip_data.read(FileRecord.filename))
                process_xml_file()

        output_plain_stream.close()
        zip_data.close()


def process_config_file(config):
    procs = []
    for gar_config_section in config.sections():
        if gar_config_section != 'Common':
            xml_file = GarConfig.get(gar_config_section, "xml_file")
            xml_tag = GarConfig.get(gar_config_section, "xml_tag")
            xml_attributes = GarConfig.get(gar_config_section, "xml_attributes").split(',')
            # process_xml_type(xml_file, xml_tag, xml_attributes, gar_config_section)
            proc = Process(target=process_xml_type, args=(xml_file, xml_tag, xml_attributes, gar_config_section,))
            procs.append(proc)

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()


# ConfigFile = sys.argv[1]
ConfigFile = 'Z:/garbage/tmp/gar/util/gar2.config'

GarConfig = configparser.ConfigParser()
GarConfig.readfp(codecs.open(ConfigFile, encoding='utf-8'))

InputFile = GarConfig.get("Common", "input_file")
OutputDir = GarConfig.get("Common", "output_dir")
XmlFilePrefix = GarConfig.get("Common", "xml_file_prefix")
XmlFileSuffix = GarConfig.get("Common", "xml_file_suffix")
FieldSeparator = GarConfig.get("Common", "field_separator")
OutputFileMode = GarConfig.get("Common", "output_file_mode")
XmlTypeEnabled = GarConfig.getboolean("Common", "enabled")

ZipData = zipfile.ZipFile(InputFile, 'r')
ArchiveFileList = ZipData.filelist

if __name__ == '__main__':
    start = time.time()
    process_config_file(GarConfig)
    end = time.time()
    print('Time taken in seconds: ', end - start)

ZipData.close()
