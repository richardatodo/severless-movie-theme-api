from typing import Optional
from boto3.dynamodb.conditions import Attr, Key
import boto3.resources
from botocore.exceptions import ClientError
from mangum import Mangum
from fastapi import FastAPI, HTTPException, Query
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import boto3

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in .env file.")
OpenAI.api_key = OPENAI_API_KEY

app = FastAPI()

client = OpenAI()
dynamodb = boto3.resource("dynamodb")
movie_table = dynamodb.Table(os.getenv("MOVIE_TABLE"))

# Read data.json at startup
try:
    with open("movies.json", "r") as f:
        movies = json.load(f)
except FileNotFoundError:
    movies = []
    print("movies.json file not found!")
except json.JSONDecodeError:
    movies = []
    print("Error decoding JSON data.")

# Export JSON file to DynamoDB
if movies:
    for movie in movies:
        try:
            movie_table.put_item(Item=movie)
        except ClientError as e:
            print(f"Error inserting item into DynamoDB: {str(e)}")
    print(f"Successfully exported data from {movies} to DynamoDB table {movie_table}")
else:
    print("No data loaded due to previous errors.")

# Home
@app.get("/")
def read_root():
    return {"Welcome to the Movie Theme Song Finder API!"}

# Get all movies
@app.get("/api/movies")
async def get_all():
    response = movie_table.scan()
    return {"movies": response["Items"]}

# Get movie by id
@app.get("/api/movies/id/{id}")
async def get_by_id(id: int):
    response = movie_table.get_item(Key={"id": id})
    if "Item" not in response:
        raise HTTPException(
            status_code=404, 
            detail="This movie is currently not available. Please check again later."
        )
    return {"movie": response["Item"]}

# Search Movies by Title or Genre or Artist or Song Title
@app.get("/api/movies/search")
async def search(
    title: Optional[str] = Query(None, description="Search by movie title"),
    genre: Optional[str] = Query(None, description="Search by movie genre"),
    artist: Optional[str] = Query(None, description="Search by artist of the theme song"),
    theme_song_title: Optional[str] = Query(None, description="Search by theme song title")
):
    # Build filter expressions
    filtered_movies = None
    if title:
        filtered_movies = Attr("title").contains(title)
    if genre:
        filtered_movies = (
            filtered_movies & Attr("genre").contains(genre)
            if filtered_movies
            else Attr("genre").contains(genre)
        )
    if artist:
        filtered_movies = (
            filtered_movies & Attr("theme_song.artist").contains(artist)
            if filtered_movies
            else Attr("theme_song.artist").contains(artist)
        )
    if theme_song_title:
        filtered_movies = (
            filtered_movies & Attr("theme_song.title").contains(theme_song_title)
            if filtered_movies
            else Attr("theme_song.title").contains(theme_song_title)
        )
    # Perform scan operation
    try:
        response = movie_table.scan(FilterExpression=filtered_movies) if filtered_movies else movie_table.scan()
        movies = response.get("Items", [])
        if not movies:
            raise HTTPException(
                status_code=404,
                detail="No movie matched your criteria"
            )
        return {"result": movies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying DynamoDB: {str(e)}")

# Get movies by year   
@app.get("/api/movies/year/{year}")
async def get_by_year(year: int):
    try:
        response = movie_table.scan(FilterExpression=Attr("year").eq(year))
        movies = response.get("Items", [])
        if not movies:
            raise HTTPException(
                status_code=404, 
                detail=f"We don't have any {year} movies currently. Please check again later."
            )
        return {"movies": movies}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying movies by year: {str(e)}"
        )

# Get movie summary
def generate_movie_summary(title: str, year: int, genre: str) -> str:
    """
    Generate Movie Summary from OpenAI API
    """
    prompt = (
        f"Write a concise and engaging summary for a movie titled '{title}' "
        f"released in {year}. The genre of the movie is {genre}. "
        f"Focus on the plot and main themes without revealing spoilers."
    )

    try:
        response = client.chat_completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert movie reviewer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error generating summary: {str(e)}"

@app.get("/api/movies/summary/{id}")
async def get_movie_summary(id: int):
    """
    AI Generated Movie Summary by ID.
    Stores the summary in DynamoDB if it does not exist.
    """
    try:
        # Check if movie exists
        response = movie_table.query(
            KeyConditionExpression=Key("id").eq(id)
        )
        movie = response.get("Items", [])
        if not movie:
            raise HTTPException(status_code=404, detail="Movie Not Found")
        movie = movie[0]

        # Check if summary already exists
        if "summary" in movie and movie["summary"]:
            return {
                "id": movie["id"],
                "title": movie["title"],
                "summary": movie["summary"]
            }

        # Generate a new summary
        summary = generate_movie_summary(movie["title"], movie["year"], movie["genre"])

        # Update the movie with the new summary
        movie_table.update_item(
            Key={"id": id},
            UpdateExpression="SET summary = :s",
            ExpressionAttributeValues={":s": summary}
        )
        return {
            "id": movie["id"],
            "title": movie["title"],
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving or generating movie summary: {str(e)}"
        )

handler = Mangum(app)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)
