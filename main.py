from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from twython import Twython, TwythonError
import pandas as pd

# Current limitations of bot: Can only be used by 1 telegram user at any one time, and main.py script need to be re-run
# for every failed login attempt by user

CONSUMER_KEY = "CONSUMER_KEY"
CONSUMER_SECRET = "CONSUMER_SECRET"
ACCESS_TOKEN = "ACCESS_TOKEN"
ACCESS_SECRET = "ACCESS_SECRET"

twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET)
auth = twitter.get_authentication_tokens()
OAUTH_TOKEN = auth['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

# Instance list containing authenticated Twython instances
twython_instance_list = []

twitter_tweets = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
twitter_profiles = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
twitter_get_user_timelines = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

updater = Updater(token='Your Telegram bot access token', use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Welcome to Twitternator! Type /help for a list of "
                                                                  "available commands.")


def help_commands(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Authorization commands: /login, /login_with_pin (pin code). "
                                                                  "Search commands (no authorization needed): "
                                                                  "/search_tweets (keywords), /search_profiles (keywords), "
                                                                  "/get_users_liked_tweets (specify user here), "
                                                                  "/get_user_timeline (insert username)."
                                                                  "User account commands (authorization needed): "
                                                                  "/update_status (insert status), /get_mentions, "
                                                                  "/my_tweets_retweeted.")


def login(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Welcome to Twitternator! Please authorize your"
                                                                  "Twitter account for authentication purposes through"
                                                                  "the link below")
    context.bot.send_message(chat_id=update.message.chat_id, text=auth['auth_url'])
    context.bot.send_message(chat_id=update.message.chat_id, text="Please type /login_with_pin (pin code here)")


def login_with_pin(update, context):
    user_query = update.message.text
    user_query_list = user_query.split()
    oauth_verifier = user_query_list[1:]
    twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    try:
        final_step = twitter.get_authorized_tokens(oauth_verifier)
        final_oauth_token = final_step['oauth_token']
        final_oauth_token_secret = final_step['oauth_token_secret']
        twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, final_oauth_token, final_oauth_token_secret)
        twython_instance_list.append(twitter)
        if twitter.verify_credentials():
            context.bot.send_message(chat_id=update.message.chat_id, text="You have successfully authenticated "
                                                                          "Twitternator!")
    except TwythonError:
        context.bot.send_message(chat_id=update.message.chat_id, text="Unable to authenticate user. Please try /login "
                                                                      "again")


