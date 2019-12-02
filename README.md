# Setup for KaggleLocalLB

* Python Packages

  * pandas
  * selenium
  * jsonlib
  * requests
  * imgkit
  * Jinja2

* Web Browser - Firefox

* Gecko Driver Installation (Web Driver b/w firefox and Selenium)

  * Download the latest release from https://github.com/mozilla/geckodriver/releases
  * Extraction : `tar xvzf geckodriver*`
  * Executable : `chmod +x geckodriver`
  * Move it to bin : `sudo mv geckodriver /usr/local/bin`


# Creating Slack app | Installation | Permissions and Obtaining token

* Visit : https://api.slack.com/apps
* Click on **Create app** button and enter name and select the workspace
* After successful creation you'll be directed to Settings Page > Click on **Permissions**
* Scroll down to **Scopes** > click on **Select Permission Scopes** drop down > Scroll to **Files** > Select **Upload and modify as a user**
* Click **Save Changes** button
* Scroll up and click **Install App to Workspace** > Click **Authorize**
* Upon Successful Authorisation and Installation you'll be redirected to same but now OAuth Access Token will be displayed copy it and use it in your script 
