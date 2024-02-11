# Minimal FastAPI Provider Example
This is a very minimal example implementation of an AssetFetch provider in under 200 lines of Python and FastAPI code.
It offers a list of untextured low-poly OBJ models for download.

It lacks many more advanced features like filtering, pagination or auth.

# Setup
This example uses Python along with the FastAPI framework which broadly offers two ways of running the application:

## Manual Setup
- Install Python 3.8 or newer
- Install FastAPI, [as described on the website](https://fastapi.tiangolo.com/#requirements).
- Open a terminal in the `app` subdirectory
- Set the environment variables:
  - `AF_MODEL_DIRECTORY` to the full path to the `models` directory
  - `AF_API_URL` to the path on which the application will run (usually `http://localhost:8000`)
- Run the application with `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
  - Make sure the port defined here matches the one in `AF_API_URL`

## Docker Setup
If you have docker installed, you can simply perform `docker compose up`.

# Interaction
After starting the application the initialization endpoint can be reached via the path `/`, so the full URL is `http://localhost:8000/` if you didn't change any of the settings.