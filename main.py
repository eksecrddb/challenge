#!/usr/bin/env python3

from flask import Flask, jsonify, request
import boto3
from botocore.exceptions import ClientError
import time
import amazondax # dax addition

app = Flask(__name__)

daxurl='daxs://ratest.ls3ias.dax-clusters.eu-west-2.amazonaws.com'
dax = amazondax.AmazonDaxClient.resource(endpoint_url=daxurl)
table = dax.Table(ddbtable)

ddb = boto3.resource('dynamodb', region_name='eu-west-2')
ddbtable = 'movies'
#table = ddb.Table(ddbtable)


#function to track response time
def responsetime(start_time):
    elapsedtime = (time.time() - start_time) * 1000
    return (elapsedtime)

#api
@app.route('/movies', methods=['GET'])
def query_movies():
    try:
        start_time = time.time()
        title = request.args.get('title')
        year = request.args.get('year')
        genre = request.args.get('genre')
        actors = request.args.get('actors')

        if not any([title, year, genre, actors]):
            return jsonify({'error': 'Error please enter Title, Year, Genre, or Actors'})

        filter_expression = None
        expression_attribute_values = {} 
        expression_attribute_names = {}

        if title:
            filter_expression = 'contains (Title, :title)'
            expression_attribute_values[':title'] = title

        if year:
            filter_expression = '#yrs = :year' #year is a reserved word in DDB so need to add placeholder
            expression_attribute_values[':year'] = year
            expression_attribute_names['#yrs'] = 'Year'

        if genre:
            filter_expression = 'contains (Genre, :genre)'
            expression_attribute_values[':genre'] = genre

        if actors:
            filter_expression = 'contains (Actors, :actors)'
            expression_attribute_values[':actors'] = actors

        ddb_response = {
            'FilterExpression': filter_expression,
            'ExpressionAttributeValues': expression_attribute_values
        }

        if expression_attribute_names:
            response_params['ExpressionAttributeNames'] = expression_attribute_names

        response = table.scan(**ddb_response) 

        movies = response['Items']

        if not movies:
            return jsonify({'error': 'Error please enter valid movie'})

        formatted_response = {
            'movies': [{
                'Title': movie['Title'],
                'Year': movie['Year'],
                'Genre': movie['Genre'],
                'Actors': movie['Actors']
            } for movie in movies]
        }

        totaltime = responsetime(start_time)
        formatted_response['response_time_ms'] = totaltime

        return jsonify(formatted_response)

    except ClientError as mycodeerror:
        return jsonify({'error': str(mycodeerror)}) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

