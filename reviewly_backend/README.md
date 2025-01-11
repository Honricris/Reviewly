# Reviewly_backend




DATABASE_URL=
EDEN_API_TOKEN=
EDEN_API_URL=

docker build -t reviewly-backend .
docker run -p 5000:5000 --env-file .env reviewly-backend