def unknown(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def update_status(update, context):
    twitter_instance = twython_instance_list[0]
    user_query = update.message.text
    user_query_list = user_query.split()
    split_user_query = user_query_list[1:]
    twitter_instance.update_status(status=split_user_query)


def get_users_liked_tweets(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Below shows most recent 5 tweets liked by a "
                                                                  "specified user. If user not specified, shows most "
                                                                  "recent 5 tweets liked by the authenticating user")
    try:
        twitter_instance = twython_instance_list[0]
    # If user did not authenticate
    except IndexError:
        context.bot.send_message(chat_id=update.message.chat_id, text="Error! You must first authenticate before "
                                                                      "using this feature. /login")
        pass

    # If user is specified, get tweets liked by specified user
    try:
        profile_query = update.message.text
        profile_query_list = profile_query.split()
        profile_query_joined = ''
        for i in profile_query_list[1:]:
            profile_query_joined = i + ' ' + profile_query_joined
        profile_query_joined_fixed = profile_query_joined[: -1]
        query = {'q': profile_query_joined_fixed}
        dict_ = {'screen_name': [], 'followers_count': []}
        for status in twitter_profiles.search_users(**query):
            dict_['screen_name'].append(status['name'])
            dict_['followers_count'].append(status['followers_count'])
        df = pd.DataFrame(dict_)
        df.sort_values(by='followers_count', inplace=True, ascending=False)
        df.head(5)
        liked_tweets_list = twitter_instance.get_favorites(screen_name=list(df['screen_name'].head(1))[0], count=5)
        for i in range(0, 5):
            context.bot.send_message(chat_id=update.message.chat_id, text=list(liked_tweets_list)[i]["text"])
    # If user not specified, get tweets liked by authenticating user
    except TwythonError:
        liked_tweets_list = twitter_instance.get_favorites(count=5)
        for i in range(0, 5):
            context.bot.send_message(chat_id=update.message.chat_id, text=list(liked_tweets_list)[i]["text"])


def search_tweets(update, context):
    user_query = update.message.text
    user_query_list = user_query.split()
    user_query_joined = ''
    for i in user_query_list[1:]:
        user_query_joined = i + ' ' + user_query_joined
    user_query_joined_fixed = user_query_joined[: -1]
    query = {'q': user_query_joined_fixed,
             'result_type': 'popular',
             'count': 10,  # max 10 tweets
             'lang': 'en',
             }
    # Search tweets
    dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
    for status in twitter_tweets.search(**query)['statuses']:
        dict_['user'].append(status['user']['screen_name'])
        dict_['date'].append(status['created_at'])
        dict_['text'].append(status['text'])
        dict_['favorite_count'].append(status['favorite_count'])

    # Structure data in a pandas DataFrame for easier manipulation
    df = pd.DataFrame(dict_)
    df.sort_values(by='favorite_count', inplace=True, ascending=False)
    df.head(5)
    print(df)
    context.bot.send_message(chat_id=update.message.chat_id, text=list(df['text'].head(1))[0])


def search_profiles(update, context):
    profile_query = update.message.text
    profile_query_list = profile_query.split()
    profile_query_joined = ''
    for i in profile_query_list[1:]:
        profile_query_joined = i + ' ' + profile_query_joined
    profile_query_joined_fixed = profile_query_joined[: -1]
    query = {'q': profile_query_joined_fixed}
    # Search profiles
    dict_ = {'screen_name': [], 'id': [], 'location': [], 'url': [], 'description': [], 'followers_count': [], 'created_at': []}
    for status in twitter_profiles.search_users(**query):
        dict_['screen_name'].append(status['name'])
        dict_['id'].append(status['id'])
        dict_['location'].append(status['location'])
        dict_['url'].append(status['url'])
        dict_['description'].append(status['description'])
        dict_['created_at'].append(status['created_at'])
        dict_['followers_count'].append(status['followers_count'])

    # Structure data in a pandas DataFrame for easier manipulation
    df = pd.DataFrame(dict_)
    df.sort_values(by='followers_count', inplace=True, ascending=False)
    df.head(5)
    context.bot.send_message(chat_id=update.message.chat_id, text="user: " + list(df['screen_name'].head(1))[0])
    context.bot.send_message(chat_id=update.message.chat_id, text="user id: " + list(df['id'].head(1))[0])
    context.bot.send_message(chat_id=update.message.chat_id, text="location: " + list(df['location'].head(1))[0])
    context.bot.send_message(chat_id=update.message.chat_id, text="link: " + list(df['url'].head(1))[0])
    context.bot.send_message(chat_id=update.message.chat_id, text="user description: " + list(df['description'].head(1))[0])
    context.bot.send_message(chat_id=update.message.chat_id, text="profile created at: " + list(df['created_at'].head(1))[0])
    context.bot.send_message(chat_id=update.message.chat_id, text="follower count: " +
                                                                  str(list(df['followers_count'].head(1))[0]))


def get_my_retweeted_tweets(update, context):
    try:
        twitter_instance = twython_instance_list[0]
    # If user did not authenticate
    except IndexError:
        context.bot.send_message(chat_id=update.message.chat_id, text="Error! You must first authenticate before "
                                                                      "using this feature. /login")
        pass
    get_retweeted_list = twitter_instance.retweeted_of_me(count=5)
    for i in range(0, 5):
        context.bot.send_message(chat_id=update.message.chat_id, text=list(get_retweeted_list)[i]['text'])
        context.bot.send_message(chat_id=update.message.chat_id, text="user who retweeted this tweet: " +
                                                                      list(get_retweeted_list)[i]['entities']['user_mentions']['screen_name'])


def get_mentions(update, context):
    try:
        twitter_instance = twython_instance_list[0]
    # If user did not authenticate
    except IndexError:
        context.bot.send_message(chat_id=update.message.chat_id, text="Error! You must first authenticate before "
                                                                      "using this feature. /login")
        pass
    get_mentions_list = twitter_instance.get_mentions_timeline(count=5)
    for i in range(0, 5):
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="user: " + list(get_mentions_list)[i]['user']['screen_name'])
        context.bot.send_message(chat_id=update.message.chat_id, text=list(get_mentions_list)[i]["text"])


def get_user_timeline(update, context):
    profile_query = update.message.text
    profile_query_list = profile_query.split()
    profile_query_joined = ''
    for i in profile_query_list[1:]:
        profile_query_joined = i + ' ' + profile_query_joined
    profile_query_joined_fixed = profile_query_joined[: -1]
    get_user_timeline_list = twitter_get_user_timelines.get_user_timeline(screen_name=profile_query_joined_fixed,
                                                                          count=5)
    for i in range(0, 5):
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="user: " + list(get_user_timeline_list)[i]['user']['screen_name'])
        context.bot.send_message(chat_id=update.message.chat_id, text=list(get_user_timeline_list)[i]["text"])


def main():
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    help_handler = CommandHandler('help', help_commands)
    dispatcher.add_handler(help_handler)
    login_handler = CommandHandler('login', login)
    dispatcher.add_handler(login_handler)
    login_with_pin_handler = CommandHandler('login_with_pin', login_with_pin)
    dispatcher.add_handler(login_with_pin_handler)
    search_tweets_handler = CommandHandler('search', search_tweets)
    dispatcher.add_handler(search_tweets_handler)
    liked_tweets_handler = CommandHandler('liked_tweets', get_users_liked_tweets)
    dispatcher.add_handler(liked_tweets_handler)
    search_profiles_handler = CommandHandler('search_profiles', search_profiles)
    dispatcher.add_handler(search_profiles_handler)
    update_status_handler = CommandHandler('update_status', update_status)
    dispatcher.add_handler(update_status_handler)
    get_mentions_handler = CommandHandler('get_mentions', get_mentions)
    dispatcher.add_handler(get_mentions_handler)
    my_tweets_retweeted_handler = CommandHandler('my_tweets_retweeted', get_my_retweeted_tweets)
    dispatcher.add_handler(my_tweets_retweeted_handler)
    get_user_timeline_handler = CommandHandler('get_user_timeline', get_user_timeline)
    dispatcher.add_handler(get_user_timeline_handler)
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()