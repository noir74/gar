import xml.sax, sys


def process_objects(object_type, object_attributes, separator, input_data):
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

    parser_instance = xml.sax.make_parser()
    parser_instance.setContentHandler(MovieHandler())

    # parser_instance.parse(sys.stdin)
    parser_instance.parse(input_data)
