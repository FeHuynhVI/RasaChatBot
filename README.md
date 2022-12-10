# Covid botchat rasa

## Requirement:
- pip install rasa==3.0
- pip install git+https://github.com/RasaHQ/rasa-nlu-examples
- pip install underthesea
- pip install transformers
- pip install wikipedia

```shell
conda create -n py308 python=3.8 
conda install -y --file requirements.conda.txt
pip install -r requirements.txt
```

----------------------------------------------------------------------------------------------------
## Setting:
- Open file: `custom\vi_tokenize.py` change path url to stopwords file 'PATH_STOP_WORD'

- Copy 3 file from directory 'custom' overwrite to rasa directory of you:
    ### Examples:
        C:\Users\Admin\anaconda3\Lib\site-packages\rasa\nlu\utils\hugging_face\registry.py
        C:\Users\Admin\anaconda3\Lib\site-packages\rasa\engine\recipes\default_components.py
        C:\Users\Admin\anaconda3\Lib\site-packages\rasa\nlu\tokenizers\vi_tokenize.py

- You can also copy the file contents slack-custom.py overwrite file slack.py in rasa directory
----------------------------------------------------------------------------------------------------
## Train:
 
```shell
rasa train
```

## Run:
 
```shell
rasa run actions
```
 
```shell
rasa run shell
```

----------------------------------------------------------------------------------------------------
## Connect bot to slack:
- [Connect bot with rasa](https://rasa.com/docs/rasa/connectors/slack/)
- You also need install ngrok [Download ngrok](https://ngrok.com/) or 
```shell
pip install pyngrok
```

- Run simple to testing by cli: 

```shell
ngrok http 5002
```

- Change config in file: credentials.yml
- Run in local

```shell
rasa run --port 5002 --connector slack --credentials credentials.yml --cors * --enable-api --debug
```
    
```shell
rasa run actions
```