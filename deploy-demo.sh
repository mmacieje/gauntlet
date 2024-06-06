cd /home/ec2-user/gauntlet/
docker-compose -f production.yml down
git pull && docker-compose -f production.yml build
docker-compose -f production.yml up -d
