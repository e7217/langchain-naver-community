## Installation
To install `langchain-naver-community`, simply run the following command:
```python
pip install -U langchain-naver-community
```
### Setting Up Credentials
Setting Up Credentials
To use Naver's APIs, you need to set up your API credentials. You can obtain a **Naver API Key** by signing up at the [Naver Developers](https://developers.naver.com/main/) website and creating an application.

Once you have your **Client ID** and **Client Secret**, you can set them as environment variables in your script as follows:
```
import getpass
import os

# Set your Naver API credentials as environment variables
if not os.environ.get("NAVER_CLIENT_ID"):
    os.environ["NAVER_CLIENT_ID"] = getpass.getpass("Enter your Naver Client ID:\n")

if not os.environ.get("NAVER_CLIENT_SECRET"):
    os.environ["NAVER_CLIENT_SECRET"] = getpass.getpass("Enter your Naver Client Secret:\n")

```
This ensures that your credentials are securely stored without being hardcoded into your scripts. 🔒