import parse_xml
import read_zip

object_type = 'STEAD'
attributes_list = 'ID,OBJECTID,OBJECTGUID,CHANGEID,NUMBER,OPERTYPEID,PREVID,NEXTID,UPDATEDATE,STARTDATE,ENDDATE,ISACTUAL,ISACTIVE'
object_attributes = attributes_list.split(',')
separator = '<>'

#input_data = read_zip.get_objects('Z:\\garbage\\tmp\\gar\\data\\in\\full\\01\\AS_STEADS_20201231_1ff8acf7-020a-40ea-a68f-6d3110a2311e.XML', 2)
read_zip.get_objects('Z:\\garbage\\tmp\\gar\\data\\in\\delta\\gar_delta_xml.zip', 'AS_HOUSES')
#parse_xml.process_objects(object_type, object_attributes, separator, input_data)


