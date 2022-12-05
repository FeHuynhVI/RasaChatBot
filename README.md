# Covid botchat rasa

## Requirement:
- pip install rasa==3.0
- pip install git+https://github.com/RasaHQ/rasa-nlu-examples
- pip install underthesea
- pip install transformers
- pip install wikipedia
----------------------------------------------------------------------------------------------------
## Setting:
- Open file: 

    ```custom\vi_tokenize.py``` change path url to stopwords file 'PATH_STOP_WORD'

- Copy 3 file from directory 'custom' overwrite to rasa directory of you:
    ### Examples:
        C:\Users\Admin\anaconda3\Lib\site-packages\rasa\nlu\utils\hugging_face\registry.py
        C:\Users\Admin\anaconda3\Lib\site-packages\rasa\engine\recipes\default_components.py
        C:\Users\Admin\anaconda3\Lib\site-packages\rasa\nlu\tokenizers\vi_tokenize.py

- You can also copy the file contents slack-custom.py overwrite file slack.py in rasa directory
----------------------------------------------------------------------------------------------------
## Train:
- CMD: 
    ```rasa train```
## Run:
- OPEN 2 CMD (Command line)
- CMD 1: 
    ```rasa run actions```
- CMD 2: 
    ```rasa run shell```
----------------------------------------------------------------------------------------------------
## Connect bot to slack:
- [Connect bot with rasa](https://rasa.com/docs/rasa/connectors/slack/)
- You also need install ngrok [Download ngrok](https://ngrok.com/) or ```pip install pyngrok```
- Run 
    ```ngrok http 5002```
- Change config in file: credentials.yml
- Run in local
    ```rasa run --port 5002 --connector slack --credentials credentials.yml --cors * --enable-api --debug```
    
    ```rasa run actions```
