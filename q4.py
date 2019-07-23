from google.cloud import vision
from google.cloud.vision import enums
from google.cloud.vision import types

from google.cloud import datastore

client = vision.ImageAnnotatorClient()

def object_detection(event, context):

    try:
        image = vision.types.Image()
        image.source.image_uri = 'gs://'+event['bucket']+'/'+event['name']

        response = client.label_detection(image=image)
        labels = response.label_annotations

        l = []

        for label in labels:
            l.append(label.description)

        print(l)
        c = datastore.Client()
        entity = datastore.Entity(c.key('ketav'))
        entity.update({'label':l})
        c.put(entity)
        
    except:
        print("Error! Please check your code")