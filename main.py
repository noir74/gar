import configparser
import zipfile
import re
import io
import xml.sax
from threading import Thread
import codecs

def process_xml_file(xml_tag, xml_attributes, input_xml_stream, output_plain_stream):
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


def process_xml_type(xml_file, xml_tag, xml_attributes):
    zip_data = zipfile.ZipFile(InputFile, 'r')
    output_plain_stream = codecs.open(OutputDir + '/' + xml_file + '.out', mode='a+', buffering=8192, encoding='utf-8')

    for FileRecord in ArchiveFileList:
        match = re.match(XmlFilePrefix + xml_file + XmlFileSuffix, FileRecord.filename)

        if match:
            input_xml_stream = io.BytesIO(zip_data.read(FileRecord.filename))
            process_xml_file(xml_tag, xml_attributes, input_xml_stream, output_plain_stream)

    output_plain_stream.close()
    zip_data.close()


def process_config_file(config):
    threads = []
    for section in config.sections():
        if section != 'Common' and config.get(section, "process") == 'yes':
            xml_file = config.get(section, "xml_file")
            xml_tag = config.get(section, "xml_tag")
            xml_attributes = config.get(section, "xml_attributes").split(',')
            #process_xml_type(xml_file, xml_tag, xml_attributes)
            threads.append(Thread(target=process_xml_type, args=(xml_file, xml_tag, xml_attributes)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

# ConfigFile = sys.argv[1]
ConfigFile = 'Z:/garbage/tmp/gar/util/gar2.config'

config = configparser.ConfigParser()
config.readfp(codecs.open(ConfigFile, encoding='utf-8'))

InputFile = config.get("Common", "input_file")
OutputDir = config.get("Common", "output_dir")
XmlFilePrefix = config.get("Common", "xml_file_prefix")
XmlFileSuffix = config.get("Common", "xml_file_suffix")
FieldSeparator = config.get("Common", "field_separator")

ZipData = zipfile.ZipFile(InputFile, 'r')
ArchiveFileList = ZipData.filelist

process_config_file(config)

ZipData.close()
