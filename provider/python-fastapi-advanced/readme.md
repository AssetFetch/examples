# Advanced FastAPI Provider Example
This is a more advanced example implementation of an AssetFetch provider.
It offers materials, HDRIs and 3D models to authenticated in exchange for credits which can be added to an account via a simple web interface to simulate user sign-ups and purchases.

# Setup
This example uses Python along with the FastAPI framework which broadly offers two ways of running the application:

## Manual Setup
- Install Python 3.8 or newer
- Install FastAPI, [as described on the website](https://fastapi.tiangolo.com/#requirements).
- Open a terminal in the `app` subdirectory
- Set the environment variables:
  - `AF_MODEL_DIRECTORY` to the full path to the `models` directory
  - `AF_API_URL` to the path on which the application will run (usually `http://localhost:8001`)
- Run the application with `uvicorn main:app --host 0.0.0.0 --port 8001 --reload`
  - Make sure the port defined here matches the one in `AF_API_URL`

## Docker Setup
If you have docker installed, you can simply perform `docker compose up`.
The application will be available on `http://localhost:8001`

# Interaction
After starting the application the initialization endpoint can be reached via the path `/`, so the full URL is `http://localhost:8001/` if you didn't change any of the settings.