# We want to scrape web pages.
# Each page wil have a different request method and will need different
# regex expressions to parse the data.

# The requests and regex won't change often.
# It can be stored in a seperate text file for each site, or in the
# site's class file.

# Updating will be difficult. Some sites the data will be gotten by date. So you# can check to see if the date is already on hard drive.
# That might not always be the case.

# We need to be able to import a module and do an update command
# which will check to see if the data we need is already stored in the cache.
# If it isn't, it will go to a site and get the data and store it.
