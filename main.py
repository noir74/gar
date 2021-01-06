import functions

object_type = 'STEAD'
attributes_list = 'ID,OBJECTID,OBJECTGUID,CHANGEID,NUMBER,OPERTYPEID,PREVID,NEXTID,UPDATEDATE,STARTDATE,ENDDATE,ISACTUAL,ISACTIVE'
object_attributes = attributes_list.split(',')
separator = '<>'

functions.add_to_file('Z:/garbage/tmp/gar/data/in/delta/gar_delta_xml.zip', 'AS_HOUSES', 'Z:/garbage/tmp/gar/data/out/delta/AS_HOUSES.out')

