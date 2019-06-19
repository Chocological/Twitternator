# Twitternator
A one-stop Telegram bot that fulfills your Twittering needs all through the convenience of Telegram!

Let's get you started through rolling out your first Telegram Twitter bot.

1. Go the this link and apply for a Twitter developer account: https://developer.twitter.com/en/apply-for-access

2. After you successfully create your account, head over to this link to create a Twitter app: https://developer.twitter.com/en/apps/create

3. After creating your Twitter app, head over back to the main page and you should see your app with the App ID shown beside the name of your app.

4. Go to this link: https://developer.twitter.com/en/apps/(insert app ID from previous step)

5. Go to the Keys and Tokens tab to preview your current consumer API keys. Note down the consumer API key and API secret key as you will need
   it later to authenticate your Telegram bot.
   
6. Generate a set of fresh access token and access token secret just right below the consumer API section. Similar to the consumer keys, note
   down your access token and access token secret.
   
7. Fork this repository into your local repository. I am using Pycharm IDE to run main.py python script, but you can use your own Python IDE as long as it comes with its own terminal with which you run the script.

8. Run these commands in your Python IDE terminal to install the required packages: 
   8.1. pip install python-telegram-bot==12.0.0b1 --upgrade
   8.2. pip install twython
   8.3. pip install pandas

9. Once you open main.py using your desired (in my case, Pycharm) Python IDE. NOTE: There are four global variables whose values that you      need to edit.
   9.1. CONSUMER_KEY - Replace "CONSUMER_KEY" string with the consumer key saved earlier

10. Go to Telegram and search for "Botfather". Create a new Telegram bot for Twitter with your desired name for the bot.

11. You will be given an access token for your Telegram bot. Note it down as you will need it for the main.py script.

12. In line 26 of main.py, fill in your access token from the previous step. Remember to keep your access token safe!

13. run the script with the command: python main.py

14. Search for the name of your created bot on Telegram. You can start talking to it by typing /start

15. Enjoy using the bot!

Enjoy what this bot does? Tip me a coffee treat :)

Bitcoin address: 1Nn6Vg2qLCxn87bgkytefrmMxpaAZ3WqRF
Ethereum address: 0x854E0CdF408f7A7A6ca6f6731f0b0F02125F8f63
Bitcoin Cash address: qrhwru36gm5gsnmp5cqwr6rhnyflmgda9q9q3uq0ra
Stellar address: GD346LX7BGGO7H6XTQ6U3QLRJDTLD6T4W7R7YPD2IUNUN26VD4CT3Y2M
