# Serverless-Movie-Theme-API

A **FastAPI-based API** that allows users to search for movies by title, genre, artist, or theme song title. The API also integrates with **OpenAI** to generate AI-powered movie summaries, making it an innovative and versatile tool for movie enthusiasts and developers. The project leverages various **AWS services** for scalability and performance.

---

## Features

- Search for movies by:
  - **Title**
  - **Genre**
  - **Theme song artist**
  - **Theme song title**
- Case-insensitive, flexible search capabilities.
- AI-generated movie summaries using OpenAI.
- Seamless integration with **DynamoDB** for data storage.
- Serverless deployment using **AWS Lambda**.
- API management via **Amazon API Gateway**.
- Static files hosted on **Amazon S3**.

---

## AWS Services Used

1. **AWS Lambda**  
   - Executes the FastAPI application as a serverless function.
2. **Amazon API Gateway**  
   - Provides an API layer for interacting with the Lambda function.
3. **Amazon DynamoDB**  
   - Stores movie data and summary results for quick access.
4. **Amazon S3**  
   - Hosts static assets and supports file-based operations.

---

## Getting Started

### Prerequisites

- **Python 3.9** or later.
- An **AWS account** with permissions for Lambda, API Gateway, DynamoDB, and S3.
- An **OpenAI API key** for AI-generated summaries.

---

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/richardatodo/movie-theme-api.git
   cd movie-theme-api

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt

3. **Set Up Environment Variables** Create a .env file in the project root and add your configurations:
    OPENAI_API_KEY=your_openai_api_key
    AWS_REGION=your_aws_region
    DYNAMODB_TABLE_NAME=your_dynamodb_table_name
Replace placeholders with your specific values.

4. **Run the Application Locally**

5. Open your browser and navigate to:
   * Interactive API Docs: http://127.0.0.1:8000/docs
   * ReDoc Documentation: http://127.0.0.1:8000/redoc

### API Endpoints
#### Home
* GET /
  * Description: Displays a welcome message.

#### Get All Movies
* `GET /api/movies`
  * Description: Returns all available movies.

#### Get Movie by ID
* `GET /api/movies/id/{id}`
  * Description: Fetch a movie by its ID.
  * Parameters:
    * `id` (int): Movie ID.

#### Search Movies
* `GET /api/movies/search`
   * Description: Search for movies using various criteria.
   * Query Parameters:
     * `title` (str, optional): Search by movie title.
     * `genre` (str, optional): Search by movie genre.
     * `artist` (str, optional): Search by theme song artist.
     * `theme_song_title` (str, optional): Search by theme song title.

#### Get Movies by Year
* `GET /api/movies/year/{year}`
   * Description: Get movies released in a specific year.
   * Parameters:
     * `year` (int): Release year.

#### AI-Generated Movie Summary
* `GET /api/movies/summary/{id}`
   * Generate a concise, engaging summary for a specific movie.
   * Parameters:
     * `Id`(int): Movie ID.
   * Requires:
     * A valid OpenAI API Key.

---

### Deployment to AWS
The infra_setup.py will setup AWS Lambda, Amazon S3, APIGATEWAY, and DynamoDB. 
1. **Package the Application**
* Zip the application with dependencies using a tool like pip install --target ./ package and zip the directory.
* Create a Lambda Function

2. **Upload the zipped file to AWS Lambda.**
* Set up the environment variables (OPENAI_API_KEY, AWS_REGION, DYNAMODB_TABLE_NAME).
* Set Up API Gateway

3. **Create a new REST API or HTTP API.**
* Integrate with the Lambda function.

4. **Set Up DynamoDB**
* Create a DynamoDB table with the appropriate schema.

5. **Deploy Static Files to S3**
* Upload any static assets to an S3 bucket.
* Configure S3 bucket permissions and hosting if required.

6. **Test the Deployment**
* Use Postman, cURL, or the API Gateway console to test the endpoints.

---

### Contributing
If you find any issues or have suggestions, feel free to open an issue or submit a pull request or reach out to me.
* **Ameh Richard Atodo** [@RichardAtodo](https://x.com/RichardAtodo)