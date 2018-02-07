# Slack Member List

To get a list of Slack members, send a GET request:

```sh
curl "https://kywjux5aw5.execute-api.us-east-1.amazonaws.com/prod/proxy"
```

The response is a JSON list which looks like this:

```python
[
    {
        "name": "User Name",
        "title": "Comp Sci Student",     # Can be null
        "image_24": "https://..."        # Can be null
        "image_32": "https://..."        # Can be null
        "image_48": "https://..."        # Can be null
        "image_72": "https://..."        # Can be null
        "image_192": "https://..."       # Can be null
        "image_512": "https://..."       # Can be null
        "image_1024": "https://..."      # Can be null
        "image_original": "https://..."  # Can be null
    },
    # ...
]
```
