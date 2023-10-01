echo "Switching to branch main"
git checkout main

echo "Deploying files to to server..."
scp -r dist/* shakib@146.190.160.22:/var/www/flask_server/

echo "Deployed successfully!"
