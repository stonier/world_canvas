#!/usr/bin/env python

import rospy
import yaml
import random
import uuid
import unique_id
import cPickle as pickle
import world_canvas_msgs.msg
import world_canvas_msgs.srv

from geometry_msgs.msg import *
from rospy_message_converter import message_converter
from yocs_msgs.msg import Table, TableList
from world_canvas_msgs.msg import Annotation, AnnotationData

def read(filename):
    yaml_data = None 
    with open(filename) as f:
       yaml_data = yaml.load(f)

    anns_list = []
    data_list = []

    for t in yaml_data:
        ann = Annotation()
        ann.timestamp = rospy.Time.now()
        ann.world_id = unique_id.toMsg(uuid.UUID('urn:uuid:' + world_id))
        ann.data_id = unique_id.toMsg(unique_id.fromRandom())
        ann.id = unique_id.toMsg(unique_id.fromRandom())
        ann.name = t['name']
        ann.type = 'yocs_msgs/Table'
        for i in range(0, random.randint(0,11)):
            ann.keywords.append('kw'+str(random.randint(1,11)))
        if 'prev_id' in vars():
            ann.relationships.append(prev_id)
        prev_id = ann.id
        ann.shape = 3  #CYLINDER
        ann.color.r = 0.2
        ann.color.g = 0.2
        ann.color.b = 0.8
        ann.color.a = 0.5
        ann.size.x = float(t['radius'])*2
        ann.size.y = float(t['radius'])*2
        ann.size.z = float(t['height'])
        ann.pose.header.frame_id = t['frame_id']
        ann.pose.header.stamp = rospy.Time.now()
        ann.pose.pose.pose = message_converter.convert_dictionary_to_ros_message('geometry_msgs/Pose',t['pose'])
        
        # tables are assumed to lay on the floor, so z coordinate is zero;
        # but WCF assumes that the annotation pose is the center of the object
        ann.pose.pose.pose.position.z += ann.size.z/2.0

        anns_list.append(ann)

        object = Table()
        object.name = t['name']
        object.radius = float(t['radius'])
        object.height = float(t['height'])
        object.pose.header.frame_id = t['frame_id']
        object.pose.header.stamp = rospy.Time.now()
        object.pose.pose.pose = message_converter.convert_dictionary_to_ros_message('geometry_msgs/Pose',t['pose'])
        data = AnnotationData()
        data.id = ann.data_id
        data.data = pickle.dumps(object)
        
        data_list.append(data)
        
        print ann, object, data
    
    return anns_list, data_list

if __name__ == '__main__':
    rospy.init_node('tables_saver')
    world_id = rospy.get_param('~world_id')
    filename = rospy.get_param('~filename')
    anns, data = read(filename)

    print "Waiting for save_annotations_data service..."
    rospy.wait_for_service('save_annotations_data')
    save_srv = rospy.ServiceProxy('save_annotations_data', world_canvas_msgs.srv.SaveAnnotationsData)

    print 'Saving virtual tables from ', filename,' with world uuid ', world_id
    save_srv(unique_id.toMsg(uuid.UUID('urn:uuid:' + world_id)), anns, data)
    print "Done"
