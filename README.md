# arrrXiv

To update:

git add <updates>
git commit -m "<commit message>"
git push
git push heroku master
heroku ps:scale worker=1
heroku restart worker.1

To check:

heroku ps
heroku logs

If not working:
- Make sure "local" variable set to false, "tweet_now" to true
- Make sure requirements are up-to-date
