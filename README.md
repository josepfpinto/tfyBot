<!-- PROJECT LOGO -->
<br />
<div align="center">

<h3 align="center">Think For Yourself Bot</h3>

  <p align="center">
    Coming soon...
    <br />
    <br />
    <a href="mailto:josepfpinto@gmail.com">Report Bug</a>

[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
    <br />
    <br />
    <br />
  </p>
</div>


<!-- ABOUT THE PROJECT -->
## About The Project
Coming soon...
<br />
<br />

### Built With

An whatsapp bot created with typescript and LangChain. The infrastructure in AWS. During development the code is deployed directly from GitHub.

* [![Typescript][Typescript.js]][Typescript-url]
* [![AWS][AWS.js]][AWS-url]
* [![Github][Github.js]][Github-url]
* [![Langchain][Langchain.js]][Langchain-url]
* [![OpenAi][OpenAi.js]][OpenAi-url]
<br />
<br />

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.md` for more information.
<br />
<br />

<!-- CONTACT -->
## Contact

Email - <a href="mailto:josepfpinto@gmail.com">josepfpinto@gmail.com</a>

José Pedro Pinto - [@linkedIn](https://www.linkedin.com/in/josepfpinto/)

Project Link: [https://github.com/josepfpinto/tfyBot](https://github.com/josepfpinto/tfyBot)
<br />
<br />


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/josepfpinto/drinkee_website/blob/main/LICENSE.md
[linkedin-shield]: https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white
[linkedin-url]: https://www.linkedin.com/in/josepfpinto/
[product-screenshot]: images/screenshot.png
[Typescript.js]: https://img.shields.io/badge/typescript-20232A?style=for-the-badge&logo=typescript&logoColor=%23F7DF1E
[Typescript-url]: https://www.typescriptlang.org/
[AWS.js]: https://img.shields.io/badge/aws_cloud-20232A?style=for-the-badge&logo=amazon&logoColor=23000000
[AWS-url]: https://aws.amazon.com/
[Github.js]: https://img.shields.io/badge/Github-20232A?style=for-the-badge&logo=github&logoColor=fff
[Github-url]: github.com/
[Langchain.js]: https://img.shields.io/badge/Langchain-20232A?style=for-the-badge&logo=langshain&logoColor=fff
[Langchain-url]: https://www.langchain.com/
[OpenAi.js]: https://img.shields.io/badge/OpenAi-412991?style=for-the-badge&logo=openai&logoColor=fff
[OpenAi-url]: https://www.openai.com/


# Serverless Framework Python Flask API service backed by DynamoDB on AWS

This template demonstrates how to develop and deploy a simple Python Flask API service, backed by DynamoDB, running on AWS Lambda using the traditional Serverless Framework.


## Anatomy of the template

This template configures a single function, `api`, which is responsible for handling all incoming requests thanks to configured `httpApi` events. To learn more about `httpApi` event configuration options, please refer to [httpApi event docs](https://www.serverless.com/framework/docs/providers/aws/events/http-api/). As the events are configured in a way to accept all incoming requests, `Flask` framework is responsible for routing and handling requests internally. The implementation takes advantage of `serverless-wsgi`, which allows you to wrap WSGI applications such as Flask apps. To learn more about `serverless-wsgi`, please refer to corresponding [GitHub repository](https://github.com/logandk/serverless-wsgi). The template also relies on `serverless-python-requirements` plugin for packaging dependencies from `requirements.txt` file. For more details about `serverless-python-requirements` configuration, please refer to corresponding [GitHub repository](https://github.com/UnitedIncome/serverless-python-requirements).

Additionally, the template also handles provisioning of a DynamoDB database that is used for storing data about users. The Flask application exposes two endpoints, `POST /users` and `GET /user/{userId}`, which allow to create and retrieve users.

## Usage

### Prerequisites

In order to package your dependencies locally with `serverless-python-requirements`, you need to have `Python3.9` installed locally. You can create and activate a dedicated virtual environment with the following command:

```bash
python3.9 -m venv ./venv
source ./venv/bin/activate
```

Alternatively, you can also use `dockerizePip` configuration from `serverless-python-requirements`. For details on that, please refer to corresponding [GitHub repository](https://github.com/UnitedIncome/serverless-python-requirements).

### Deployment

This example is made to work with the Serverless Framework dashboard, which includes advanced features such as CI/CD, monitoring, metrics, etc.

In order to deploy with dashboard, you need to first login with:

```
serverless login
```

install dependencies with:

```
npm install
```

and then perform deployment with:

```
serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying aws-python-flask-dynamodb-api-project to stage dev (us-east-1)

✔ Service deployed to stack aws-python-flask-dynamodb-api-project-dev (182s)

endpoint: ANY - https://xxxxxxxx.execute-api.us-east-1.amazonaws.com
functions:
  api: aws-python-flask-dynamodb-api-project-dev-api (1.5 MB)
```

_Note_: In current form, after deployment, your API is public and can be invoked by anyone. For production deployments, you might want to configure an authorizer. For details on how to do that, refer to [httpApi event docs](https://www.serverless.com/framework/docs/providers/aws/events/http-api/).

### Invocation

After successful deployment, you can create a new user by calling the corresponding endpoint:

```bash
curl --request POST 'https://xxxxxx.execute-api.us-east-1.amazonaws.com/users' --header 'Content-Type: application/json' --data-raw '{"name": "John", "userId": "someUserId"}'
```

Which should result in the following response:

```bash
{"userId":"someUserId","name":"John"}
```

You can later retrieve the user by `userId` by calling the following endpoint:

```bash
curl https://xxxxxxx.execute-api.us-east-1.amazonaws.com/users/someUserId
```

Which should result in the following response:

```bash
{"userId":"someUserId","name":"John"}
```

If you try to retrieve user that does not exist, you should receive the following response:

```bash
{"error":"Could not find user with provided \"userId\""}
```

### Local development

Thanks to capabilities of `serverless-wsgi`, it is also possible to run your application locally, however, in order to do that, you will need to first install `werkzeug`, `boto3` dependencies, as well as all other dependencies listed in `requirements.txt`. It is recommended to use a dedicated virtual environment for that purpose. You can install all needed dependencies with the following commands:

```bash
pip install werkzeug boto3
pip install -r requirements.txt
```

Additionally, you will need to emulate DynamoDB locally, which can be done by using `serverless-dynamodb-local` plugin. In order to do that, execute the following commands:

```bash
serverless plugin install -n serverless-dynamodb-local
serverless dynamodb install
```

It will add the plugin to `devDependencies` in `package.json` file as well as to `plugins` section in `serverless.yml`. Additionally, it will also install DynamoDB locally.

You should also add the following config to `custom` section in `serverless.yml`:


```yml
custom:
  (...)
  dynamodb:
    start:
      migrate: true
    stages:
      - dev
```

Additionally, we need to reconfigure DynamoDB Client to connect to our local instance of DynamoDB. We can take advantage of `IS_OFFLINE` environment variable set by `serverless-wsgi` plugin and replace:


```python
dynamodb_client = boto3.client('dynamodb')
```

with

```python
dynamodb_client = boto3.client('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')
```

Now you can start DynamoDB local with the following command:

```bash
serverless dynamodb start
```

At this point, you can run your application locally with the following command:

```bash
serverless wsgi serve
```

For additional local development capabilities of `serverless-wsgi` and `serverless-dynamodb-local` plugins, please refer to corresponding GitHub repositories:
- https://github.com/logandk/serverless-wsgi
- https://github.com/99x/serverless-dynamodb-local
