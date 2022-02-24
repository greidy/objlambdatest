import boto3
import json

s3 = boto3.client('s3')
BUCKET_NAME = "dg-tri-challenge-bucket"

def getAllJSONNames(bucket):
    requested_bucket = s3.list_objects_v2(Bucket = bucket)
    #print(requested_bucket)
    return map(lambda k: k['Key'],
               filter(lambda o: o['Key'].endswith(".json"), requested_bucket['Contents']))

def getObjectAsJson(bucket, key):
    object_content = s3.get_object(Bucket = bucket, Key = key)
    try :
        plot = json.loads(object_content["Body"].read().decode("utf-8"))
        if (plot['x_values'] == None or plot['y_values'] == None):
            raise Exception("Invalid plot data")

        if (len(plot['x_values']) != len(plot['y_values'])):
            raise Exception("Plot data mismatch")

        return { 'x': plot['x_values'], 'y': plot['y_values'], 'type': 'line', 'name': key}
    except:
        return None

def transformAllPlotData(bucket):
    all_plot_names = getAllJSONNames(BUCKET_NAME)
    all_plot_data = []
    for plot_name in all_plot_names:
        #print(plot_name)
        plot_data = getObjectAsJson(BUCKET_NAME, plot_name)
        if (plot_data != None):
            all_plot_data.append(plot_data)

    #print(all_plot_data)
    return all_plot_data

def lambda_handler(event, context):
    object_context = event["getObjectContext"]

    # Extract the route and request token from the input context
    request_route = object_context["outputRoute"]
    request_token = object_context["outputToken"]

    # generate the aggregated and transformed plot data (json format)
    aggregated_plot_data = json.dumps(transformAllPlotData(BUCKET_NAME))

    # Write object back to S3 Object Lambda
    s3 = boto3.client('s3')
    # The WriteGetObjectResponse API sends the transformed data
    # back to S3 Object Lambda and then to the user
    s3.write_get_object_response(
        Body=aggregated_plot_data,
        RequestRoute=request_route,
        RequestToken=request_token)

    # Exit the Lambda function: return the status code
    return {'status_code': 200}
