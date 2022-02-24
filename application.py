import dash
import dash_core_components as dcc
from dash import html
from dash.dependencies import Input, Output
import boto3
import json

BUCKET_ARN = "arn:aws:s3-object-lambda:us-east-2:650805712162:accesspoint/dg-tri-challenge-lambda-access-point"
# This is a READ-ONLY key, not secret for the purpose of this exercise
s3 = boto3.client('s3',
                  aws_access_key_id='XXXXXXXXXXXXXXXXXXXX',
                  aws_secret_access_key='XXXXXXXXXXXXXXXXXXXX')

def getJSONObject(bucket, key):
    objectBody = s3.get_object(Bucket = bucket, Key = key)
    return json.loads(objectBody["Body"].read().decode("utf-8"))

app = dash.Dash(__name__)
application = app.server
app.title='Online Plot Viewer'


app.layout = html.Div(children=[
    html.H1(children='Online Plot Viewer with Live Data Updates'),
    html.Div(children='''
            Live Data Aggregation
        '''),
    dcc.Graph(
            id='example-graph'),
    dcc.Interval(
            id='interval-component',
            interval=5*1000,
            n_intervals=0
    )
])

@app.callback(Output('example-graph', 'figure'),
	          Input('interval-component', 'n_intervals'))
def update_plot(n):
    new_figure={
		'data':  getJSONObject(BUCKET_ARN, 'unused'),
        'layout': {
            'plot_bgcolor': 'lightgray',
            'title': 'Collected from ' + BUCKET_ARN,
            'xaxis':{'title':'x_values'},
            'yaxis':{'title':'y_values'},
        },
    }
    return new_figure

########### Run the app
if __name__ == '__main__':
    application.run(debug=True, port=8080)