import zipfile
import re
import io
import xml.sax
import sys


def add_to_file(input_zip_file, files_to_fetch, output_plain_file):
    zip_data = zipfile.ZipFile(input_zip_file, 'r')
    file_list = zip_data.filelist
    output_plain_stream = open(output_plain_file, "a", 8192)

    for FileRecord in file_list:
        if re.match('^[0-9]{2}/' + files_to_fetch + '_[0-9]{8}_', FileRecord.filename) != 0:
            object_type = 'STEAD'
            attributes_list = 'ID,OBJECTID,OBJECTGUID,CHANGEID,NUMBER,OPERTYPEID,PREVID,NEXTID,UPDATEDATE,STARTDATE,ENDDATE,ISACTUAL,ISACTIVE'
            object_attributes = attributes_list.split(',')
            separator = '<>'

            input_xml_stream = io.BytesIO(zip_data.read(FileRecord.filename))
            parse_xml_data(object_type, object_attributes, separator, input_xml_stream)

    output_plain_stream.close()
    zip_data.close()


def parse_xml_data(object_type, object_attributes, separator, input_xml_stream, output_plain_stream):
    class MovieHandler(xml.sax.ContentHandler):

        # Call when an element starts
        def startElement(self, xml_tag, xml_attributes):
            if xml_tag == object_type:
                output_string = ''
                for object_attribute in object_attributes:

                    if xml_attributes.get(object_attribute) is not None:
                        attribute_value = xml_attributes.getValue(object_attribute)
                    else:
                        attribute_value = ''

                    output_string = output_string + attribute_value + separator

                print(output_string)
                output_plain_stream.writelines(output_string)

    parser_instance = xml.sax.make_parser()
    parser_instance.setContentHandler(MovieHandler())
    parser_instance.parse(input_xml_stream)
