from google.cloud import monitoring_v3
import base64
import time
from datetime import datetime
import logging
import csv
import io
from google.cloud import storage
from google.cloud.storage import Blob

import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message

from email.mime.text import MIMEText
import smtplib


PROJECT_ID = "pe-training"

def cloud_monitoring_report(request):

    # Monitoring API for CPU utilization
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path(PROJECT_ID)  

    interval = monitoring_v3.types.TimeInterval()
    now = time.time()

    interval.end_time.seconds = int(now)
    interval.end_time.nanos = int((now - interval.end_time.seconds) * 10 ** 9)  

    interval.start_time.seconds = int(now - 604800) 
    interval.start_time.nanos = interval.end_time.nanos

    aggregation = monitoring_v3.types.Aggregation()
    aggregation.alignment_period.seconds = 86400  
    aggregation.per_series_aligner = monitoring_v3.enums.Aggregation.Aligner.ALIGN_MEAN


    results = client.list_time_series(
        project_name,
        'metric.type = "compute.googleapis.com/instance/cpu/utilization"',
        interval,
        monitoring_v3.enums.ListTimeSeriesRequest.TimeSeriesView.FULL,
        aggregation)

    # Creating CSV file for CPU utilization metric
    csvstring = io.StringIO()
    headers = ["Instance ID", "Date 1", "Usage", "Date 2", "Usage", "Date 3", "Usage",
               "Date 4", "Usage", "Date 5", "Usage", "Date 6", "Usage", "Date 7", "Usage"]

    writer = csv.writer(csvstring, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(headers)
    for result in results:

        row = [result.resource.labels["instance_id"]]

        for point in result.points:
            row.append(datetime.utcfromtimestamp(int(point.interval.start_time.seconds)).strftime('%Y-%m-%d'))
            row.append(point.value.double_value)  

        writer.writerow(row)

    logging.info(csvstring.getvalue())
    csvstring.seek(0)

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y")

    # Upload csv file to cloud storage
    client = storage.Client(project=PROJECT_ID)
    bucket = client.get_bucket('ketav-source')
    blob = Blob(timestampStr, bucket)
    blob.upload_from_file(csvstring, content_type='text/csv')


    # Send Email
    msg = MIMEMultipart()
     
     
    message = "https://storage.cloud.google.com/ketav-source/"+timestampStr

    password = [YOUR PASSWORD]
    msg['From'] = [YOUR EMAIL ID]
    msg['To'] = [DEV OPS EMAIL ID]
    msg['Subject'] = "Report"
     
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
     
    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
     
    server.starttls()
     
    # Login Credentials for sending the mail
    server.login(msg['From'], password)
     
     
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
     
    server.quit()
