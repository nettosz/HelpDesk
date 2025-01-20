

echo "killing old docker processes"
docker-compose rm -fs helpdesk

echo "building docker containers"
docker-compose up --build -d helpdesk

