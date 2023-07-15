import json
import boto3

ddb_table = 'movies'
bucket_name = 'ramoviesbucket'
s3_key = 'movieData.json' 

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(ddb_table)
    bucket = bucket_name
    key = s3_key
    
#get from S3 
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=bucket, Key=key)
    file_content = response['Body'].read().decode('utf-8')
    movie_data = json.loads(file_content)
    
#attributes within file
    title = movie_data['Title']
    year = movie_data['Year']
    genre = movie_data['Genre']
    actors = movie_data['Actors']
    
    item = {
        'Title': title,
        'Year': year,
        'Genre': genre,
        'Actors': actors
    }
    
#push to ddb
    table.put_item(Item=item)
    
    return {
        'statusCode': 200,
        'body': 'Movie data has been pushed to DDB'
    }

