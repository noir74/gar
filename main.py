import configparser
import zipfile
import re
import io
import xml.sax


def process_xml_file(xml_tag, xml_attributes, input_xml_stream, output_plain_stream, source_file):
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

                    output_string = output_string + attribute_value + field_separator

                output_plain_stream.writelines(source_file + ': ' + output_string + '\n')

    parser_instance = xml.sax.make_parser()
    parser_instance.setContentHandler(MovieHandler())
    parser_instance.parse(input_xml_stream)


def process_xml_type(xml_file, xml_tag, xml_attributes):
    zip_data = zipfile.ZipFile(input_file, 'r')
    archive_file_list = zip_data.filelist
    output_plain_stream = open(output_dir + '/' + xml_file + '.out', mode='a+', buffering=8192, encoding='utf-8')

    for FileRecord in archive_file_list:
        match = re.match(xml_file_prefix + xml_file + xml_file_suffix, FileRecord.filename)

        if match:
            input_xml_stream = io.BytesIO(zip_data.read(FileRecord.filename))
            process_xml_file(xml_tag, xml_attributes, input_xml_stream, output_plain_stream, FileRecord.filename)

    output_plain_stream.close()
    zip_data.close()


def process_config_file(config):
    for section in config.sections():
        if section != 'Common' and config.get(section, "process") == 'yes':
            xml_file = config.get(section, "xml_file")
            xml_tag = config.get(section, "xml_tag")
            xml_attributes = config.get(section, "xml_attributes").split(',')
            process_xml_type(xml_file, xml_tag, xml_attributes)


# config_file = sys.argv[1]
config_file = 'Z:/garbage/tmp/gar/util/gar2.config'

config = configparser.ConfigParser()
config.readfp(open(config_file, encoding='utf-8'))

input_file = config.get("Common", "input_file")
output_dir = config.get("Common", "output_dir")
xml_file_prefix = config.get("Common", "xml_file_prefix")
xml_file_suffix = config.get("Common", "xml_file_suffix")
field_separator = config.get("Common", "field_separator")

process_config_file(config)
